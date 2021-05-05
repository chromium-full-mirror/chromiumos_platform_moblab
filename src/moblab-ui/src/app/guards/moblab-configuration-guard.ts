import {Injectable} from '@angular/core';
import {CanActivate, Router} from "@angular/router";
import {MatSnackBar} from '@angular/material/snack-bar';

import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {ConfigSetupService} from '../services/moblab-configuration-alerting.service';

@Injectable()
export class ConfigGuard implements CanActivate {

    constructor(
        private router: Router,
        private snackBar: MatSnackBar,
        private moblabRpcService: MoblabGrpcService,
        private configSetupService: ConfigSetupService,
    ) { }

    canActivate(): boolean {
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
                }
            },
            (errorMsg: string) => {
                this.setOffError('Failed to get cloud configuration: ' + errorMsg);
            }
        );
        return true;
    }

    setOffError(dialogue: string) {
        const snackBarRef = this.snackBar.open(dialogue, 'Dismiss', {
            verticalPosition: 'top',
            panelClass: ['snack-error'],
        });
    }

}
