import { Component, OnInit } from "@angular/core";
import { MatSnackBar } from "@angular/material/snack-bar";

@Component({
  selector: "app-sidebar",
  templateUrl: "./app-sidebar.component.html",
  styleUrls: ["./app-sidebar.component.scss"]
})
export class AppSidebarComponent implements OnInit {

  showUnlaunched = true;

  constructor() {
  }

  appErrorMessage = "This is where error messages go";

  navTabsAboveRun = [
    { route: "/view_jobs", label: "View Jobs", icon: "visibility" }
  ];

  navTabsBelowRun = [
    { route: "/manage_dut", label: "Manage DUT's", icon: "laptop_chromebook" },
    { route: "/config", label: "Configuration", icon: "settings" },
    { route: "/mobmonitor", label: "Mobmonitor", icon: "security" },
    { route: "/advanced", label: "Advanced Settings", icon: "settings_applications"},
    { route: "/report_problem", label: "Report Problem", icon: "bug_report" },
    { route: "/documentation", label: "Documentation", icon: "help" }
  ];

  testMenuOptions = [];


  if (showUnlaunched = true) {
    this.testMenuOptions.concat(
      [
        { route: "/run_tests/cts", label: "Android Qualification" },
        { route: "/run_tests/storagequal", label: "Storage Qualification" },
        { route: "/run_tests/memoryqual", label: "Memory Qualification" },
        { route: "/run_tests/bvt", label: "Board Qualification" },
        { route: "/run_tests/power", label: "Power" },
        { route: "/run_tests/other", label: "Run Suite" }
      ]);
  };



  ngOnInit() {}

  onSend(event){
    console.log(event);
  }
}
