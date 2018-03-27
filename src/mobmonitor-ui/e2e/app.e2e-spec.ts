import { browser } from 'protractor';
import { AppPage } from './app.po';

describe('mobmonitor-ui App', () => {
  let page: AppPage;

  beforeEach(() => {
    // need to add this otherwise protractor test fails
    // timing out waiting for the infinite 1 second interval
    // to complete
    browser.waitForAngularEnabled(false);
    page = new AppPage();
  });

  it('should display welcome message', () => {
    page.navigateTo();
    expect(page.getTitleText()).toEqual('Mobmonitor');
  });

  it('should show health checks', () => {
    page.navigateTo();
    expect(page.getHealthCheckTitle()).toEqual('healthyService');

    expect(page.getHealthCheckStatus('healthy')).toEqual('healthy');
    expect(page.getHealthCheckStatus('warning')).toEqual('healthy with warnings');
    expect(page.getHealthCheckStatus('unhealthy')).toEqual('not healthy');
  });

  it('should run actions', () => {
    page.navigateTo();
    const actionButton = page.getActionButton('action-testAction');
    expect(actionButton.getText()).toEqual('testAction');

    actionButton.click();
    const snackBar = page.getSnackbarButton();
    snackBar.click();
  });

  it('should run actions with params', () => {
    page.navigateTo();
    page.getActionButton('action-testActionWithParams').click();
    page.fillParam('testParam', 'abc123');
    page.submitParamDialogButton().click();
    page.getSnackbarButton().click();
  });

  it('should cancel an action with params', () => {
    page.navigateTo();
    page.getActionButton('action-testActionWithParams').click();
    page.cancelParamDialogButton().click();
  });

  it('should disable param dialog submit until form filled out', () => {
    page.navigateTo();
    page.getActionButton('action-testActionWithParams').click();
    expect(page.submitParamDialogButton().isEnabled()).toBe(false);
    page.fillParam('testParam', 'abc123');
    expect(page.submitParamDialogButton().isEnabled()).toBe(true);
  });

  it('should download logs', () => {
    page.navigateTo();
    page.downloadLogsButton().click();
  });
});
