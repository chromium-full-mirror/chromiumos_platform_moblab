import {Injectable} from '@angular/core';
import {Observable, of, Subject, BehaviorSubject} from 'rxjs';

@Injectable()
export class ConfigSetupService {

    private isCloudConfigShownOnBoot: boolean = false;
    private isCloudConfigEnabled: boolean = false;
    private observableSubject$ = new BehaviorSubject(this.isCloudConfigEnabled);
    public cloudConfigObservable: Observable<boolean> = this.observableSubject$.asObservable();

    constructor() { }

    setIsCloudConfigAsShown(): void {
        /**
         * Get if configuration component has been shown on boot up.
        */
        this.isCloudConfigShownOnBoot = true;
    }

    getIsCloudConfigShownOnBoot(): boolean {
        /**
         * Set configuration page as been shown on boot up.
        */
        return this.isCloudConfigShownOnBoot;
    }

    setIsCloudConfigEnabled(isCloudConfigEnabled: boolean): void {
        /**
         * Set 'enabled' status of cloud configuration.
        */
        this.isCloudConfigEnabled = isCloudConfigEnabled;
        this.observableSubject$.next(this.isCloudConfigEnabled);
    }

    getIsCloudConfigEnabled(): boolean {
        /**
         * Get if cloud configuration has been enabled.
        */
        return this.isCloudConfigEnabled;
    }

}

