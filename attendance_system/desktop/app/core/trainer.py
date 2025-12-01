import cv2
import numpy as np
import pickle
import os
from pathlib import Path
from insightface.app import FaceAnalysis
from app.core.config import FACE_RECOGNITION_CONFIG, PATHS

class ModelTrainer:
    def __init__(self):
        self.app = FaceAnalysis(
            name=FACE_RECOGNITION_CONFIG["model_name"],
            providers=['CPUExecutionProvider']
        )
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
    def train_all(self, progress_callback=None):
        """Quét toàn bộ thư mục dataset/raw và tạo embeddings"""
        raw_dir = PATHS["raw_dir"]
        embeddings = []
        names = []
        
        if not raw_dir.exists():
            return False, "Thư mục dataset/raw không tồn tại"
            
        user_folders = [d for d in raw_dir.iterdir() if d.is_dir()]
        total_users = len(user_folders)
        
        if total_users == 0:
            return False, "Không có dữ liệu người dùng để train"

        processed_count = 0
        
        for user_folder in user_folders:
            user_code = user_folder.name
            image_files = list(user_folder.glob("*.jpg")) + list(user_folder.glob("*.png"))
            
            user_embeddings = []
            
            for img_path in image_files:
                img = cv2.imread(str(img_path))
                if img is None: continue
                
                faces = self.app.get(img)
                if len(faces) > 0:
                    # Lấy face lớn nhất
                    face = max(faces, key=lambda x: x.bbox[2] * x.bbox[3])
                    user_embeddings.append(face.embedding)
            
            if user_embeddings:
                # Tính trung bình cộng các vector của 1 người để ra vector đại diện chuẩn nhất
                mean_embedding = np.mean(user_embeddings, axis=0)
                mean_embedding = mean_embedding / np.linalg.norm(mean_embedding) # Normalize
                
                embeddings.append(mean_embedding)
                names.append(user_code) # Lưu User Code làm định danh
                
            processed_count += 1
            if progress_callback:
                progress_callback(processed_count / total_users * 100)

        # Lưu vào file
        data = {"names": names, "embeddings": embeddings}
        save_path = PATHS["dataset_dir"] / "face_embeddings.pkl"
        
        with open(save_path, 'wb') as f:
            pickle.dump(data, f)
            
        return True, f"Đã train xong {len(names)} người dùng!"
    
    def train_user(self, user_code, progress_callback=None):
        """Train thêm 1 người dùng mới vào model hiện tại (Incremental Training)"""
        raw_dir = PATHS["raw_dir"]
        user_folder = raw_dir / user_code
        
        if not user_folder.exists():
            return False, f"Không tìm thấy ảnh của {user_code}"
        
        # Load model hiện tại (nếu có)
        save_path = PATHS["dataset_dir"] / "face_embeddings.pkl"
        
        if save_path.exists():
            with open(save_path, 'rb') as f:
                data = pickle.load(f)
                embeddings = data["embeddings"]
                names = data["names"]
                
            # Kiểm tra user đã tồn tại chưa
            if user_code in names:
                # Xóa user cũ để thay thế
                idx = names.index(user_code)
                del names[idx]
                del embeddings[idx]
                print(f"🔄 Updating existing user: {user_code}")
        else:
            # Tạo model mới
            embeddings = []
            names = []
            print(f"✨ Creating new model with user: {user_code}")
        
        # Extract embeddings từ ảnh của user mới
        image_files = list(user_folder.glob("*.jpg")) + list(user_folder.glob("*.png"))
        user_embeddings = []
        
        for i, img_path in enumerate(image_files):
            img = cv2.imread(str(img_path))
            if img is None: 
                continue
            
            faces = self.app.get(img)
            if len(faces) > 0:
                face = max(faces, key=lambda x: x.bbox[2] * x.bbox[3])
                user_embeddings.append(face.embedding)
            
            if progress_callback:
                progress_callback((i + 1) / len(image_files) * 100)
        
        if not user_embeddings:
            return False, f"Không phát hiện khuôn mặt trong ảnh của {user_code}"
        
        # Tính mean embedding
        mean_embedding = np.mean(user_embeddings, axis=0)
        mean_embedding = mean_embedding / np.linalg.norm(mean_embedding)
        
        # Thêm vào model
        embeddings.append(mean_embedding)
        names.append(user_code)
        
        # Lưu lại
        data = {"names": names, "embeddings": embeddings}
        with open(save_path, 'wb') as f:
            pickle.dump(data, f)
        
        return True, f"✅ Đã thêm {user_code} vào model! (Total: {len(names)} users)"
