from .base import BaseAgent
from ..models import ResourcePredictionRequest, ResourcePredictionResponse, PredictedOrder
from ..rag.chroma_client import get_rag_client
import json
import time


class ResourcePredictionAgent(BaseAgent):
    """Resource prediction agent for labs, imaging, and consults"""
    
    def __init__(self):
        super().__init__(agent_id="resource_prediction", model_deployment="gpt-5")
        self.rag_client = get_rag_client()
        
    def process(self, request: ResourcePredictionRequest) -> ResourcePredictionResponse:
        """Predict required resources based on patient presentation"""
        start_time = time.time()
        
        query = f"ESI {request.esi_score} {request.chief_complaint} resource prediction"
        guidelines = self.rag_client.query_guidelines(query, n_results=2)
        guidelines_text = "\n\n".join([f"Guideline: {g['text']}" for g in guidelines])
        
        system_prompt = f"""You are an expert emergency physician predicting required resources for ED patients.

Predict:
1. Labs needed (CBC, CMP, Troponin, D-dimer, etc.)
2. Imaging (X-ray, CT, Ultrasound, MRI)
3. Consults (Cardiology, Surgery, Neurology, etc.)
4. Medications
5. Length of stay (hours)
6. Admission probability (0.0-1.0)

Consider ESI level, chief complaint, age, and vital signs.

CLINICAL GUIDELINES (from RAG):
{guidelines_text}

Respond in JSON format:
{{
  "predicted_orders": [
    {{"type": "lab|imaging|consult|medication", "name": "<name>", "priority": "stat|urgent|routine"}}
  ],
  "predicted_los_hours": <float>,
  "admission_probability": <0.0-1.0>,
  "confidence": <0.0-1.0>,
  "reasoning": "<explanation>"
}}"""

        user_prompt = f"""Patient Information:

Chief Complaint: {request.chief_complaint}
ESI Score: {request.esi_score}
Age: {request.age} years

Vital Signs:
- Heart Rate: {request.vital_signs.heart_rate} bpm
- Blood Pressure: {request.vital_signs.blood_pressure_systolic}/{request.vital_signs.blood_pressure_diastolic} mmHg
- Respiratory Rate: {request.vital_signs.respiratory_rate} breaths/min
- SpO2: {request.vital_signs.spo2}%
- Temperature: {request.vital_signs.temperature}°F
- Pain Scale: {request.vital_signs.pain_scale}/10

Predict required resources."""

        try:
            response_text = self.call_llm(system_prompt, user_prompt, temperature=0.4)
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            response_data = json.loads(response_text)
            
            predicted_orders = [
                PredictedOrder(**order) for order in response_data["predicted_orders"]
            ]
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return ResourcePredictionResponse(
                predicted_orders=predicted_orders,
                predicted_los_hours=response_data["predicted_los_hours"],
                admission_probability=response_data["admission_probability"],
                confidence=response_data["confidence"],
                reasoning=response_data["reasoning"],
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            return ResourcePredictionResponse(
                predicted_orders=[],
                predicted_los_hours=2.0,
                admission_probability=0.5,
                confidence=0.3,
                reasoning=f"Error: {str(e)}",
                agent_id=self.agent_id,
                processing_time_ms=processing_time_ms
            )
