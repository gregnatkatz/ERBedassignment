from .base import BaseAgent
from ..models import TriageRequest, TriageResponse
import json
import time


class TriageAgent(BaseAgent):
    """Triage agent for ESI scoring and acuity assessment"""
    
    def __init__(self):
        super().__init__(agent_id="triage", model_deployment="o3")
        
    def process(self, request: TriageRequest) -> TriageResponse:
        """Process triage request and return ESI score with reasoning"""
        start_time = time.time()
        
        system_prompt = """You are an expert emergency department triage nurse using the Emergency Severity Index (ESI) system.

ESI Levels:
- Level 1 (Resuscitation): Immediate life-threatening condition requiring immediate intervention
- Level 2 (Emergent): High-risk situation, severe pain/distress, or vital sign abnormalities
- Level 3 (Urgent): Stable but requires multiple resources (2+ of: labs, imaging, procedures, consults)
- Level 4 (Less Urgent): Stable, requires 1 resource
- Level 5 (Non-urgent): No resources needed, minor issue

Consider:
1. Vital signs (HR, BP, RR, SpO2, Temperature, Pain)
2. Chief complaint
3. Age and medical history
4. Risk factors

Respond in JSON format:
{
  "esi_score": <1-5>,
  "confidence": <0.0-1.0>,
  "reasoning": "<detailed explanation>",
  "recommended_actions": ["<action1>", "<action2>", ...]
}"""

        user_prompt = f"""Patient Assessment:

Chief Complaint: {request.chief_complaint}
Age: {request.age} years

Vital Signs:
- Heart Rate: {request.vital_signs.heart_rate} bpm
- Blood Pressure: {request.vital_signs.blood_pressure_systolic}/{request.vital_signs.blood_pressure_diastolic} mmHg
- Respiratory Rate: {request.vital_signs.respiratory_rate} breaths/min
- SpO2: {request.vital_signs.spo2}%
- Temperature: {request.vital_signs.temperature}°F
- Pain Scale: {request.vital_signs.pain_scale}/10

Medical History: {', '.join(request.medical_history) if request.medical_history else 'None reported'}

Provide ESI triage assessment."""

        try:
            response_text = self.call_llm(system_prompt, user_prompt, temperature=0.3)
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            response_data = json.loads(response_text)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return TriageResponse(
                esi_score=response_data["esi_score"],
                confidence=response_data["confidence"],
                reasoning=response_data["reasoning"],
                recommended_actions=response_data["recommended_actions"],
                agent_id=self.agent_id,
                model_version="v1.0",
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            return TriageResponse(
                esi_score=3,
                confidence=0.5,
                reasoning=f"Error processing triage: {str(e)}. Defaulting to ESI-3 for safety.",
                recommended_actions=["Manual triage review required"],
                agent_id=self.agent_id,
                model_version="v1.0",
                processing_time_ms=processing_time_ms
            )
