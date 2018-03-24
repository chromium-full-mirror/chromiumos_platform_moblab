# MobmonitorUi

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 1.7.3.

## Installing nodejs

You will need nodejs locally to build and run the app. The easiest way to get
nodejs is nvm.

Install [nvm](https://github.com/creationix/nvm#install-script)
```
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.8/install.sh | bash
```

Install node
```
nvm i v6.11.5
```

Install angular cli
```
npm i -g @angular/cli
```

Install local node modules
```
npm i
```

Note: if you are running tests outside of the chroot, you need to install node
there as well.

## Development server

Run `ng serve --proxy-config proxy.conf.json` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files. You may need to update `proxy.conf.json` to point to Mobmonitor's backend.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `-prod` flag for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).
These tests need to be run outside of chroot, so that they can access a chrome
binary.

## Running end-to-end tests

Run `e2e/run_e2e.sh` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).
These tests need to be run outside of chroot, so that they can access a chrome
binary.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
