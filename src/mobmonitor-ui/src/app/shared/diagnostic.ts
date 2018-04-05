export interface Diagnostic {
  category: string;
  checks: DiagnosticEntry[];
}

interface DiagnosticEntry {
  name: string;
  description: string;
}
