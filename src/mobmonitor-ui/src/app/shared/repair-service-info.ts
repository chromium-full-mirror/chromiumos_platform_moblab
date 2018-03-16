export interface RepairServiceInfo {
  service: string;
  healthcheck: string;
  action: string;
  args: string[];
  kwargs: any;
}
