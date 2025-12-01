import cv2
import numpy as np
import pickle
import insightface
from insightface.app import FaceAnalysis
from pathlib import Path
from app.core.config import FACE_RECOGNITION_CONFIG, PATHS
from app.core.api_client import APIClient

class FaceRecognizer:
    def __init__(self):
        self.app = None
        self.known_embeddings = []
        self.known_ids = [] # IDs stored in pkl
        self.id_to_name = {} # Map ID -> Full Name
        self.api = APIClient()
        
        self.load_model()
        self.load_database()

    def load_model(self):
        """Khởi tạo InsightFace"""
        try:
            print("🔄 Loading InsightFace model...")
            self.app = FaceAnalysis(
                name=FACE_RECOGNITION_CONFIG["model_name"],
                providers=['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            print("✅ Model loaded!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")

    def load_database(self):
        """Load embeddings và map tên người dùng"""
        # 1. Load Embeddings
        embeddings_path = PATHS["dataset_dir"] / "face_embeddings.pkl"
        
        if embeddings_path.exists():
            try:
                with open(embeddings_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_ids = data["names"] # List of IDs (strings)
                    self.known_embeddings = data["embeddings"]
                print(f"✅ Loaded {len(self.known_ids)} users from embeddings")
            except Exception as e:
                print(f"❌ Error loading embeddings: {e}")
        else:
            print("⚠️ No embeddings database found")

        # 2. Load User Info from API to map ID -> Name
        try:
            users = self.api.get("users/")
            if users:
                for u in users:
                    self.id_to_name[str(u['id'])] = u['full_name']
                print(f"✅ Loaded {len(self.id_to_name)} user names from DB")
        except Exception as e:
            print(f"⚠️ Could not load user names: {e}")

    def process_frame(self, frame):
        """
        Xử lý frame: Detect -> Recognize
        Returns: List of results [{"bbox": [x1,y1,x2,y2], "name": str, "score": float, "id": str}]
        """
        if self.app is None:
            return []

        faces = self.app.get(frame)
        results = []
        
        for face in faces:
            bbox = face.bbox.astype(int)
            result = {
                "bbox": bbox,
                "name": "Unknown",
                "score": 0.0,
                "id": None
            }

            if self.known_embeddings:
                embedding = face.embedding
                
                # Tính Cosine Similarity
                sims = []
                for known_emb in self.known_embeddings:
                    sim = np.dot(embedding, known_emb) / (np.linalg.norm(embedding) * np.linalg.norm(known_emb))
                    sims.append(sim)
                
                if sims:
                    max_sim = max(sims)
                    idx = sims.index(max_sim)
                    
                    if max_sim > FACE_RECOGNITION_CONFIG["similarity_threshold"]: # Use config threshold
                        user_id = self.known_ids[idx]
                        name = self.id_to_name.get(str(user_id), f"User {user_id}")
                        
                        result["name"] = name
                        result["score"] = float(max_sim)
                        result["id"] = user_id
            
            results.append(result)

        return results
