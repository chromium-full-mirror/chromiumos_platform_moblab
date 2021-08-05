// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {browser, element, by, ElementFinder, Locator, Key, ExpectedConditions as until} from 'protractor';

export class Card {
  root: ElementFinder

  constructor(root: ElementFinder) {
    this.root = root;
  }

  element(locator: Locator) {
    return this.root.element(locator);
  }

  isLoading() {
    return until.visibilityOf(this.element(by.tagName('mat-spinner')));
  }

  submitButton() {
    return this.element(by.css('button[type="submit"]'));
  }

  replaceInput(id: string, value: string) {
    const input = this.element(by.id(id));
    return input.sendKeys(Key.chord(Key.CONTROL, 'a'), value);
  }

  scrollTo() {
    browser.wait(until.presenceOf(this.root));
    return browser.actions().mouseMove(this.root).perform();
  }

  valueOf(id: string) {
    return this.element(by.id(id)).getAttribute('value');
  }
}

export class ConfigurationPage {
  card(id: string) {
    return new Card(element(by.id(id)));
  }

  navigateTo() {
    return browser.get('/#/config');
  }
}