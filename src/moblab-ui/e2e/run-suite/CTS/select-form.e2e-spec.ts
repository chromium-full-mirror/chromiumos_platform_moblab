// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {browser, ExpectedConditions as until} from 'protractor';
import {SelectForm, RunSuitePage} from '../run-suite.po';

describe('Navigate to Moblab run-suite page, as TC No.48', () => {
  const page = new RunSuitePage(),
    form = new SelectForm();

  beforeAll(() => {
    browser.waitForAngularEnabled(false);
    page.navigateTo();
  });

  it('has CTS form selected by default', async () => {
    expect(await page.suiteActive().getText()).toEqual('CTS');
  });

  describe('then select build target, as TC No.49', () => {
    beforeAll(() => {
      browser.wait(until.invisibilityOf(page.loadingMessage()));
      form.modelButton().click();
      form.dropDownMenu(0).click();
      browser.wait(until.invisibilityOf(page.loadingMessage()));
    });

    it('"Please select build target" placeholder should disappear', () => {
      expect(
        until.invisibilityOf(form.placeholderOnSelectMilestone())
      ).toBeTruthy();
    });

    describe('then select milestone, as TC No.50', () => {
      beforeAll(() => {
        form.milestoneButton().click();
        form.dropDownMenu(0).click();
        browser.wait(until.invisibilityOf(page.loadingMessage()));
      });

      it('"Please select milestone" placeholder should disappear', () => {
        expect(
          until.invisibilityOf(form.placeholderOnSelectBuild())
        ).toBeTruthy();
      });

      describe('then select build version, as TC No.51', () => {
        beforeAll(() => {
          form.buildButton().click();
          form.dropDownMenu(0).click();
          browser.wait(until.invisibilityOf(page.loadingMessage()));
        });

        it('"Please select build" placeholder should disappear', () => {
          expect(until.invisibilityOf(form.placeholderOnPool())).toBeTruthy();
        });

        describe('then pick cts from Cts version dropdown options, as TC No.53', () => {
          beforeAll(() => {
            form.selectCTSVersion().click();
            form.dropDownMenu(0).click();
            browser.wait(
              until.invisibilityOf(form.placeholderOnSelectCTSVersion())
            );
          });

          it('has cts populates field', async () => {
            expect(await form.selectCTSVersion().getText()).toEqual('cts');
          });

          describe('then pick cts_hardware from Cts version dropdown options, as TC No.378', () => {
            beforeAll(() => {
              form.selectCTSVersion().click();
              form.dropDownMenu(1).click();
              browser.wait(
                until.invisibilityOf(form.placeholderOnSelectCTSVersion())
              );
            });

            it('has cts_hardware populates field', async () => {
              expect(await form.selectCTSVersion().getText()).toEqual(
                'cts_hardware'
              );
            });

            describe('then input specific CTS Modules, as TC No.54', () => {
              beforeAll(() => {
                form.textModeule().click();
                form.textModeule().sendKeys('arm.CtsEffectTestCases');
              });

              it('has input CTS Modules in the Modules field', () => {
                expect(form.textCloseButton().isPresent()).toBeTruthy();
              });

              it('has Run Suite button clickable', () => {
                expect(form.runSuiteButton().isEnabled()).toBeTruthy();
              });
            });
          });
        });
      });
    });
  });
});
