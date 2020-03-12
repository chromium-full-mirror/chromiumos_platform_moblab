import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

import { MobmonitorRpcService } from '../services/mobmonitor-rpc.service';
import { ErrorDisplayService } from '../services/error-display.service';
import { Diagnostic } from '../shared/diagnostic';
import { DiagnosticResult } from '../shared/diagnostic-result';

@Component({
  selector: 'mob-diagnostics',
  templateUrl: './diagnostics.component.html',
  styleUrls: ['./diagnostics.component.scss']
})
export class DiagnosticsComponent implements OnInit {
  // list of diagnostic definitions
  diagnostics: Diagnostic[] = [];

  // indicates whether a diagnostic defined by a diagnosticKey is
  // currently running, used for UI indicators
  private diagnosticRunning: { [key: string]: boolean } = {};

  // holds the results of running a diagnostic, grouped by diagnosticKey
  private diagnosticResult: { [key: string]: DiagnosticResult } = {};

  // whether user has chosen to hide a completed diagnostic, key is diagnosticKey
  private resultHidden: { [key: string]: boolean } = {};

  constructor(
    private rpc: MobmonitorRpcService,
    public snackBar: MatSnackBar,
    private errorDisplay: ErrorDisplayService
  ) {}

  ngOnInit() {
    this.rpc.listDiagnostics().subscribe(
      data => {
        this.diagnostics = data;
        for (const diagnostic of this.diagnostics) {
          for (const check of diagnostic.checks) {
            const key = this.getDiagnosticKey(diagnostic.category, check.name);
            this.diagnosticRunning[key] = false;
          }
        }
      },
      error => {
        this.errorDisplay.openErrorDialog(error);
      }
    );
  }

  runDiagnostic(category: string, name: string) {
    const key = this.getDiagnosticKey(category, name);
    this.diagnosticRunning[key] = true;
    this.diagnosticResult[key] = undefined;
    this.rpc
      .runDiagnostic({
        category,
        name
      })
      .subscribe(
        result => {
          // cache the response
          this.diagnosticResult[key] = result;
          this.diagnosticRunning[key] = false;
          this.resultHidden[key] = false;
          this.snackBar.open(`Diagnostic ${name} complete`, 'OK', {
            duration: 2000
          });
        },
        error => {
          this.diagnosticRunning[key] = false;
          this.errorDisplay.openErrorDialog(error);
        }
      );
  }

  // UI indicator telling if the diagnostic is running and awaiting response
  isDiagnosticRunning(category: string, name: string): boolean {
    return this.diagnosticRunning[this.getDiagnosticKey(category, name)];
  }

  // Fetch the response, if any, from the diagnosticResults cache
  getDiagnosticResult(category: string, name: string): string {
    const result = this.diagnosticResult[this.getDiagnosticKey(category, name)];
    if (result) {
      return result.result;
    } else {
      return undefined;
    }
  }

  // Users can toggle on/off results, as they can be quite long
  isResultHidden(category: string, name: string): boolean {
    const key = this.getDiagnosticKey(category, name);
    return this.resultHidden[key];
  }

  toggleResult(category: string, name: string) {
    const key = this.getDiagnosticKey(category, name);
    this.resultHidden[key] = !this.resultHidden[key];
  }

  getToggleResultText(category: string, name: string): string {
    return this.isResultHidden(category, name) ? 'show' : 'hide';
  }

  // combines a category from Diagnostic.category and a name from Diagnostic.checks[i].name
  // into a consistent key to be used in various component objects
  private getDiagnosticKey(category: string, name: string): string {
    return `${category} ${name}`;
  }

  getButtonId(category: string, name: string): string {
    return `diagnostic-${category.split(' ').join('-')}-${name
      .split(' ')
      .join('-')}`;
  }
}
