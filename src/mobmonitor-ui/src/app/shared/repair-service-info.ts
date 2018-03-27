export interface RepairServiceInfo {
  service: string;
  healthcheck: string;
  action: string;
  params: {[key: string]: string};
}
