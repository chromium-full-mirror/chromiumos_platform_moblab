// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {browser, by, element} from 'protractor';
export class SelectForm {
  modelButton() {
    return element(by.id('modelSelector'));
  }

  milestoneButton() {
    return element(by.id('milestoneSelector'));
  }

  buildButton() {
    return element(by.id('buildSelector'));
  }

  poolButton() {
    return element(by.id('poolSelector'));
  }

  placeholderOnPool() {
    return element(by.id('mat-hint-1'));
  }

  placeholderOnBuildTarget() {
    return element(by.id('mat-hint-2'));
  }

  placeholderOnSelectMilestone() {
    return element(by.id('mat-hint-3'));
  }

  placeholderOnSelectBuild() {
    return element(by.id('mat-hint-4'));
  }

  /**
   * Returns the selected index from dropdown menu which exclude "grey out/failed" option.
   * @param {number} index - the index of dropdown menu start from "0".
   */
  dropDownMenu(index: number) {
    return element.all(by.css('[role="listbox"] [tabindex="0"]')).get(index);
  }

  runSuiteButton() {
    return element(by.tagName('app-run-suite-button'));
  }

  selectCTSVersion() {
    return element(by.className('mat-select-value'));
  }

  placeholderOnSelectCTSVersion() {
    return element(by.className('mat-select-placeholder'));
  }

  textModeule() {
    return element(by.id('textInput'));
  }

  textCloseButton() {
    return element(by.buttonText('close'));
  }
}

export class RunSuitePage {
  runSuiteMenu() {
    return element(by.css('a[href*="#/run_tests"]'));
  }

  /**
   * Returns the current using suite
   */
  suiteActive() {
    return element(by.css('[role="tablist"] [tabindex="0"]'));
  }

  loadingMessage() {
    return element(by.id('loading-message'));
  }

  navigateTo() {
    return browser.get('/#/run_tests');
  }
}
