import {Component, ViewChild, OnInit} from '@angular/core';
import {MoblabRpcService} from '../services/services.module';

@Component({
  selector: 'run-suite',
  template: `
    <md-list>
          <moblab-selector
            #boardSelector
            [title] = "'Select board:'"
            [placeholder] = "['Pick from available boards']"
            (update) = "boardChanged($event.value, $event.index)">
          </moblab-selector>
          <moblab-selector
            #buildSelector
            [title] = "'Select build:'"
            [placeholder] = "['Pick from available builds']"
            (update) = "buildChanged($event.value, $event.index)">
          >
          </moblab-selector>
          <moblab-selector
            #suiteSelector
            [title] = "'Select suite:'"
            [placeholder] = "['Pick from available suites']"
            (update) = "suiteChanged($event.value, $event.index)">
          >
          </moblab-selector>
          <moblab-selector
            #rwFirmwareSelector
            [title] = "'RW Firmware (Optional):'"
            [placeholder] = "['Select the RW Firmware (Faft only) (Optional)']"
            [isShown] = "false"
          >
          </moblab-selector>
          <moblab-selector
            #roFirmwareSelector
            [title] = "'RO Firmware (Optional):'"
            [placeholder] = "['Select the RO Firmware (Faft only) (Optional)']"
            [isShown] = "false"
          >
          </moblab-selector>
          <moblab-selector
            #poolSelector
            [title] = "'Pool (Optional):'"
            [placeholder] = "['Select a pool']"
          >
          </moblab-selector>
    <button md-raised-button color="primary" disabled #runSuiteButton (click)="onRunSuite()">Run Suite</button>
    </md-list>
    `,
})

export class RunSuiteComponent implements OnInit {
  suites = ["bvt-cq", "bvt-inline", "cts", "gts", "hardware_storagequal", "hardware_memoryqual",
            "faft_setup", "faft_ec", "faft_bios"];

  constructor(private moblabRpcService: MoblabRpcService) { }

  @ViewChild('boardSelector') boardSelector;
  @ViewChild('buildSelector') buildSelector;
  @ViewChild('suiteSelector') suiteSelector;
  @ViewChild('rwFirmwareSelector') rwFirmwareSelector;
  @ViewChild('roFirmwareSelector') roFirmwareSelector;
  @ViewChild('poolSelector') poolSelector;
  @ViewChild('runSuiteButton') runSuiteButton;

  ngOnInit() {
    var boards: string;
    this.moblabRpcService.getBoards().subscribe(
      response => { boards = response },
      error => { console.log("Error happened" + error) },
      () => {
        this.boardSelector.options = boards;
      });

    var pools: string;
    this.moblabRpcService.getPools().subscribe(
      response => { pools = response },
      error => { console.log("Error happened" + error) },
      () => {
        this.poolSelector.options = pools;
      });
  }

  boardChanged(boardName, selectedIndex) {

    var builds: string;

    this.moblabRpcService.getBuilds(boardName).subscribe(
      response => { builds = response },
      error => { console.log("Error happened" + error) },
      () => {
        this.buildSelector.options = builds;
      });

  }

  buildChanged(value) {
    this.suiteSelector.options = this.suites;
  };

  suiteChanged(value) {
    let suiteSelected: string = this.suiteSelector.getSelectedValue();
    var showFirmware: boolean = false;
    var builds: string;
    let boardName = this.boardSelector.getSelectedValue();
    if (suiteSelected == "faft_setup") {
      showFirmware = true;
      this.moblabRpcService.getFirmwareBuilds(boardName).subscribe(
          response => {
            builds = response
          },
          error => {
            console.log("Error happened" + error)
          },
          () => {
            this.rwFirmwareSelector.options = builds;
            this.roFirmwareSelector.options = builds;
          });
    }
    this.rwFirmwareSelector.setVisible(showFirmware);
    this.roFirmwareSelector.setVisible(showFirmware);
    this.runSuiteButton.disabled = false;
  };

  onRunSuite() {
    this.moblabRpcService.runSuite(this.boardSelector.getSelectedValue(),
      this.buildSelector.getSelectedValue(), this.suiteSelector.getSelectedValue(),
      this.poolSelector.getSelectedValue(), this.rwFirmwareSelector.getSelectedValue(),
      this.roFirmwareSelector.getSelectedValue()).subscribe(
      response => { console.log(response) },
      error => { console.log("Error happened" + error) });
  }

}

