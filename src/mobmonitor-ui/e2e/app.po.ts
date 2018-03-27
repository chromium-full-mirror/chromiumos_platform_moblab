import { browser, by, element, until } from 'protractor';

export class AppPage {
  navigateTo() {
    return browser.get('/');
  }

  getTitleText() {
    return element(by.css('h1')).getText();
  }

  getHealthCheckTitle() {
    const locator = by.css('h2');
    browser.wait(until.elementLocated(locator), 2000);
    return element(locator).getText();
  }

  getHealthCheckStatus(health) {
    const locator = by.css(`.check-health.${health}`);
    browser.wait(until.elementLocated(locator), 2000);
    return element(locator).getText();
  }

  getActionButton(id) {
    const locator = by.id(id);
    browser.wait(until.elementLocated(locator));
    return element(locator);
  }


  getSnackbarButton () {
    const locator = by.css('.mat-simple-snackbar-action');
    browser.wait(until.elementLocated(locator));
    return element(locator);
  }

  fillParam(param, value) {
    const locator = by.id(`param-${param}`);
    browser.wait(until.elementLocated(locator));
    element(locator).sendKeys(value);
  }

  submitParamDialogButton() {
    return element(by.partialButtonText('Run Action'));
  }

  cancelParamDialogButton() {
    return element(by.partialButtonText('Cancel'));
  }

  downloadLogsButton() {
    const locator = by.partialLinkText('Download Logs');
    browser.wait(until.elementLocated(locator));
    return element(locator);
  }
}
