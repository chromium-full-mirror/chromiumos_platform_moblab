import os
from os.path import expanduser
import sys

from google.api_core import page_iterator
from google.cloud import storage

"""
This is a standalone script used to get the number of custom builds 
that have been uploaded to the moblab buckets. This analysis helps with 
figuring out who are the active users of the Custom OS Image feature. 
This script is expected to be run outside the Moblab dev environment
in the local setup. 
This script is expected to be run by members of moblab team who
have full access to the GCP account. 
Download the account login json from the GCP and put it in ~/.gsutil/moblab_login
 
"""
# download the service_account json from the GCP web portal
# Set environment variable
path_where_key_is_stored = expanduser(
    "~/.gsutil/moblab_login/chromeos-partner-moblab-account-login.json"
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path_where_key_is_stored


def _item_to_value(iterator, item):
    return item


def list_directories(gcs, bucket_name, prefix):
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    extra_params = {"projection": "noAcl", "prefix": prefix, "delimiter": "/"}
    path = "/b/" + bucket_name + "/o"
    iterator = page_iterator.HTTPIterator(
        client=gcs,
        api_request=gcs._connection.api_request,
        path=path,
        items_key="prefixes",
        item_to_value=_item_to_value,
        extra_params=extra_params,
    )
    return [x for x in iterator]


def main(argv):
    client = storage.Client()
    # get the list of buckets under the account
    buckets = client.list_buckets()
    bucket_names = [x.name for x in buckets]
    bucket_level_info = {}

    # for each bucket, figure out the number of custom_builds
    for bucket_name in bucket_names:
        folders = list_directories(client, bucket_name, "")
        num_builds_per_partner = 0
        for folder in folders:
            if "-local" in folder:
                # figure out the list of custom OS builds uploaded in this folder
                blobs = client.list_blobs(
                    bucket_name, prefix=folder, delimiter=""
                )
                # always expect something after the first "/" because of the above query
                build_folders = [blob.name.split("/")[1] for blob in blobs]
                # Example of build_folder:
                # chromeos-moblab-peng-staging/eve-local/R102-14679.0.0-d2022_04_11_1033
                # make build_folder names unique
                uniq_builds = set(build_folders)
                # remove dummy results in the result
                if "" in uniq_builds:
                    uniq_builds.remove("")
                num_builds_per_partner += len(uniq_builds)
        if num_builds_per_partner:
            print(
                f"{bucket_name} bucket has {num_builds_per_partner} custom builds"
            )
            bucket_level_info[bucket_name] = num_builds_per_partner
    print(bucket_level_info)


if __name__ == "__main__":
    main(sys.argv[1:])
