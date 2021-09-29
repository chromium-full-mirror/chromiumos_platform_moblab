// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {browser, by, element} from 'protractor';
import {DUT, ManageDutsPage} from './manage-duts.po';

describe('Selecting an unenrolled DUT', () => {
  const page = new ManageDutsPage(),
    unenrolled_dut = page.getUnenrolled(),
    enrollButton = element(by.buttonText('Enroll Selected')),
    unenrollButton = element(by.buttonText('Unenroll Selected')),
    reverifyButton = element(by.buttonText('Reverify Selected'));

  beforeAll(() => {
    browser.waitForAngularEnabled(false);
    page.navigateTo();
    browser.wait(page.isLoaded);
  });

  it('enables the buttons "Enroll", "Unenroll" and "Reverify", as TC No.23', () => {
    unenrolled_dut.toggleSelection();
    expect(enrollButton.isEnabled()).toBeTruthy();
    expect(unenrollButton.isEnabled()).toBeTruthy();
    expect(reverifyButton.isEnabled()).toBeTruthy();
  });

  describe('then clicking on "Enroll Selected"', () => {
    let dut: DUT;

    beforeAll(async () => {
      dut = page.getByAddr(await unenrolled_dut.macAddr());
      enrollButton.click();
      browser.wait(page.isLoaded);
    });

    it('changes the DUT\'s to "Ready"', async () => {
      expect(await dut.status()).toBe('Ready');
    });

    it("shows the DUT's build target, model and labels information", async () => {
      expect(await dut.buildTarget()).not.toBe('');
      expect(await dut.model()).not.toBe('');
      expect(await dut.labels()).not.toEqual([]);
    });

    describe('then clicking on "Unenroll Selected"', () => {
      beforeAll(() => {
        dut.toggleSelection();
        unenrollButton.click();
        browser.wait(page.isLoaded);
      });

      it('changes the DUT\'s status to "Not Enrolled", as TC No.24', async () => {
        expect(await dut.status()).toBe('Not Enrolled');
      });

      it("removes the DUT's build target, model and labels", async () => {
        expect(await dut.buildTarget()).toBe('');
        expect(await dut.model()).toBe('');
        expect(await dut.labels()).toEqual([]);
      });
    });
  });
});
