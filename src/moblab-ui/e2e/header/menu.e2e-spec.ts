// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {browser, element, by, ExpectedConditions as until} from 'protractor';

describe('Clicking the hamburger button', () => {
  const menu = element(by.tagName('mat-sidenav')),
    menuButton = element(by.className('menu-button'));

  beforeAll(() => {
    browser.waitForAngularEnabled(false);
    browser.get('/');
    browser.wait(until.visibilityOf(menu), 5000);
    menuButton.click();
  });

  it('hides the menu, as TC No.262', () => {
    expect(browser.wait(until.invisibilityOf(menu), 3000)).toBeTruthy();
  });

  describe('at the second time', () => {
    it('shows the menu, as TC No.263', () => {
      menuButton.click();
      expect(browser.wait(until.visibilityOf(menu), 3000)).toBeTruthy();
    });
  });
});