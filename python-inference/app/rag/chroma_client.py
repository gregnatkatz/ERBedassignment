"""ChromaDB client for clinical guidelines RAG."""
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os

class ClinicalGuidelinesRAG:
    """RAG system for clinical guidelines using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client and embedding model."""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.collection = self.client.get_or_create_collection(
            name="clinical_guidelines",
            metadata={"description": "ESI protocols, treatment pathways, and clinical guidelines"}
        )
        
        if self.collection.count() == 0:
            self._initialize_guidelines()
    
    def _initialize_guidelines(self):
        """Initialize collection with sample clinical guidelines."""
        guidelines = [
            {
                "id": "esi-1-protocol",
                "text": "ESI Level 1 (Resuscitation): Immediate life-threatening conditions requiring immediate physician evaluation and intervention. Examples: cardiac arrest, severe respiratory distress, unresponsive, major trauma with shock. Immediate bed assignment to trauma bay or resuscitation room with full monitoring.",
                "category": "ESI Protocol",
                "esi_level": 1
            },
            {
                "id": "esi-2-protocol",
                "text": "ESI Level 2 (Emergent): High-risk situations requiring rapid evaluation within 10 minutes. Examples: chest pain with cardiac risk factors, severe pain (8-10/10), altered mental status, high-risk mechanisms of injury. Assign to monitored bed with telemetry if available. Immediate labs and imaging as indicated.",
                "category": "ESI Protocol",
                "esi_level": 2
            },
            {
                "id": "esi-3-protocol",
                "text": "ESI Level 3 (Urgent): Stable patients requiring multiple resources (2+ of: labs, imaging, IV medications, specialist consult). Examples: abdominal pain requiring CT, moderate trauma, fever with suspected infection. Target evaluation within 30 minutes. Standard bed assignment based on acuity and resource needs.",
                "category": "ESI Protocol",
                "esi_level": 3
            },
            {
                "id": "chest-pain-pathway",
                "text": "Chest Pain Pathway: For patients with chest pain and cardiac risk factors: Immediate ECG within 10 minutes, troponin at 0 and 3 hours, aspirin 325mg unless contraindicated, continuous cardiac monitoring, cardiology consult if STEMI or NSTEMI. Assign to monitored bed with telemetry.",
                "category": "Treatment Pathway",
                "condition": "chest_pain"
            },
            {
                "id": "sepsis-pathway",
                "text": "Sepsis Pathway: For patients with suspected infection and SIRS criteria: Immediate lactate, blood cultures x2, broad-spectrum antibiotics within 1 hour, IV fluid bolus 30mL/kg. ICU consult if septic shock. Prioritize bed assignment and expedite labs.",
                "category": "Treatment Pathway",
                "condition": "sepsis"
            },
            {
                "id": "bed-assignment-principles",
                "text": "Bed Assignment Principles: Match patient acuity to bed capabilities (monitored vs non-monitored). Consider isolation needs. Balance nurse workload - avoid clustering high-acuity patients. Proximity to nursing station for unstable patients.",
                "category": "Operations",
                "topic": "bed_assignment"
            },
            {
                "id": "staffing-ratios",
                "text": "Staffing Ratios: ESI 1-2 patients require 1:2-3 nurse ratio. ESI 3 patients 1:4 ratio. ESI 4-5 patients 1:5-6 ratio in fast-track. Monitor ratios continuously and reallocate staff as acuity changes.",
                "category": "Operations",
                "topic": "staffing"
            },
            {
                "id": "resource-prediction",
                "text": "Resource Prediction: ESI 1-2 typically require labs, imaging, IV access, medications, specialist consults. ESI 3 requires 2+ resources. Anticipate needs based on chief complaint: chest pain → ECG, troponin, cardiology; abdominal pain → labs, CT, surgery consult.",
                "category": "Operations",
                "topic": "resource_prediction"
            }
        ]
        
        for guideline in guidelines:
            embedding = self.embedding_model.encode(guideline["text"]).tolist()
            self.collection.add(
                ids=[guideline["id"]],
                embeddings=[embedding],
                documents=[guideline["text"]],
                metadatas=[{k: v for k, v in guideline.items() if k not in ["id", "text"]}]
            )
        
        print(f"Initialized ChromaDB with {len(guidelines)} clinical guidelines")
    
    def query_guidelines(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Query clinical guidelines based on semantic similarity."""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        guidelines = []
        if results and results['documents']:
            for i in range(len(results['documents'][0])):
                guidelines.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        
        return guidelines

rag_client = None

def get_rag_client() -> ClinicalGuidelinesRAG:
    """Get or create global RAG client."""
    global rag_client
    if rag_client is None:
        rag_client = ClinicalGuidelinesRAG()
    return rag_client
