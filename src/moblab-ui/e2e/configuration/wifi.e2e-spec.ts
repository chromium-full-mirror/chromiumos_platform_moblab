// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {browser, ExpectedConditions as until} from 'protractor';
import {ConfigurationPage} from './configuration.po';

describe('The "DUT Wi-Fi Configuration" card', () => {
  const page = new ConfigurationPage(),
    card = page.card('dut-wifi-card');

  beforeAll(() => {
    browser.waitForAngularEnabled(false);
    page.navigateTo();
    card.scrollTo();
  });

  it('has a disabled submit button by default, as TC No.12', () => {
    expect(card.submitButton().isEnabled()).toBeFalsy();
  });

  describe('with updated information', () => {
    // Use a time suffix to make sure it always updates the new information
    const wifiName = 'fake_name_' + new Date().getTime();

    beforeAll(() => {
      card.replaceInput('dut-wifi-name-input', wifiName);
      card.replaceInput('dut-wifi-password-input', 'fake_password');
    });

    it('has its submit button clickable', () => {
      expect(card.submitButton().isEnabled()).toBeTruthy();
    });

    it('shows loading animation when the submit button is clicked', () => {
      card.submitButton().click();
      expect(card.isLoading()).toBeTruthy();
      expect(browser.wait(until.not(card.isLoading()), 10000)).toBeTruthy();
    });

    describe('submitted', () => {
      // TODO verify if the DUTs are connected to the AP

      it('should show updated data', () => {
        page.navigateTo();
        card.scrollTo();
        expect(card.valueOf('dut-wifi-name-input')).toMatch(wifiName);
      });
    });
  });
});