import { MoblabPartnerUiPage } from './app.po';

describe('moblab-partner-ui App', function() {
  let page: MoblabPartnerUiPage;

  beforeEach(() => {
    page = new MoblabPartnerUiPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
