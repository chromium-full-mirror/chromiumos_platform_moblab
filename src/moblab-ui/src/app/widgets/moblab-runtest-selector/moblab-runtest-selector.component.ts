import { Component, OnInit, ViewChild, Output, EventEmitter } from "@angular/core";
import { MoblabGrpcService } from "./../../services/moblab-grpc.service";

@Component({
  selector: "app-moblab-runtest-selector",
  templateUrl: "./moblab-runtest-selector.component.html",
  styleUrls: ["./moblab-runtest-selector.component.scss"]
})
export class MoblabRuntestSelectorComponent implements OnInit {
  @ViewChild("modelSelector") modelSelector;
  @ViewChild("buildSelector") buildSelector;
  @ViewChild("poolSelector") poolSelector;

  @Output() update = new EventEmitter();

  constructor(private moblabRpcService: MoblabGrpcService) {}

  private selectedModel: string;
  private selectedBuild: string;
  private selectedPool: string;

  models: string[] = [];
  modelSelectorEnabled = true;
  pools: string[] = [];
  poolSelectorEnabled = false;

  ngOnInit() {
    this.moblabRpcService.listModels((boards: string[]) => {
      this.updateModels(boards);
    });
  }

  updateModels(newModels: string[]) {
    this.models = newModels;
    this.modelSelectorEnabled = true;
  }

  modelChanged(model: string, placeholder) {
    this.selectedModel = model;
    this.buildSelector.start();
  }

  buildChanged(selectedBuild: string) {
    this.selectedBuild = selectedBuild;
    this.moblabRpcService.listPools((pools: string[]) => {
      this.updatePools(pools);
    });
    console.log("Emitting");
    console.log({ model: this.selectedModel,
      build: this.selectedBuild });
    this.update.emit({ model: this.selectedModel,
                       build: this.selectedBuild }
                     );
  }

  updatePools(newPools: string[]) {
    this.pools = newPools;
    this.poolSelectorEnabled = true;
  }

  poolChanged(pool: string, placeholder) {
    this.selectedPool = pool;
    this.update.emit({ pool: this.selectedPool } );
  }
}
