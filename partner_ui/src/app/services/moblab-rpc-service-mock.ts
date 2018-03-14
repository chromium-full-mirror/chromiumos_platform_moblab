import {Injectable} from "@angular/core";
import {Observable} from "rxjs";

@Injectable()
export class MoblabRpcServiceMock {

  private createMockObservable(data): Observable<any> {
    return Observable.from([data]).flatMap(
        value => Observable.timer(1),
        value => value
    );
  }

  getBoards(): Observable<string> {
    return this.createMockObservable(["cyan", "veyron_minnie"]);
  }

  getBuilds(board: string): Observable<string> {
    return this.createMockObservable(["build1", "build2"]);
  }

  getFirmwareBuilds(board: string): Observable<string> {
    return this.createMockObservable(["firmware1", "firmware2"]);
  }

  getPools(): Observable<string> {
    return this.createMockObservable(["pool1", "pool2"]);
  }

  getVersionInformation(): Observable<string> {
    return this.createMockObservable({
      "CHROMEOS_RELEASE_TRACK": "dev-channel\n",
      "GOOGLE_RELEASE": "9000.76.0\n",
      "CHROMEOS_DEVSERVER": "\n",
      "CHROMEOS_RELEASE_BUILDER_PATH": "guado_moblab-release/R56-9000.76.0\n",
      "CHROMEOS_RELEASE_BUILD_NUMBER": "9000\n",
      "CHROMEOS_CANARY_APPID": "{90F229CE-83E2-4FAF-8479-E368A34938B1}\n",
      "CHROMEOS_RELEASE_CHROME_MILESTONE": "56\n",
      "CHROMEOS_RELEASE_BRANCH_NUMBER": "76\n",
      "CHROMEOS_RELEASE_PATCH_NUMBER": "0\n",
      "CHROMEOS_RELEASE_APPID": "{BCC6E30A-D921-18E8-73D3-60177AD4AF86}\n",
      "DEVICETYPE": "CHROMEBOX\n",
      "CHROMEOS_RELEASE_DESCRIPTION": "9000.76.0 (Official Build) dev-channel guado_moblab test\n",
      "CHROMEOS_BOARD_APPID": "{BCC6E30A-D921-18E8-73D3-60177AD4AF86}\n",
      "CHROMEOS_RELEASE_BUILD_TYPE": "Official Build\n",
      "CHROMEOS_RELEASE_NAME": "Chrome OS\n",
      "CHROMEOS_RELEASE_BOARD": "guado_moblab\n",
      "CHROMEOS_RELEASE_VERSION": "9000.76.0\n",
      "CHROMEOS_AUSERVER": "https://tools.google.com/service/update2\n",
      "MOBLAB_ID": "cd965c3e-0518-11e7-a6ee-2c600c8dcc7b\n",
      "MOBLAB_MAC_ADDRESS": "2c:60:0c:8d:cc:7b\n"
    });
  }

  getNetworkInformation(): Observable<Map<string, string>> {
    return this.createMockObservable({"server_ips": ["100.96.49.226"], "is_connected": true});
  }

  getCloudStorageInformation(): Observable<Map<string, string>> {
    return this.createMockObservable({
      "image_storage_server": "gs://chromeos-moblab-haddowktest/",
      "use_existing_boto_file": true,
      "gs_secret_access_key": "oW+3v+uUhjNIbHc5fQ//LJqH+mmvamup/SbWmy63",
      "gs_access_key_id": "GOOGVRWGSJTCJWIPVMSB"
    });
  }

  getConfigSettings(): Observable<Map<string, Array<Array<string>>>> {
    return this.createMockObservable(
        {
          "PACKAGES": [["custom_max_age", "1"], ["minimum_free_space", "1"], ["serve_packages_from_autoserv", "True"]],
          "UPDATE_COMMANDS": [["afe", "AUTOTEST_REPO/utils/compile_gwt_clients.py -c autotest.AfeClient"], ["apache", "sudo service apache2 reload"], ["build_externals", "AUTOTEST_REPO/utils/build_externals.py"], ["migrate", "AUTOTEST_REPO/database/migrate.py sync"], ["test_importer", "AUTOTEST_REPO/utils/test_importer.py"], ["tko", "AUTOTEST_REPO/utils/compile_gwt_clients.py -c autotest.TkoClient"]],
          "AUTOTEST_WEB": [["host", "localhost"], ["database", "chromeos_autotest_db"], ["db_type", "mysql"], ["user", "chromeosqa-admin"], ["password", "moblab_db_passwd"], ["job_timeout_default", "24"], ["job_timeout_mins_default", "1440"], ["job_max_runtime_mins_default", "1440"], ["parse_failed_repair_default", "0"], ["readonly_host", "localhost"], ["readonly_user", "chromeosqa-admin"], ["readonly_password", "moblab_db_passwd"], ["query_timeout", "3600"], ["min_retry_delay", "20"], ["max_retry_delay", "60"], ["graph_cache_creation_timeout_minutes", "10"], ["parameterized_jobs", "False"], ["template_debug_mode", "True"], ["sql_debug_mode", "False"], ["restricted_groups", "USE SHADOW RESTRICTED_GROUPS"], ["global_db_host", ""], ["global_db_database", ""], ["global_db_type", ""], ["global_db_user", ""], ["global_db_password", ""], ["global_db_query_timeout", ""], ["global_db_min_retry_delay", ""], ["global_db_max_retry_delay", ""], ["afe_root_url", "http://cautotest.corp.google.com/afe/"], ["wmatrix_url", "/wmatrix"]],
          "HOSTS": [["wait_up_processes", ""], ["default_protection", "NO_PROTECTION"], ["default_reboot_timeout", "240"], ["wait_down_reboot_timeout", "120"], ["wait_down_reboot_warning", "30"], ["hours_to_wait_for_recovery", "0.01"]],
          "BUG_REPORTING": [["gs_domain", "https://storage.cloud.google.com/"], ["chromeos_image_archive", "chromeos-image-archive/"], ["arg_prefix", "?arg="], ["retrieve_logs_cgi", "http://cautotest.corp.google.com/tko/retrieve_logs.cgi?job=/"], ["generic_results_bin", "results/"], ["debug_dir", "debug/"], ["buildbot_builders", "http://chromegw.corp.google.com/i/chromeos/builders/"], ["build_prefix", "build/"], ["job_view", "http://%s/afe/#tab_id=view_job&object_id=%s"], ["crbug_url", "https://code.google.com/p/chromium/issues/detail?id=%s"], ["gs_file_prefix", "gs://"], ["chromium_email_address", "@chromium.org"], ["credentials", "USE SHADOW CREDENTIALS"], ["monorail_server", ""], ["client_id", "USE SHADOW CLIENT_ID"], ["client_secret", "USE SHADOW CLIENT_SECRET"], ["scope", "USE SHADOW SCOPE"], ["wmatrix_retry_url", "https://wmatrix.googleplex.com/retry_teststats/?days_back=30&tests=%s"], ["wmatrix_test_history_url", "https://wmatrix.googleplex.com/unfiltered?hide_missing=True&tests=%s"], ["pool_health_cc", "chromeos-infra-eng@grotations.appspotmail.com"], ["pool_health_labels", "recoverduts,Pri-1"], ["pool_health_components", "Infra>Client>ChromeOS"]],
          "SSP": [["user", ""]],
          "SHARD": [["shard_hostname", ""], ["heartbeat_pause_sec", "60"]],
          "POOL_INSTANCE_SHARDING": [],
          "CLIENT": [["drop_caches", "False"], ["drop_caches_between_iterations", "False"], ["output_dir", ""], ["dns_zone", "cros.corp.google.com"], ["http_proxy", ""], ["https_proxy", ""], ["metadata_index", ""]],
          "CROS": [["stable_cros_version", "R55-8872.67.0"], ["stable_build_pattern", "%s-release/%s"], ["source_tree", "/usr/local/google/chromeos"], ["gs_offloading_enabled", "True"], ["image_storage_server", "gs://chromeos-moblab-haddowktest/"], ["results_storage_server", ""], ["cts_results_server", ""], ["cts_apfe_server", "gs://chromeos-cts-apfe/"], ["dev_server_hosts", "chromeos-devserver1, chromeos-devserver2, chromeos-devserver3, chromeos-devserver4, chromeos-devserver5, chromeos-devserver6, chromeos-devserver7, chromeos-crash1, chromeos2-devserver6, chromeos2-devserver7, chromeos2-devserver5"], ["dev_server", "http://192.168.231.1:8080"], ["canary_channel_server", "gs://chromeos-releases/canary-channel/"], ["crash_server", "http://172.17.40.24:8082, http://100.107.160.6:8082, http://100.107.160.5:8082"], ["sharding_factor", "1"], ["infrastructure_user", "chromeos-test"], ["gs_offloader_use_rsync", "False"], ["gs_offloader_multiprocessing", "False"], ["cloud_notification_enabled", "True"], ["cloud_notification_topic", "projects/chromeos-partner-moblab/topics/moblab-notification-staging"], ["android_build_name_pattern", "%\\(branch\\)s/%\\(target\\)s/%\\(build_id\\)s"], ["firmware_url_pattern", "%s/static/%s/firmware_from_source.tar.bz2"], ["factory_image_url_pattern", "%s/static/canary-channel/%s/factory_test/chromiumos_factory_image.bin"], ["factory_artifact", "factory_image"], ["image_url_pattern", "%s/update/%s"], ["log_url_pattern", "http://%s/tko/retrieve_logs.cgi?job=/results/%s/"], ["package_url_pattern", "%s/static/%s/autotest/packages"], ["servo_board", "beaglebone_servo"], ["released_ro_builds_auron_paine", "auron_paine-firmware/R39-6301.58.6"], ["released_ro_builds_auron_yuna", "auron_yuna-firmware/R39-6301.59.5"], ["released_ro_builds_banjo", "banjo-firmware/R34-5216.334.4"], ["released_ro_builds_buddy", "buddy-firmware/R39-6301.202.5"], ["released_ro_builds_candy", "candy-firmware/R34-5216.310.1"], ["released_ro_builds_celes", "celes-firmware/R46-7287.92.3"], ["released_ro_builds_cyan", "cyan-firmware/R46-7287.57.32,cyan-firmware/R46-7287.57.25"], ["released_ro_builds_gandof", "gandof-firmware/R39-6301.155.9"], ["released_ro_builds_gnawty", "gnawty-firmware/R34-5216.239.34,gnawty-firmware/R34-5216.239.16"], ["released_ro_builds_guado", "guado-firmware/R39-6301.108.4"], ["released_ro_builds_heli", "heli-firmware/R34-5216.392.4"], ["released_ro_builds_lulu", "lulu-firmware/R39-6301.136.39,lulu-firmware/R39-6301.136.16"], ["released_ro_builds_mccloud", "mccloud-firmware/R36-5827.14.0"], ["released_ro_builds_ninja", "ninja-firmware/R34-5216.383.7"], ["released_ro_builds_orco", "orco-firmware/R34-5216.362.7"], ["released_ro_builds_panther", "panther-firmware/R32-4920.24.26"], ["released_ro_builds_rikku", "rikku-firmware/R39-6301.110.4"], ["released_ro_builds_samus", "samus-firmware/R39-6300.102.0,samus-firmware/R39-6300.90.0"], ["released_ro_builds_squawks", "squawks-firmware/R34-5216.152.22,squawks-firmware/R34-5216.152.21,squawks-firmware/R34-5216.152.17"], ["released_ro_builds_tricky", "tricky-firmware/R36-5829.12.0"], ["released_ro_builds_veyron_jaq", "veyron_jaq-firmware/R41-6588.160.0,veyron_jaq-firmware/R41-6588.92.0,veyron_jaq-firmware/R41-6588.44.0"], ["released_ro_builds_veyron_jerry", "veyron_jerry-firmware/R41-6588.160.0,veyron_jerry-firmware/R41-6588.92.0,veyron_jerry-firmware/R41-6588.40.0"], ["released_ro_builds_veyron_mickey", "veyron_mickey-firmware/R41-6588.168.0,veyron_mickey-firmware/R41-6588.159.0"], ["released_ro_builds_veyron_mighty", "veyron_mighty-firmware/R41-6588.160.0,veyron_mighty-firmware/R41-6588.97.0,veyron_mighty-firmware/R41-6588.51.0"], ["released_ro_builds_veyron_minnie", "veyron_minnie-firmware/R41-6588.160.0,veyron_minnie-firmware/R41-6588.92.0"], ["released_ro_builds_veyron_speedy", "veyron_speedy-firmware/R41-6588.160.0,veyron_speedy-firmware/R41-6588.92.0,veyron_speedy-firmware/R41-6588.55.0"], ["released_ro_builds_wolf", "wolf-firmware/R30-4389.24.62,wolf-firmware/R30-4389.24.58,wolf-firmware/R30-4389.24.39"], ["rpm_sentry_username", "fake_user"], ["rpm_sentry_password", "fake_password"], ["rpm_frontend_uri", "http://chromeos-rpmserver2.cbf.corp.google.com:9999"], ["rpm_recovery_boards", "stumpy,kiev"], ["lab_status_url", "http://chromiumos-lab.appspot.com/current?format=json"], ["statsd_server", "146.148.70.158"], ["statsd_port", "8125"], ["sam_instances", "cautotest"], ["test_instance", "chromeos-autotest.cbf"], ["extra_servers", "chromeos-mcp"], ["es_host", "172.25.65.90"], ["es_port", "9200"], ["es_udp_port", "9700"], ["es_use_http", "False"], ["skip_devserver_health_check", "True"], ["swarming_proxy", ""], ["gs_offloader_limit_file_count", "False"], ["pools_support_firmware_repair", "faft-test,faft-test-tot,faft-test-experiment"], ["restricted_subnets", ""], ["enable_drone_in_restricted_subnet", "False"], ["prefer_local_devserver", "False"], ["enable_ssh_tunnel_for_servo", "False"], ["enable_ssh_tunnel_for_chameleon", "False"], ["enable_ssh_connection_for_devserver", "False"], ["enable_ssh_tunnel_for_moblab", "False"], ["enable_getting_controls_in_batch", "False"], ["enable_devserver_trigger_auto_update", "False"], ["hwid_key", "no_hwid_labels"], ["devserver_dir", "/usr/lib/devserver/"]],
          "AUTOSERV": [["client_autodir_paths", "/usr/local/autotest,/usr/local/autodir"], ["measure_run_time_tests", "desktopui_ScreenLocker,login_LoginSuccess,security_ProfilePermissions"], ["incremental_tko_parsing", "False"], ["testing_mode", "False"], ["container_path", "/usr/local/autotest/containers"], ["container_base", "http://storage.googleapis.com/chromeos-image-archive/autotest-containers/base.tar.xz"], ["container_base_folder_url", "http://storage.googleapis.com/abci-ssp/autotest-containers"], ["container_base_name", "base_02"], ["enable_ssp_container", "True"], ["min_version_support_ssp", "6919"], ["min_launch_control_build_id_support_ssp", "2675445"], ["auto_start_servod", "True"], ["support_builds_arg_in_suite_job", "True"], ["ssh_engine", "raw_ssh"], ["enable_master_ssh", "True"], ["require_atfork_module", "False"], ["use_sshagent_with_paramiko", "True"], ["enable_server_prebuild", "False"]],
          "SCHEDULER": [["die_on_orphans", "False"], ["enable_scheduler", "True"], ["notify_email", "chromeos-test-cron+cautotest@google.com"], ["notify_email_errors", "USE SHADOW NOTIFY_EMAIL_ERRORS"], ["notify_email_from", "chromeos-autotest@google.com"], ["notify_email_statuses", "Completed,Failed,Aborted"], ["max_processes_per_drone", "1000"], ["max_processes_warning_threshold", "0.8"], ["max_parse_processes", "100"], ["max_transfer_processes", "50"], ["tick_pause_sec", "5"], ["minimum_tick_sec", "5"], ["clean_interval_minutes", "5"], ["drones", "localhost"], ["drone_installation_directory", "/usr/local/autotest"], ["results_host", "localhost"], ["results_host_installation_directory", ""], ["secs_to_wait_for_atomic_group_hosts", "600"], ["pidfile_timeout_mins", "300"], ["max_pidfile_refreshes", "2000"], ["gc_stats_interval_mins", "360"], ["reverify_period_minutes", "30"], ["reverify_max_hosts_at_once", "30"], ["drone_sets_enabled", "False"], ["default_drone_set_name", ""], ["enable_archiving", "False"], ["copy_task_results_back", "False"], ["copy_parse_log_back", "False"], ["tick_debug", "True"], ["extra_debugging", "False"], ["max_repair_limit", "2"], ["max_provision_retries", "0"], ["drone_build_externals", "False"], ["inline_host_acquisition", "USE SHADOW INLINE_HOST_ACQUISITION"], ["threaded_drone_manager", "True"]],
          "NOTIFICATIONS": [["chromium_build_url", "http://build.chromium.org/p/chromiumos/"], ["sheriffs", "USE SHADOW SHERIFFS"], ["lab_sheriffs", "USE SHADOW SHERIFFS"], ["gmail_api_credentials", ""], ["gmail_api_credentials_test_failure", ""]],
          "AUTOTEST_SERVER_DB": [["database", "chromeos_lab_servers"]],
          "ANDROID": [["image_url_pattern", "%s/static/%s"], ["stable_version_dragonboard", "git_mnc-brillo-dev/dragonboard-userdebug/2512766"], ["stable_version_edison", "git_nyc-jaqen-dev/jaqen_edison-userdebug/2979181"], ["package_url_pattern", "%s/static/%s"]],
          "SERVER": [["hostname", "localhost"], ["rpc_logging", "False"], ["rpc_log_path", "/usr/local/autotest/logs/rpcserver.log"], ["rpc_num_old_logs", "5"], ["rpc_max_log_size_mb", "20"], ["rpc_logserver", "False"], ["gb_diskspace_required", "0.7"], ["kilo_inodes_required", "100"], ["kilo_inodes_required_veyron_rialto", "55"], ["kilo_inodes_required_arkham", "50"], ["kilo_inodes_required_storm", "50"], ["kilo_inodes_required_whirlwind", "50"], ["gb_encrypted_diskspace_required", "0.1"], ["smtp_server", ""], ["smtp_port", ""], ["smtp_user", ""], ["smtp_password", ""], ["crash_collection_hours_to_wait", "0.001"], ["use_server_db", "False"], ["suite_scheduler_afe", ""], ["global_afe_hostname", "cautotest"], ["creds_dir", ""], ["use_prod_sponge_server", "False"]],
          "ACTS": [["acts_config_folder", ""]]
        }
    );
  }


  runSuite(board: string, build: string, suite: string, pool: string, rw_firmware: string,
           ro_firmware: string) {
    console.log("run_suite", {
      "board": board, "build": build, "suite": suite,
      "pool": pool, "rw_firmware": rw_firmware, "ro_firmware": ro_firmware
    });
    return this.createMockObservable(null);
  }
}
