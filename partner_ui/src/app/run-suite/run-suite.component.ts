import {Component, ViewChild, OnInit} from '@angular/core';
import {MoblabRpcService} from '../services/services.module';

@Component({
  selector: 'run-suite',
  template: `
    <table>
        <tr>
          <moblab-selector
            #boardSelector
            [title] = "'Select board:'"
            [options] = "['Pick from available boards', 'veyron_jerry']"
            (update) = "boardChanged($event.value, $event.index)">
          </moblab-selector>
          <moblab-selector
            #buildSelector
            [title] = "'Select build:'"
            [options] = "['Pick from available builds']"
            (update) = "buildChanged($event.value, $event.index)">
          >
          </moblab-selector>
          <moblab-selector
            #suiteSelector
            [title] = "'Select suite:'"
            [options] = "['Pick from available suites']"
            (update) = "suiteChanged($event.value, $event.index)">
          >
          </moblab-selector>
          <moblab-selector
            #rwFirmwareSelector
            [title] = "'RW Firmware (Optional):'"
            [options] = "['Select the RW Firmware (Faft only) (Optional)']"
          >
          </moblab-selector>
          <moblab-selector
            #roFirmwareSelector
            [title] = "'RO Firmware (Optional):'"
            [options] = "['Select the RO Firmware (Faft only) (Optional)']"
          >
          </moblab-selector>
          <moblab-selector
            #poolSelector
            [title] = "'Pool (Optional):'"
            [options] = "['Select a pool']"
          >
          </moblab-selector>
        </tr>
    </table>
    <button disabled #runSuiteButton (click)="onRunSuite()">Run Suite</button>
    `,
})

export class RunSuiteComponent implements OnInit {
  pickBoard = ["Pick from available boards"];
  pickBuild = ["Pick from available builds"];
  pickSuite = ["Pick from available suites"];
  pickRwFirmware = ["Select the RW Firmware (Faft only) (Optional)"];
  pickRoFirmware = ["Select the RO Firmware (Faft only) (Optional)"];
  pickSuites = ["Select a pool"];
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
        this.boardSelector.options = this.pickBoard.concat(boards);
        this.boardSelector.setDisabled(false);
      });

    var pools: string;
    this.moblabRpcService.getPools().subscribe(
      response => { pools = response },
      error => { console.log("Error happened" + error) },
      () => {
        this.poolSelector.options = this.pickSuites.concat(pools);
        if (pools.length > 0) {
          this.poolSelector.setDisabled(false);
        }
      });
  }

  boardChanged(boardName, selectedIndex) {
    if(selectedIndex == 0) {
      this.buildSelector.options = [].concat(this.pickBuild);
      this.buildSelector.setDisabled(true);
    } else {
      var builds: string;

      this.moblabRpcService.getBuilds(boardName).subscribe(
        response => { builds = response },
        error => { console.log("Error happened" + error) },
        () => {
          this.buildSelector.options = [].concat(this.pickBuild).concat(builds);
          this.buildSelector.setDisabled(false);
        });
    }
  }

  buildChanged(value, index) {
    if(index == 0) {
      this.suiteSelector.options = this.pickSuite;
      this.suiteSelector.setDisabled(true);
    } else {
      this.suiteSelector.options = this.pickSuite.concat(this.suites);
      this.suiteSelector.setDisabled(false);
    }
  };

  suiteChanged(value, index) {
    if(index != 0) {
      this.runSuiteButton.nativeElement.disabled = false;
    }
  };

  onRunSuite() {
    this.moblabRpcService.runSuite(this.boardSelector.getSelectedValue(),
      this.buildSelector.getSelectedValue(), this.suiteSelector.getSelectedValue(),
      this.poolSelector.getSelectedValue(), null, null).subscribe(
      response => { console.log(response) },
      error => { console.log("Error happened" + error) });
  }

}

