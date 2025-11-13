from .base import BaseAgent
from ..models import StaffingRequest, StaffingResponse, StaffingRecommendation
from ..rag.chroma_client import get_rag_client
import json
import time


class StaffingAgent(BaseAgent):
    """Staffing optimization agent"""
    
    def __init__(self):
        super().__init__(agent_id="staffing_optimization", model_deployment="gpt-5")
        self.rag_client = get_rag_client()
        
    def process(self, request: StaffingRequest) -> StaffingResponse:
        """Analyze staffing needs and provide recommendations"""
        start_time = time.time()
        
        guidelines = self.rag_client.query_guidelines("staffing ratios nurse patient", n_results=2)
        guidelines_text = "\n\n".join([f"Guideline: {g['text']}" for g in guidelines])
        
        system_prompt = f"""You are an expert ED operations manager optimizing staffing.

Consider:
1. Patient census and acuity distribution
2. Recommended nurse-to-patient ratios (ESI 1-2: 1:2, ESI 3: 1:4, ESI 4-5: 1:6)
3. Time of day (peak hours, shift changes)
4. Staff fatigue and break coverage

CLINICAL GUIDELINES (from RAG):
{guidelines_text}

Respond in JSON format:
{{
  "recommendations": [
    {{"action": "add_staff|reallocate|no_change", "details": "<details>", "priority": "high|medium|low"}}
  ],
  "confidence": <0.0-1.0>,
  "reasoning": "<explanation>"
}}"""

        esi_info = "\n".join([
            f"- ESI {level}: {count} patients"
            for level, count in request.esi_distribution.items()
        ])

        user_prompt = f"""Staffing Analysis:

Current Census: {request.current_census} patients
Current Staff: {request.staff_count} nurses
Time: {request.time_of_day}

ESI Distribution:
{esi_info}

Provide staffing recommendations."""

        try:
            response_text = self.call_llm(system_prompt, user_prompt, temperature=0.3)
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            response_data = json.loads(response_text)
            
            recommendations = [
                StaffingRecommendation(**rec) for rec in response_data["recommendations"]
            ]
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return StaffingResponse(
                recommendations=recommendations,
                confidence=response_data["confidence"],
                reasoning=response_data["reasoning"],
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            return StaffingResponse(
                recommendations=[
                    StaffingRecommendation(
                        action="no_change",
                        details=f"Error: {str(e)}",
                        priority="low"
                    )
                ],
                confidence=0.3,
                reasoning="Error in staffing analysis",
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
