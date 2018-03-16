export interface HealthCheck {
  service: string;
  health: 'unhealthy'|'warning'|'healthy';
  errors?: HealthCheckEntry[];
  warnings?: HealthCheckEntry[];
}

interface HealthCheckEntry {
  name: string;
  description: string;
  actions?: string[];
}
