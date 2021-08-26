import {Injectable} from '@angular/core';
import {CanActivate, Router} from '@angular/router';

import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {ConfigSetupService} from '../services/moblab-configuration-alerting.service';
import {NotificationsService} from '../services/notifications.service';
import {environment} from 'environments/environment';

@Injectable()
export class ConfigGuard implements CanActivate {
  constructor(
    private router: Router,
    private moblabRpcService: MoblabGrpcService,
    private configSetupService: ConfigSetupService,
    private notificationsService: NotificationsService
  ) {}

  canActivate(): Promise<boolean> {
    if (environment.disableConfigGuard) {
      this.configSetupService.setIsCloudConfigEnabled(true);
      return Promise.resolve(true);
    }

    return new Promise((resolve, _) => {
      this.moblabRpcService.get_cloud_configuration(
        (
          boto_key_id: string,
          boto_key_secret: string,
          gcs_bucket_url: string,
          is_cloud_enabled: boolean,
          is_remote_console_enabled: boolean,
          is_remote_command_enabled: boolean
        ) => {
          if (!this.configSetupService.getIsCloudConfigEnabled()) {
            this.router.navigate(['/config']);
            resolve(false);
          } else {
            resolve(true);
          }
        },
        (errorMsg: string) => {
          this.notificationsService.error(
            'Failed to get cloud configuration: ' + errorMsg
          );
        }
      );
    });
  }
}
