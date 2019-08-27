import { Component, Input, OnInit } from "@angular/core";
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from "@angular/platform-browser";
@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.css"]
})

export class AppComponent implements OnInit {
  constructor(
    private matIconRegistry: MatIconRegistry,
    private domSanitizer: DomSanitizer
  ) {
    this.matIconRegistry.addSvgIcon(
      "moblab",
      this.domSanitizer.bypassSecurityTrustResourceUrl("../assets/moblab.svg")
    );
  }

  // @Input() toShow: string;

  ngOnInit() {
    console.log("Starting app....");
  }

  // getButtonColor(buttonName) {
  //   if (buttonName === this.toShow) {
  //      return("primary");
  //   } else {
  //     return("");
  //   }
  // }
}
