// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {browser, by, element, ExpectedConditions as until} from 'protractor';
import {ConfigurationPage} from './configuration.po';

describe('The "Test Runner Configuration" card', () => {
  const page = new ConfigurationPage(),
    card = page.card('test-runner'),
    status = card.element(by.id('test-runner-config')),
    pauseButton = card.element(by.buttonText('Pause'));

  beforeAll(() => {
    browser.waitForAngularEnabled(false);
    page.navigateTo();
    card.scrollTo();
  });

  it('shows "Active" by default, as TC No.9', () => {
    expect(status.getText()).toMatch(/status:( |\n)+Active/);
  });

  it('has a button whose label is "Pause"', () => {
    expect(pauseButton.isDisplayed()).toBeTruthy();
  });

  describe('with the "Pause" button clicked', () => {
    const resumeButton = card.element(by.buttonText('Resume')),
      warning = element(by.className('mat-toolbar-warn'));

    beforeAll(() => {
      pauseButton.click();
      browser.wait(until.invisibilityOf(pauseButton));
    });

    it('changes its status to "Paused"', () => {
      expect(status.getText()).toMatch(/status:( |\n)+Paused/);
    });

    it('changes the button text to "Resume"', () => {
      expect(resumeButton.isDisplayed()).toBeTruthy();
    });

    it('should show a warning banner on top of the page', () => {
      expect(warning.isDisplayed()).toBeTruthy();
      expect(warning.getText()).toMatch(/^Job Scheduler is paused due to/);
    });

    it('should show a warning banner even the page is reloaded, as TC No.323', () => {
      browser.refresh();
      expect(browser.wait(until.visibilityOf(warning))).toBeTruthy();
    });

    describe('then clicking on "Resume"', () => {
      beforeAll(() => {
        card.scrollTo();
        resumeButton.click();
        browser.wait(until.invisibilityOf(resumeButton));
      });

      it('changes its status back to "Active", as TC No.147', () => {
        expect(status.getText()).toMatch('Active');
      });

      it('changes the button text back to "Pause"', () => {
        expect(pauseButton.isDisplayed()).toBeTruthy();
      });

      it('should hide the warning banner', () => {
        expect(warning.isPresent()).toBeFalsy();
      });
    });
  });
});