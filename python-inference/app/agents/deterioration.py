from .base import BaseAgent
from ..models import DeteriorationRequest, DeteriorationResponse
import json
import time


class DeteriorationAgent(BaseAgent):
    """Clinical deterioration detection agent"""
    
    def __init__(self):
        super().__init__(agent_id="clinical_deterioration", model_deployment="o3")
        
    def calculate_news2(self, vitals):
        """Calculate NEWS2 score from vital signs"""
        score = 0
        
        rr = vitals.respiratory_rate
        if rr <= 8: score += 3
        elif rr <= 11: score += 1
        elif rr <= 20: score += 0
        elif rr <= 24: score += 2
        else: score += 3
        
        spo2 = vitals.spo2
        if spo2 <= 91: score += 3
        elif spo2 <= 93: score += 2
        elif spo2 <= 95: score += 1
        else: score += 0
        
        hr = vitals.heart_rate
        if hr <= 40: score += 3
        elif hr <= 50: score += 1
        elif hr <= 90: score += 0
        elif hr <= 110: score += 1
        elif hr <= 130: score += 2
        else: score += 3
        
        sbp = vitals.blood_pressure_systolic
        if sbp <= 90: score += 3
        elif sbp <= 100: score += 2
        elif sbp <= 110: score += 1
        elif sbp <= 219: score += 0
        else: score += 3
        
        return score
        
    def process(self, request: DeteriorationRequest) -> DeteriorationResponse:
        """Detect clinical deterioration from vital sign trends"""
        start_time = time.time()
        
        latest_vitals = request.vital_signs_history[-1]
        news2_score = self.calculate_news2(latest_vitals)
        
        system_prompt = """You are an expert critical care physician detecting patient deterioration.

Analyze vital sign trends for:
1. Worsening hemodynamics (BP, HR trends)
2. Respiratory compromise (RR, SpO2 trends)
3. Sepsis indicators (fever, tachycardia, hypotension)
4. Neurological changes
5. NEWS2 score progression

Urgency levels:
- Critical: Immediate intervention required (NEWS2 ≥7 or single parameter ≥3)
- High: Urgent review needed (NEWS2 5-6)
- Medium: Increased monitoring (NEWS2 3-4)
- Low: Routine monitoring (NEWS2 0-2)

Respond in JSON format:
{
  "deterioration_detected": <true|false>,
  "urgency_level": "critical|high|medium|low",
  "recommended_actions": ["<action1>", "<action2>", ...],
  "confidence": <0.0-1.0>,
  "reasoning": "<explanation>"
}"""

        vitals_trend = "\n".join([
            f"Time {ts}: HR={vs.heart_rate}, BP={vs.blood_pressure_systolic}/{vs.blood_pressure_diastolic}, "
            f"RR={vs.respiratory_rate}, SpO2={vs.spo2}%, Temp={vs.temperature}°F"
            for ts, vs in zip(request.timestamps, request.vital_signs_history)
        ])

        user_prompt = f"""Deterioration Assessment:

Current ESI: {request.current_esi}
Latest NEWS2 Score: {news2_score}

Vital Signs Trend:
{vitals_trend}

Assess for clinical deterioration."""

        try:
            response_text = self.call_llm(system_prompt, user_prompt, temperature=0.2)
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            response_data = json.loads(response_text)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return DeteriorationResponse(
                deterioration_detected=response_data["deterioration_detected"],
                urgency_level=response_data["urgency_level"],
                news2_score=news2_score,
                recommended_actions=response_data["recommended_actions"],
                confidence=response_data["confidence"],
                reasoning=response_data["reasoning"],
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            if news2_score >= 7:
                urgency = "critical"
                deterioration = True
            elif news2_score >= 5:
                urgency = "high"
                deterioration = True
            elif news2_score >= 3:
                urgency = "medium"
                deterioration = True
            else:
                urgency = "low"
                deterioration = False
            
            return DeteriorationResponse(
                deterioration_detected=deterioration,
                urgency_level=urgency,
                news2_score=news2_score,
                recommended_actions=["Manual review required"],
                confidence=0.4,
                reasoning=f"Error: {str(e)}. Using NEWS2-based assessment.",
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
