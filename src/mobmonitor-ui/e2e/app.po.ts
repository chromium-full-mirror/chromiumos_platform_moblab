import { browser, by, element } from 'protractor';

//TODO (mattmallett@ crbug.com/824880)
export class AppPage {
  navigateTo() {
    return browser.get('/');
  }

  getParagraphText() {
    return element(by.css('app-root h1')).getText();
  }
}
