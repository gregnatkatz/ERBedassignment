import { useState, useEffect } from 'react';
import { AgentBar } from './components/AgentBar';
import { BedGrid } from './components/BedGrid';
import { AlertFeed } from './components/AlertFeed';
import { MetricsPanel } from './components/MetricsPanel';
import { RequestBedModal } from './components/RequestBedModal';
import { generateInitialBeds, generateInitialAlerts, generateAlert } from './utils/faker';
import { Agent, Bed, Alert, Metrics } from './types';
import { Zap } from 'lucide-react';

function App() {
  const [agents, setAgents] = useState<Agent[]>([
    { id: '1', name: 'Coordinator', confidence: 98, active: false },
    { id: '2', name: 'Triage', confidence: 94, active: false },
    { id: '3', name: 'Resource Prediction', confidence: 87, active: false },
    { id: '4', name: 'Bed Assignment', confidence: 91, active: false },
    { id: '5', name: 'Staffing Optimization', confidence: 89, active: false },
    { id: '6', name: 'Wait Time Management', confidence: 92, active: false },
    { id: '7', name: 'Clinical Deterioration', confidence: 96, active: false },
  ]);

  const [beds, setBeds] = useState<Bed[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const metrics: Metrics = {
    door_to_provider: 28,
    lwbs_rate: 3.2,
    bed_utilization: 75,
    patient_satisfaction: 4.1,
  };

  useEffect(() => {
    setBeds(generateInitialBeds());
    setAlerts(generateInitialAlerts(8));

    const alertInterval = setInterval(() => {
      setAlerts((prev) => {
        const newAlert = generateAlert();
        return [newAlert, ...prev].slice(0, 12);
      });
    }, Math.random() * 7000 + 8000);


    return () => {
      clearInterval(alertInterval);
    };
  }, []);

  const activateAgent = (agentId: string, duration: number = 800) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, active: true } : agent
    ));
    setTimeout(() => {
      setAgents(prev => prev.map(agent => 
        agent.id === agentId ? { ...agent, active: false } : agent
      ));
    }, duration);
  };

  const handleRequestBed = async (data: { patientName: string; esiLevel: string; chiefComplaint: string }) => {
    console.log('Bed request:', data);
    
    activateAgent('1', 600); // Coordinator
    activateAgent('2', 600); // Triage
    
    const processingAlert: Alert = {
      id: `alert-${Date.now()}`,
      visit_id: `visit-${Date.now()}`,
      alert_type: 'Bed Assignment Requested',
      severity: 'low',
      message: `AI processing bed assignment for ${data.patientName} (ESI-${data.esiLevel}, ${data.chiefComplaint})`,
      agent_id: 'Bed Assignment Agent',
      created_at: new Date().toISOString(),
      acknowledged: false,
      icon: '🔄',
    };
    setAlerts((prev) => [processingAlert, ...prev]);

    try {
      activateAgent('4', 1200); // Bed Assignment
      
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/bed-request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_name: data.patientName,
          esi_level: parseInt(data.esiLevel),
          chief_complaint: data.chiefComplaint,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Backend returned ${response.status}: ${errorText}`);
      }

      const result = await response.json();

      if (result.success) {
        activateAgent('3', 600);
        activateAgent('5', 600);
        
        const successAlert: Alert = {
          id: `alert-${Date.now()}-success`,
          visit_id: result.visit_id || `visit-${Date.now()}`,
          alert_type: 'Bed Optimally Assigned',
          severity: 'low',
          message: result.message,
          agent_id: 'Bed Assignment Agent',
          created_at: new Date().toISOString(),
          acknowledged: false,
          icon: '✅',
        };
        setAlerts((prev) => [successAlert, ...prev]);
        
        setBeds((prev) => prev.map(bed => {
          const bedId = bed.bed_number?.trim() || '';
          const assignedBed = String(result.assigned_bed).trim();
          if (bedId === assignedBed) {
            return {
              ...bed,
              occupied: true,
              patient_id: result.patient_id || bed.patient_id,
              patient_name: data.patientName,
              esi_score: parseInt(data.esiLevel),
              chief_complaint: data.chiefComplaint,
              wait_time_minutes: 0,
            };
          }
          return bed;
        }));
        
        setTimeout(() => {
          activateAgent('6', 600);
          activateAgent('7', 600);
        }, 300);
      } else {
        const errorAlert: Alert = {
          id: `alert-${Date.now()}-error`,
          visit_id: `visit-${Date.now()}`,
          alert_type: 'Bed Assignment Failed',
          severity: 'high',
          message: `Failed to assign bed: ${result.message}`,
          agent_id: 'Bed Assignment Agent',
          created_at: new Date().toISOString(),
          acknowledged: false,
          icon: '⚠️',
        };
        setAlerts((prev) => [errorAlert, ...prev]);
      }
    } catch (error) {
      console.error('Bed request failed:', error);
      const errorAlert: Alert = {
        id: `alert-${Date.now()}-error`,
        visit_id: `visit-${Date.now()}`,
        alert_type: 'Bed Assignment Failed',
        severity: 'high',
        message: `Network error: Unable to reach backend service`,
        agent_id: 'Bed Assignment Agent',
        created_at: new Date().toISOString(),
        acknowledged: false,
        icon: '⚠️',
        };
        setAlerts((prev) => [errorAlert, ...prev]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Zap className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">ContosoHealth</h1>
            <p className="text-sm text-slate-400">A Faith Based Organization - AI-Powered Emergency Department Management</p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-green-900/30 border border-green-500/50 px-4 py-2 rounded-full">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-green-300">All Systems Operational</span>
        </div>
      </div>

      <AgentBar agents={agents} />

      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="col-span-2">
          <BedGrid beds={beds} />
        </div>
        <div className="col-span-1">
          <AlertFeed alerts={alerts} onRequestBed={() => setIsModalOpen(true)} />
        </div>
      </div>

      <MetricsPanel metrics={metrics} />

      <RequestBedModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleRequestBed}
      />
    </div>
  );
}

export default App;
