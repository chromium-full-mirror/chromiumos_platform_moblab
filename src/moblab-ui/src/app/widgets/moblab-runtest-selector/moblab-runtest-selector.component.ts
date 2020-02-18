import {Component, EventEmitter, OnInit, Output, ViewChild} from '@angular/core';

import {MoblabGrpcService} from './../../services/moblab-grpc.service';

@Component({
  selector: 'app-moblab-runtest-selector',
  templateUrl: './moblab-runtest-selector.component.html',
  styleUrls: ['./moblab-runtest-selector.component.scss']
})
export class MoblabRuntestSelectorComponent implements OnInit {
  @ViewChild('modelSelector', { static: true }) modelSelector;
  @ViewChild('buildSelector', { static: true }) buildSelector;
  @ViewChild('poolSelector', { static: true }) poolSelector;

  @Output() update = new EventEmitter();

  private selectedModel: string;
  private selectedBuild: string;
  private selectedPool: string;

  models: string[] = [];
  modelSelectorEnabled = true;
  pools: string[] = [];
  poolSelectorEnabled = false;

  constructor(private moblabRpcService: MoblabGrpcService) {}

  ngOnInit() {
    this.moblabRpcService.listModels((boards: string[]) => {
      this.updateModels(boards);
    });
  }

  updateModels(newModels: string[]) {
    this.models = newModels;
    this.modelSelectorEnabled = true;
  }

  modelChanged(model: string) {
    this.selectedModel = model;
    this.buildSelector.start();
  }

  buildChanged(event) {
    if (event.build) {
      this.selectedBuild = event.build;
      this.moblabRpcService.listPools((pools: string[]) => {
        this.updatePools(pools);
      });
      this.update.emit({model: this.selectedModel, build: this.selectedBuild});
    }
    if (event.board) {
      this.update.emit({board: event.board});
    }

  }

  updatePools(newPools: string[]) {
    this.pools = newPools;
    this.poolSelectorEnabled = true;
  }

  poolChanged(pool: string) {
    this.selectedPool = pool;
    this.update.emit({pool: this.selectedPool});
  }
}
