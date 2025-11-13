from .base import BaseAgent
from ..models import BedAssignmentRequest, BedAssignmentResponse
import json
import time


class BedAssignmentAgent(BaseAgent):
    """Bed assignment agent for optimal bed placement"""
    
    def __init__(self):
        super().__init__(agent_id="bed_assignment", model_deployment="o3")
        
    def process(self, request: BedAssignmentRequest) -> BedAssignmentResponse:
        """Assign optimal bed based on patient needs and availability"""
        start_time = time.time()
        
        system_prompt = """You are an expert charge nurse optimizing bed assignments in the ED.

Consider:
1. Patient acuity (ESI level)
2. Required capabilities (telemetry, isolation, bariatric)
3. Zone workload balance
4. Staff-to-patient ratios
5. Proximity to nursing station for high-acuity patients

Respond in JSON format:
{
  "assigned_bed": "<bed_id>",
  "zone": "<zone_name>",
  "confidence": <0.0-1.0>,
  "reasoning": "<explanation>",
  "alternative_beds": ["<bed_id>", ...]
}"""

        beds_info = "\n".join([
            f"- {bed.bed_id}: Zone={bed.zone}, Telemetry={bed.telemetry}, Occupied={bed.occupied}"
            for bed in request.available_beds
        ])
        
        workload_info = "\n".join([
            f"- {zone}: {load*100:.0f}% capacity"
            for zone, load in request.current_workload.items()
        ])

        user_prompt = f"""Bed Assignment Request:

Patient ESI: {request.esi_score}
Requirements:
- Telemetry: {request.patient_requirements.telemetry}
- Isolation: {request.patient_requirements.isolation}
- Bariatric: {request.patient_requirements.bariatric}

Available Beds:
{beds_info}

Current Workload:
{workload_info}

Assign optimal bed."""

        try:
            response_text = self.call_llm(system_prompt, user_prompt, temperature=0.2)
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            response_data = json.loads(response_text)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return BedAssignmentResponse(
                assigned_bed=response_data["assigned_bed"],
                zone=response_data["zone"],
                confidence=response_data["confidence"],
                reasoning=response_data["reasoning"],
                alternative_beds=response_data.get("alternative_beds", []),
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            available = [b for b in request.available_beds if not b.occupied]
            if available:
                bed = available[0]
                processing_time_ms = int((time.time() - start_time) * 1000)
                return BedAssignmentResponse(
                    assigned_bed=bed.bed_id,
                    zone=bed.zone,
                    confidence=0.4,
                    reasoning=f"Error: {str(e)}. Assigned first available bed.",
                    alternative_beds=[],
                    agent_id=self.agent_id,
                    processing_time_ms=processing_time_ms
                )
            else:
                raise Exception("No available beds")
