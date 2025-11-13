from .base import BaseAgent
from ..models import WaitTimeRequest, WaitTimeResponse
import json
import time


class WaitTimeAgent(BaseAgent):
    """Wait time management agent"""
    
    def __init__(self):
        super().__init__(agent_id="wait_time_management", model_deployment="gpt-5")
        
    def process(self, request: WaitTimeRequest) -> WaitTimeResponse:
        """Identify bottlenecks and suggest mitigation strategies"""
        start_time = time.time()
        
        system_prompt = """You are an expert ED flow coordinator identifying and resolving bottlenecks.

Common bottlenecks:
1. Lab delays (slow turnaround)
2. Imaging delays (equipment/staff availability)
3. Consult delays (specialist availability)
4. Bed delays (inpatient bed availability)
5. Discharge delays (paperwork, prescriptions, transportation)

Mitigation strategies:
- Expedite critical orders
- Telemedicine consults
- Parallel processing
- Early discharge planning
- Communication with ancillary services

Respond in JSON format:
{
  "bottleneck_identified": <true|false>,
  "bottleneck_type": "<type>",
  "mitigation_strategies": ["<strategy1>", "<strategy2>", ...],
  "estimated_delay_minutes": <int>,
  "confidence": <0.0-1.0>,
  "reasoning": "<explanation>"
}"""

        user_prompt = f"""Wait Time Analysis:

Patient ESI: {request.esi_score}
Current Wait: {request.current_wait_minutes} minutes
Pending Orders: {', '.join(request.pending_orders) if request.pending_orders else 'None'}

Identify bottlenecks and suggest solutions."""

        try:
            response_text = self.call_llm(system_prompt, user_prompt, temperature=0.4)
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            response_data = json.loads(response_text)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return WaitTimeResponse(
                bottleneck_identified=response_data["bottleneck_identified"],
                bottleneck_type=response_data.get("bottleneck_type"),
                mitigation_strategies=response_data["mitigation_strategies"],
                estimated_delay_minutes=response_data["estimated_delay_minutes"],
                confidence=response_data["confidence"],
                reasoning=response_data["reasoning"],
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            return WaitTimeResponse(
                bottleneck_identified=False,
                bottleneck_type=None,
                mitigation_strategies=[],
                estimated_delay_minutes=0,
                confidence=0.3,
                reasoning=f"Error: {str(e)}",
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
