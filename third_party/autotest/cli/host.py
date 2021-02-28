# Copyright 2008 Google Inc. All Rights Reserved.

"""
The host module contains the objects and method used to
manage a host in Autotest.

The valid actions are:
create:  adds host(s)
delete:  deletes host(s)
list:    lists host(s)
stat:    displays host(s) information
mod:     modifies host(s)
jobs:    lists all jobs that ran on host(s)

The common options are:
-M|--mlist:   file containing a list of machines


See topic_common.py for a High Level Design and Algorithm.

"""



import common
import json
import random
import re
import socket
import sys
import time

from cli import action_common, rpc, topic_common
from client.bin import utils as bin_utils
from client.common_lib import error, host_protections
from server import server_frontend, hosts
from server.hosts import host_info



MIGRATED_HOST_SUFFIX = '-migrated-do-not-use'


ID_AUTOGEN_MESSAGE = ("[IGNORED]. Do not edit (crbug.com/950553). ID is "
                      "auto-generated.")



class host(topic_common.atest):
    """Host class
    atest host [create|delete|list|stat|mod|jobs|rename|migrate|statjson] <options>"""
    usage_action = '[create|delete|list|stat|mod|jobs|rename|migrate|statjson]'
    topic = msg_topic = 'host'
    msg_items = '<hosts>'

    protections = host_protections.Protection.names


    def __init__(self):
        """Add to the parser the options common to all the
        host actions"""
        super(host, self).__init__()

        self.parser.add_option('-M', '--mlist',
                               help='File listing the machines',
                               type='string',
                               default=None,
                               metavar='MACHINE_FLIST')

        self.topic_parse_info = topic_common.item_parse_info(
            attribute_name='hosts',
            filename_option='mlist',
            use_leftover=True)


    def _parse_lock_options(self, options):
        if options.lock and options.unlock:
            self.invalid_syntax('Only specify one of '
                                '--lock and --unlock.')

        self.lock = options.lock
        self.unlock = options.unlock
        self.lock_reason = options.lock_reason

        if options.lock:
            self.data['locked'] = True
            self.messages.append('Locked host')
        elif options.unlock:
            self.data['locked'] = False
            self.data['lock_reason'] = ''
            self.messages.append('Unlocked host')

        if options.lock and options.lock_reason:
            self.data['lock_reason'] = options.lock_reason


    def _cleanup_labels(self, labels, platform=None):
        """Removes the platform label from the overall labels"""
        if platform:
            return [label for label in labels
                    if label != platform]
        else:
            try:
                return [label for label in labels
                        if not label['platform']]
            except TypeError:
                # This is a hack - the server will soon
                # do this, so all this code should be removed.
                return labels


    def get_items(self):
        return self.hosts


class host_help(host):
    """Just here to get the atest logic working.
    Usage is set by its parent"""
    pass


class host_list(action_common.atest_list, host):
    """atest host list [--mlist <file>|<hosts>] [--label <label>]
       [--status <status1,status2>] [--acl <ACL>] [--user <user>]"""

    def __init__(self):
        super(host_list, self).__init__()

        self.parser.add_option('-b', '--label',
                               default='',
                               help='Only list hosts with all these labels '
                               '(comma separated).')
        self.parser.add_option('-s', '--status',
                               default='',
                               help='Only list hosts with any of these '
                               'statuses (comma separated)')
        self.parser.add_option('-a', '--acl',
                               default='',
                               help=('Only list hosts within this ACL.'))
        self.parser.add_option('-u', '--user',
                               default='',
                               help=('Only list hosts available to this user. '))
        self.parser.add_option('-N', '--hostnames-only', help='Only return '
                               'hostnames for the machines queried.',
                               action='store_true')
        self.parser.add_option('--locked',
                               default=False,
                               help='Only list locked hosts',
                               action='store_true')
        self.parser.add_option('--unlocked',
                               default=False,
                               help='Only list unlocked hosts',
                               action='store_true')



    def parse(self):
        """Consume the specific options"""
        label_info = topic_common.item_parse_info(attribute_name='labels',
                                                  inline_option='label')

        (options, leftover) = super(host_list, self).parse([label_info])

        self.status = options.status
        self.acl = options.acl
        self.user = options.user
        self.hostnames_only = options.hostnames_only

        if options.locked and options.unlocked:
            self.invalid_syntax('--locked and --unlocked are '
                                'mutually exclusive')

        self.locked = options.locked
        self.unlocked = options.unlocked
        self.label_map = None

        return (options, leftover)


    def execute(self):
        """Execute 'atest host list'."""

        filters = {}
        check_results = {}
        if self.hosts:
            filters['hostname__in'] = self.hosts
            check_results['hostname__in'] = 'hostname'

        if self.labels:
            if len(self.labels) == 1:
                # This is needed for labels with wildcards (x86*)
                filters['labels__name__in'] = self.labels
                check_results['labels__name__in'] = None
            else:
                filters['multiple_labels'] = self.labels
                check_results['multiple_labels'] = None

        if self.status:
            statuses = self.status.split(',')
            statuses = [status.strip() for status in statuses
                        if status.strip()]

            filters['status__in'] = statuses
            check_results['status__in'] = None

        if self.locked or self.unlocked:
            filters['locked'] = self.locked
            check_results['locked'] = None

        return super(host_list, self).execute(op='get_hosts',
                                              filters=filters,
                                              check_results=check_results)


    def output(self, results):
        """Print output of 'atest host list'.

        @param results: the results to be printed.
        """
        if results:
            # Remove the platform from the labels.
            for result in results:
                result['labels'] = self._cleanup_labels(result['labels'],
                                                        result['platform'])
        if self.hostnames_only:
            self.print_list(results, key='hostname')
        else:
            keys = ['hostname', 'status', 'shard', 'locked', 'lock_reason',
                    'locked_by', 'platform', 'labels']
            super(host_list, self).output(results, keys=keys)

class host_stat(host):
    """atest host stat --mlist <file>|<hosts>"""
    usage_action = 'stat'

    def execute(self):
        """Execute 'atest host stat'."""
        results = []
        # Convert wildcards into real host stats.
        existing_hosts = []
        for host in self.hosts:
            if host.endswith('*'):
                stats = self.execute_rpc('get_hosts',
                                         hostname__startswith=host.rstrip('*'))
                if len(stats) == 0:
                    self.failure('No hosts matching %s' % host, item=host,
                                 what_failed='Failed to stat')
                    continue
            else:
                stats = self.execute_rpc('get_hosts', hostname=host)
                if len(stats) == 0:
                    self.failure('Unknown host %s' % host, item=host,
                                 what_failed='Failed to stat')
                    continue
            existing_hosts.extend(stats)

        for stat in existing_hosts:
            host = stat['hostname']
            # The host exists, these should succeed
            acls = self.execute_rpc('get_acl_groups', hosts__hostname=host)

            labels = self.execute_rpc('get_labels', host__hostname=host)
            results.append([[stat], acls, labels, stat['attributes']])
        return results


    def output(self, results):
        """Print output of 'atest host stat'.

        @param results: the results to be printed.
        """
        for stats, acls, labels, attributes in results:
            print('-'*5)
            self.print_fields(stats,
                              keys=['hostname', 'id', 'platform',
                                    'status', 'locked', 'locked_by',
                                    'lock_time', 'lock_reason', 'protection',])
            self.print_by_ids(acls, 'ACLs', line_before=True)
            labels = self._cleanup_labels(labels)
            self.print_by_ids(labels, 'Labels', line_before=True)
            self.print_dict(attributes, 'Host Attributes', line_before=True)


class host_get_migration_plan(host_stat):
    """atest host get_migration_plan --mlist <file>|<hosts>"""
    usage_action = "get_migration_plan"

    def __init__(self):
        super(host_get_migration_plan, self).__init__()
        self.parser.add_option("--ratio", default=0.5, type=float, dest="ratio")

    def parse(self):
        (options, leftover) = super(host_get_migration_plan, self).parse()
        self.ratio = options.ratio
        return (options, leftover)

    def execute(self):
        afe = server_frontend.AFE()
        results = super(host_get_migration_plan, self).execute()
        working = []
        non_working = []
        for stats, _, _, _ in results:
            assert len(stats) == 1
            stats = stats[0]
            hostname = stats["hostname"]
            now = time.time()
            history = HostJobHistory.get_host_history(
                afe=afe,
                hostname=hostname,
                start_time=now,
                end_time=now - 24 * 60 * 60,
            )
            dut_status, _ = history.last_diagnosis()
            if dut_status in [UNUSED, WORKING]:
                working.append(hostname)
            elif dut_status == BROKEN:
                non_working.append(hostname)
            elif dut_status == UNKNOWN:
                # if it's unknown, randomly assign it to working or
                # nonworking, since we don't know.
                # The two choices aren't actually equiprobable, but it
                # should be fine.
                random.choice([working, non_working]).append(hostname)
            else:
                raise ValueError("unknown status %s" % dut_status)
        working_transfer, working_retain = fair_partition.partition(working, self.ratio)
        non_working_transfer, non_working_retain = \
            fair_partition.partition(non_working, self.ratio)
        return {
            "transfer": working_transfer + non_working_transfer,
            "retain": working_retain + non_working_retain,
        }

    def output(self, results):
        print(json.dumps(results, indent=4, sort_keys=True))


class host_jobs(host):
    """atest host jobs [--max-query] --mlist <file>|<hosts>"""
    usage_action = 'jobs'

    def __init__(self):
        super(host_jobs, self).__init__()
        self.parser.add_option('-q', '--max-query',
                               help='Limits the number of results '
                               '(20 by default)',
                               type='int', default=20)


    def parse(self):
        """Consume the specific options"""
        (options, leftover) = super(host_jobs, self).parse()
        self.max_queries = options.max_query
        return (options, leftover)


    def execute(self):
        """Execute 'atest host jobs'."""
        results = []
        real_hosts = []
        for host in self.hosts:
            if host.endswith('*'):
                stats = self.execute_rpc('get_hosts',
                                         hostname__startswith=host.rstrip('*'))
                if len(stats) == 0:
                    self.failure('No host matching %s' % host, item=host,
                                 what_failed='Failed to stat')
                [real_hosts.append(stat['hostname']) for stat in stats]
            else:
                real_hosts.append(host)

        for host in real_hosts:
            queue_entries = self.execute_rpc('get_host_queue_entries',
                                             host__hostname=host,
                                             query_limit=self.max_queries,
                                             sort_by=['-job__id'])
            jobs = []
            for entry in queue_entries:
                job = {'job_id': entry['job']['id'],
                       'job_owner': entry['job']['owner'],
                       'job_name': entry['job']['name'],
                       'status': entry['status']}
                jobs.append(job)
            results.append((host, jobs))
        return results


    def output(self, results):
        """Print output of 'atest host jobs'.

        @param results: the results to be printed.
        """
        for host, jobs in results:
            print('-'*5)
            print('Hostname: %s' % host)
            self.print_table(jobs, keys_header=['job_id',
                                                'job_owner',
                                                'job_name',
                                                'status'])

class BaseHostModCreate(host):
    """The base class for host_mod and host_create"""
    # Matches one attribute=value pair
    attribute_regex = r'(?P<attribute>\w+)=(?P<value>.+)?'

    def __init__(self):
        """Add the options shared between host mod and host create actions."""
        self.messages = []
        self.host_ids = {}
        super(BaseHostModCreate, self).__init__()
        self.parser.add_option('-l', '--lock',
                               help='Lock hosts.',
                               action='store_true')
        self.parser.add_option('-r', '--lock_reason',
                               help='Reason for locking hosts.',
                               default='')
        self.parser.add_option('-u', '--unlock',
                               help='Unlock hosts.',
                               action='store_true')

        self.parser.add_option('-p', '--protection', type='choice',
                               help=('Set the protection level on a host.  '
                                     'Must be one of: %s.' %
                                     (', '.join('"%s"' % p
                                               for p in self.protections))),
                               choices=self.protections)
        self._attributes = []
        self.parser.add_option('--attribute', '-i',
                               help=('Host attribute to add or change. Format '
                                     'is <attribute>=<value>. Multiple '
                                     'attributes can be set by passing the '
                                     'argument multiple times. Attributes can '
                                     'be unset by providing an empty value.'),
                               action='append')
        self.parser.add_option('-b', '--labels',
                               help=('Comma separated list of labels. '))
        self.parser.add_option('-B', '--blist',
                               help='File listing the labels',
                               type='string',
                               metavar='LABEL_FLIST')
        self.parser.add_option('-a', '--acls',
                               help=('Comma separated list of ACLs.'))
        self.parser.add_option('-A', '--alist',
                               help=('File listing the acls. %s'),
                               type='string',
                               metavar='ACL_FLIST')
        self.parser.add_option('-t', '--platform',
                               help=('Sets the platform label.'))


    def parse(self):
        """Consume the options common to host create and host mod.
        """
        label_info = topic_common.item_parse_info(attribute_name='labels',
                                                 inline_option='labels',
                                                 filename_option='blist')
        acl_info = topic_common.item_parse_info(attribute_name='acls',
                                                inline_option='acls',
                                                filename_option='alist')

        (options, leftover) = super(BaseHostModCreate, self).parse([label_info,
                                                              acl_info],
                                                             req_items='hosts')

        self._parse_lock_options(options)

        self.label_map = None

        if self.labels:
            self.label_map = device.convert_to_label_map(self.labels)

        if options.protection:
            self.data['protection'] = options.protection
            self.messages.append('Protection set to "%s"' % options.protection)

        self.attributes = {}
        if options.attribute:
            for pair in options.attribute:
                m = re.match(self.attribute_regex, pair)
                if not m:
                    raise topic_common.CliError('Attribute must be in key=value '
                                                'syntax.')
                elif m.group('attribute') in self.attributes:
                    raise topic_common.CliError(
                            'Multiple values provided for attribute '
                            '%s.' % m.group('attribute'))
                self.attributes[m.group('attribute')] = m.group('value')

        self.platform = options.platform
        return (options, leftover)


    def _remove_labels(self, host, condition):
        """Remove all labels from host that meet condition(label).

        @param host: hostname
        @param condition: callable that returns bool when given a label
        """
        if host in self.host_ids:
            host_id = self.host_ids[host]
            labels_to_remove = []
            for l in self.execute_rpc('get_labels', host=host_id):
                if condition(l):
                    labels_to_remove.append(l['id'])
            if labels_to_remove:
                self.execute_rpc('host_remove_labels', id=host_id,
                                 labels=labels_to_remove)


    def _set_labels(self, host, labels):
        """Apply labels to host (and remove all other labels).

        @param host: hostname
        @param labels: list of label names
        """
        condition = lambda l: l['name'] not in labels and not l['platform']
        self._remove_labels(host, condition)
        self.check_and_create_items('get_labels', 'add_label', labels)
        self.execute_rpc('host_add_labels', id=host, labels=labels)


    def _set_platform_label(self, host, platform_label):
        """Apply the platform label to host (and remove existing).

        @param host: hostname
        @param platform_label: platform label's name
        """
        self._remove_labels(host, lambda l: l['platform'])
        self.check_and_create_items('get_labels', 'add_label', [platform_label],
                                    platform=True)
        self.execute_rpc('host_add_labels', id=host, labels=[platform_label])


    def _set_attributes(self, host, attributes):
        """Set attributes on host.

        @param host: hostname
        @param attributes: attribute dictionary
        """
        for attr, value in self.attributes.items():
            self.execute_rpc('set_host_attribute', attribute=attr,
                             value=value, hostname=host)


class host_mod(BaseHostModCreate):
    """atest host mod [--lock|--unlock --force_modify_locking
    --platform <arch>
    --labels <labels>|--blist <label_file>
    --acls <acls>|--alist <acl_file>
    --protection <protection_type>
    --attributes <attr>=<value>;<attr>=<value>
    --mlist <mach_file>] <hosts>"""
    usage_action = 'mod'

    def __init__(self):
        """Add the options specific to the mod action"""
        super(host_mod, self).__init__()
        self.parser.add_option('--unlock-lock-id',
                               help=('Unlock the lock with the lock-id. %s'),
                               default=None)
        self.parser.add_option('-f', '--force_modify_locking',
                               help='Forcefully lock\\unlock a host',
                               action='store_true')
        self.parser.add_option('--remove_acls',
                               help=('Remove all active acls. %s'),
                               action='store_true')
        self.parser.add_option('--remove_labels',
                               help='Remove all labels.',
                               action='store_true')
        self.parser.add_option('--new-env',
                               dest='new_env',
                               choices=['staging', 'prod'],
                               help=('The new environment ("staging" or '
                                     '"prod") of the hosts. %s'),
                               default=None)


    def _parse_unlock_options(self, options):
        """Parse unlock related options."""




        self.unlock_lock_id = options.unlock_lock_id


    def parse(self):
        """Consume the specific options"""
        (options, leftover) = super(host_mod, self).parse()

        self._parse_unlock_options(options)

        if options.force_modify_locking:
             self.data['force_modify_locking'] = True

        self.remove_labels = options.remove_labels
        self.new_env = options.new_env

        return (options, leftover)


    def execute(self):
        """Execute 'atest host mod'."""

        successes = []
        for host in self.execute_rpc('get_hosts', hostname__in=self.hosts):
            self.host_ids[host['hostname']] = host['id']
        for host in self.hosts:
            if host not in self.host_ids:
                self.failure('Cannot modify non-existant host %s.' % host)
                continue
            host_id = self.host_ids[host]

            try:
                if self.data:
                    self.execute_rpc('modify_host', item=host,
                                     id=host, **self.data)

                if self.attributes:
                    self._set_attributes(host, self.attributes)

                if self.labels or self.remove_labels:
                    self._set_labels(host, self.labels)

                if self.platform:
                    self._set_platform_label(host, self.platform)

                # TODO: Make the AFE return True or False,
                # especially for lock
                successes.append(host)
            except topic_common.CliError as full_error:
                # Already logged by execute_rpc()
                pass
        return successes


    def output(self, hosts):
        """Print output of 'atest host mod'.

        @param hosts: the host list to be printed.
        """
        for msg in self.messages:
            self.print_wrapped(msg, hosts)



class HostInfo(object):
    """Store host information so we don't have to keep looking it up."""
    def __init__(self, hostname, platform, labels):
        self.hostname = hostname
        self.platform = platform
        self.labels = labels


class host_create(BaseHostModCreate):
    """atest host create [--lock|--unlock --platform <arch>
    --labels <labels>|--blist <label_file>
    --acls <acls>|--alist <acl_file>
    --protection <protection_type>
    --attributes <attr>=<value>;<attr>=<value>
    --mlist <mach_file>] <hosts>"""
    usage_action = 'create'

    def parse(self):
        """Option logic specific to create action.
        """
        (options, leftovers) = super(host_create, self).parse()
        self.locked = options.lock
        if 'serials' in self.attributes:
            if len(self.hosts) > 1:
                raise topic_common.CliError('Can not specify serials with '
                                            'multiple hosts.')


    @classmethod
    def construct_without_parse(
            cls, web_server, hosts, platform=None,
            locked=False, lock_reason='', labels=[], acls=[],
            protection=host_protections.Protection.NO_PROTECTION):
        """Construct a host_create object and fill in data from args.

        Do not need to call parse after the construction.

        Return an object of site_host_create ready to execute.

        @param web_server: A string specifies the autotest webserver url.
            It is needed to setup comm to make rpc.
        @param hosts: A list of hostnames as strings.
        @param platform: A string or None.
        @param locked: A boolean.
        @param lock_reason: A string.
        @param labels: A list of labels as strings.
        @param acls: A list of acls as strings.
        @param protection: An enum defined in host_protections.
        """
        obj = cls()
        obj.web_server = web_server
        try:
            # Setup stuff needed for afe comm.
            obj.afe = rpc.afe_comm(web_server)
        except rpc.AuthError as s:
            obj.failure(str(s), fatal=True)
        obj.hosts = hosts
        obj.platform = platform
        obj.locked = locked
        if locked and lock_reason.strip():
            obj.data['lock_reason'] = lock_reason.strip()
        obj.labels = labels
        obj.acls = acls
        if protection:
            obj.data['protection'] = protection
        obj.attributes = {}
        return obj


    def _detect_host_info(self, host):
        """Detect platform and labels from the host.

        @param host: hostname

        @return: HostInfo object
        """
        # Mock an afe_host object so that the host is constructed as if the
        # data was already in afe
        data = {'attributes': self.attributes, 'labels': self.labels}
        afe_host = server_frontend.Host(None, data)
        store = host_info.InMemoryHostInfoStore(
                host_info.HostInfo(labels=self.labels,
                                   attributes=self.attributes))
        machine = {
                'hostname': host,
                'afe_host': afe_host,
                'host_info_store': store
        }
        try:
            serials = self.attributes.get('serials', '').split(',')
            adb_serial = self.attributes.get('serials')
            host_dut = hosts.create_host(machine,
                                            adb_serial=adb_serial)

            info = HostInfo(host, host_dut.get_platform(),
                            host_dut.get_labels())
            # Clean host to make sure nothing left after calling it,
            # e.g. tunnels.
            if hasattr(host_dut, 'close'):
                host_dut.close()
        except (socket.gaierror, error.AutoservRunError,
                error.AutoservSSHTimeout):
            # We may be adding a host that does not exist yet or we can't
            # reach due to hostname/address issues or if the host is down.
            info = HostInfo(host, None, [])
        return info


    def _execute_add_one_host(self, host):
        # Always add the hosts as locked to avoid the host
        # being picked up by the scheduler before it's ACL'ed.
        self.data['locked'] = True
        if not self.locked:
            self.data['lock_reason'] = 'Forced lock on device creation'
        self.execute_rpc('add_host', hostname=host, status="Ready", **self.data)

        # If there are labels avaliable for host, use them.
        info = self._detect_host_info(host)
        labels = set(self.labels)
        if info.labels:
            labels.update(info.labels)

        if labels:
            self._set_labels(host, list(labels))

        # Now add the platform label.
        # If a platform was not provided and we were able to retrieve it
        # from the host, use the retrieved platform.
        platform = self.platform if self.platform else info.platform
        if platform:
            self._set_platform_label(host, platform)

        if self.attributes:
            self._set_attributes(host, self.attributes)


    def execute(self):
        """Execute 'atest host create'."""
        successful_hosts = []
        for host in self.hosts:
            try:
                self._execute_add_one_host(host)
                successful_hosts.append(host)
            except topic_common.CliError:
                pass

        if successful_hosts:
            if not self.locked:
                for host in successful_hosts:
                    self.execute_rpc('modify_host', id=host, locked=False,
                                     lock_reason='')
        return successful_hosts


    def output(self, hosts):
        """Print output of 'atest host create'.

        @param hosts: the added host list to be printed.
        """
        self.print_wrapped('Added host', hosts)


class host_delete(action_common.atest_delete, host):
    """atest host delete [--mlist <mach_file>] <hosts>"""

    def __init__(self):
        super(host_delete, self).__init__()

    def execute(self):
        """Execute 'atest host delete'.

        @return A list of hostnames which have been successfully deleted.
        """

        return super(host_delete, self).execute()


class InvalidHostnameError(Exception):
    """Cannot perform actions on the host because of invalid hostname."""


def _add_hostname_suffix(hostname, suffix):
    """Add the suffix to the hostname."""
    if hostname.endswith(suffix):
        raise InvalidHostnameError(
              'Cannot add "%s" as it already contains the suffix.' % suffix)

    return hostname + suffix


def _remove_hostname_suffix_if_present(hostname, suffix):
    """Remove the suffix from the hostname."""
    if hostname.endswith(suffix):
        return hostname[:len(hostname) - len(suffix)]
    else:
        return hostname
