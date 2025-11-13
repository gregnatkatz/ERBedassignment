import { faker } from '@faker-js/faker';
import { Bed, Alert, Patient } from '../types';

const CHIEF_COMPLAINTS = [
  'Chest Pain',
  'Abdominal Pain',
  'Difficulty Breathing',
  'Back Pain',
  'Headache',
  'Minor Cut',
  'Fever',
  'Unresponsive',
  'Major Trauma',
  'Severe Pain',
  'Cold Symptoms',
  'Rash',
];

const ESI_LEVELS = [1, 2, 3, 4, 5];

export function generatePatientName(): string {
  const lastName = faker.person.lastName().toUpperCase();
  const firstInitial = faker.person.firstName()[0].toUpperCase();
  return `${lastName}, ${firstInitial}.`;
}

export function generatePatient(): Patient {
  return {
    id: faker.string.uuid(),
    first_name: faker.person.firstName(),
    last_name: faker.person.lastName(),
    date_of_birth: faker.date.birthdate({ min: 18, max: 90, mode: 'age' }).toISOString().split('T')[0],
    medical_record_number: faker.string.numeric(8),
    created_at: new Date().toISOString(),
  };
}

export function generateOccupiedBed(bedNumber: string, zone: string, telemetry: boolean): Bed {
  const esiScore = faker.helpers.arrayElement(ESI_LEVELS);
  const complaint = faker.helpers.arrayElement(CHIEF_COMPLAINTS);
  
  return {
    id: faker.string.uuid(),
    bed_number: bedNumber,
    zone,
    telemetry,
    isolation: zone === 'isolation',
    occupied: true,
    patient_id: faker.string.uuid(),
    patient_name: generatePatientName(),
    esi_score: esiScore,
    chief_complaint: complaint,
    wait_time_minutes: faker.number.int({ min: 2, max: 55 }),
  };
}

export function generateAlert(): Alert {
  const alertTypes = [
    { type: 'Patient Deterioration Detected', severity: 'critical' as const, icon: '🚨' },
    { type: 'Cardiology Consult Delayed', severity: 'high' as const, icon: '⚠️' },
    { type: 'Bed Optimally Assigned', severity: 'low' as const, icon: '✅' },
    { type: 'Staffing Adjustment Recommended', severity: 'high' as const, icon: '⚠️' },
    { type: 'Surge Risk Updated', severity: 'medium' as const, icon: '📊' },
    { type: 'Lab Results Delayed', severity: 'high' as const, icon: '⚠️' },
    { type: 'Bed Turnover Ready', severity: 'low' as const, icon: '🔄' },
    { type: 'Oxygen Saturation Dropping', severity: 'critical' as const, icon: '🚨' },
    { type: 'Medication Supply Low', severity: 'medium' as const, icon: '⚠️' },
    { type: 'Nurse-Patient Ratio Alert', severity: 'high' as const, icon: '⚠️' },
  ];

  const alert = faker.helpers.arrayElement(alertTypes);
  const bedNumber = `Bed ${faker.number.int({ min: 1, max: 16 })}`;
  const patientName = generatePatientName();
  const agentNames = [
    'Clinical Deterioration Agent',
    'Wait Time Management Agent',
    'Bed Assignment Agent',
    'Staffing Optimization Agent',
    'Resource Prediction Agent',
    'Coordinator Agent',
  ];

  const messages: Record<string, string> = {
    'Patient Deterioration Detected': `${bedNumber} (${patientName}) - BP dropping 140→110, HR increasing 95→125. Immediate MD re-evaluation required.`,
    'Cardiology Consult Delayed': `${bedNumber} (${patientName}) - ${faker.number.int({ min: 30, max: 90 })}min wait exceeds threshold. Telemedicine consult suggested to reduce wait by 25min.`,
    'Bed Optimally Assigned': `New ESI-2 patient assigned to monitored bed. Nurse Sarah notified (lowest current acuity load).`,
    'Staffing Adjustment Recommended': `3 ESI-2 patients in main ER. Consider moving RN Jennifer from fast-track to main ER.`,
    'Surge Risk Updated': `Next 4 hours: Moderate surge risk (35%). Predicted 8-11 ESI-2 arrivals. Resource allocation optimized.`,
    'Lab Results Delayed': `${bedNumber} - Labs ordered ${faker.number.int({ min: 30, max: 60 })}min ago, still pending. Consider follow-up with lab.`,
    'Bed Turnover Ready': `${bedNumber} cleaned and ready for next patient. EVS completed ${faker.number.int({ min: 3, max: 8 })}min ago.`,
    'Oxygen Saturation Dropping': `${bedNumber} - SpO2 declining to ${faker.number.int({ min: 85, max: 92 })}%. Consider supplemental oxygen and respiratory evaluation.`,
    'Medication Supply Low': `Morphine stock below threshold. Pharmacy notified for restock.`,
    'Nurse-Patient Ratio Alert': `Main ER nurse ratio at 1:${faker.number.int({ min: 5, max: 7 })} with 2 ESI-1 patients. Consider reallocation.`,
  };

  return {
    id: faker.string.uuid(),
    visit_id: faker.string.uuid(),
    alert_type: alert.type,
    severity: alert.severity,
    message: messages[alert.type] || `${alert.type} - ${bedNumber}`,
    agent_id: faker.helpers.arrayElement(agentNames),
    created_at: new Date(Date.now() - faker.number.int({ min: 0, max: 900000 })).toISOString(),
    acknowledged: false,
    icon: alert.icon,
  };
}

export function generateInitialBeds(): Bed[] {
  const beds: Bed[] = [];
  const zones = [
    { zone: 'monitored', telemetry: true, count: 4 },
    { zone: 'fast-track', telemetry: false, count: 4 },
    { zone: 'main-ed', telemetry: false, count: 4 },
    { zone: 'trauma', telemetry: true, count: 2 },
    { zone: 'isolation', telemetry: false, count: 2 },
  ];

  let bedNum = 1;
  zones.forEach(({ zone, telemetry, count }) => {
    for (let i = 0; i < count; i++) {
      const bedNumber = `Bed-${bedNum}`;
      const shouldOccupy = faker.datatype.boolean({ probability: 0.7 });
      
      if (shouldOccupy) {
        beds.push(generateOccupiedBed(bedNumber, zone, telemetry));
      } else {
        beds.push({
          id: faker.string.uuid(),
          bed_number: bedNumber,
          zone,
          telemetry,
          isolation: zone === 'isolation',
          occupied: false,
          patient_id: null,
        });
      }
      bedNum++;
    }
  });

  return beds;
}

export function generateInitialAlerts(count: number = 8): Alert[] {
  return Array.from({ length: count }, () => generateAlert());
}
