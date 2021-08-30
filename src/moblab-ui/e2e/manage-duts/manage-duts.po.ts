// Copyright 2021 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {browser, by, element, ElementFinder} from 'protractor';

export class DUT {
  root: ElementFinder;

  constructor(elm: ElementFinder) {
    this.root = elm;
  }

  toggleSelection() {
    const checkbox = this.root.$('mat-checkbox'),
      label = checkbox.$('label'),
      checked = async () => {
        const str = await checkbox.getAttribute('class');
        return str.split(' ').indexOf('mat-checkbox-checked') !== -1;
      };

    label.click();
    return browser.wait(checked);
  }

  private column(index: number) {
    return this.root.$(`td:nth-child(${index})`).getText();
  }

  name() {
    return this.column(2);
  }

  macAddr() {
    return this.column(3);
  }

  buildTarget() {
    return this.column(4);
  }

  model() {
    return this.column(5);
  }

  status() {
    return this.column(6);
  }

  async pools() {
    const txt = await this.column(7);
    return txt.split(',');
  }

  labels() {
    return this.root.$$('mat-chip').map(elm => elm.getText());
  }
}

export class ManageDutsPage {
  /**
   * Returns the first DUT whose status is "Not Enrolled".
   */
  getUnenrolled() {
    const locator = by.cssContainingText('.mat-cell', 'Not Enrolled');
    return new DUT(element(locator).element(by.xpath('..')));
  }

  /**
   * Returns a DUT whose host name or MAC address matches the given addr.
   * @param {string} addr - IP or MAC address.
   */
  getByAddr(addr: string) {
    const locator = by.cssContainingText('.mat-cell', addr);
    return new DUT(element(locator).element(by.xpath('..')));
  }

  navigateTo() {
    return browser.get('/#/manage_dut');
  }

  /**
   * Determine whether the DUTs list have been loaded.
   */
  async isLoaded() {
    const spinner = element(by.tagName('mat-spinner'));
    return !(await spinner.isPresent());
  }
}
