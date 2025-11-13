export interface VitalSigns {
  heart_rate: number;
  blood_pressure_systolic: number;
  blood_pressure_diastolic: number;
  respiratory_rate: number;
  spo2: number;
  temperature: number;
  pain_scale: number;
}

export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  medical_record_number: string;
  created_at: string;
}

export interface Bed {
  id: string;
  bed_number: string;
  zone: string;
  telemetry: boolean;
  isolation: boolean;
  occupied: boolean;
  patient_id: string | null;
  patient_name?: string;
  esi_score?: number;
  chief_complaint?: string;
  wait_time_minutes?: number;
}

export interface Alert {
  id: string;
  visit_id: string;
  alert_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  agent_id: string;
  created_at: string;
  acknowledged: boolean;
  icon?: string;
}

export interface Agent {
  id: string;
  name: string;
  confidence: number;
  active: boolean;
}

export interface Metrics {
  door_to_provider: number;
  lwbs_rate: number;
  bed_utilization: number;
  patient_satisfaction: number;
}
