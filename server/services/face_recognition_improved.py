"""
Improved Face Recognition Service with proper 128D vectors
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
import logging
import os
from core.config import settings

logger = logging.getLogger(__name__)

class ImprovedFaceRecognitionService:
    def __init__(self):
        self.face_cascade = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize OpenCV face detection"""
        try:
            logger.info("🔄 Initializing Improved OpenCV face detection...")
            
            # Load Haar cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                logger.error("Failed to load face cascade classifier")
                return False
            
            self.is_initialized = True
            logger.info("✅ Improved OpenCV face detection initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenCV: {str(e)}")
            return False
    
    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """Detect faces in image using OpenCV"""
        if not self.is_initialized:
            logger.error("Face recognition service not initialized")
            return []
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            face_list = []
            for (x, y, w, h) in faces:
                # Calculate confidence based on face size and position
                confidence = min(1.0, (w * h) / (100 * 100))
                
                face_info = {
                    'bbox': {
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h)
                    },
                    'landmarks': [],
                    'embedding': self._generate_128d_embedding(image[y:y+h, x:x+w]),
                    'confidence': confidence,
                    'age': None,
                    'gender': None
                }
                face_list.append(face_info)
            
            logger.info(f"Detected {len(face_list)} faces")
            return face_list
            
        except Exception as e:
            logger.error(f"Error detecting faces: {str(e)}")
            return []
    
    def _generate_128d_embedding(self, face_roi: np.ndarray) -> List[float]:
        """Generate a proper 128D embedding"""
        try:
            # Resize face to standard size
            face_resized = cv2.resize(face_roi, (64, 64))
            
            # Convert to grayscale
            gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Normalize
            normalized = gray_face.astype(np.float32) / 255.0
            
            # Generate comprehensive features to get exactly 128D
            features = []
            
            # 1. Histogram features (16D)
            hist = cv2.calcHist([gray_face], [0], None, [16], [0, 256])
            features.extend(hist.flatten())
            
            # 2. LBP features (16D)
            lbp_features = self._simple_lbp(normalized)
            features.extend(lbp_features)
            
            # 3. Texture features (5D)
            texture_features = self._extract_texture_features(normalized)
            features.extend(texture_features)
            
            # 4. HOG-like features (32D)
            hog_features = self._extract_hog_features(normalized)
            features.extend(hog_features)
            
            # 5. Gabor features (16D)
            gabor_features = self._extract_gabor_features(normalized)
            features.extend(gabor_features)
            
            # 6. Statistical features (8D)
            stat_features = self._extract_statistical_features(normalized)
            features.extend(stat_features)
            
            # 7. Edge features (16D)
            edge_features = self._extract_edge_features(normalized)
            features.extend(edge_features)
            
            # 8. Frequency domain features (16D)
            freq_features = self._extract_frequency_features(normalized)
            features.extend(freq_features)
            
            # 9. Additional features to reach 128D (3D)
            additional_features = self._extract_additional_features(normalized)
            features.extend(additional_features)
            
            # Ensure exactly 128 dimensions
            if len(features) < 128:
                features.extend([0.0] * (128 - len(features)))
            else:
                features = features[:128]
            
            logger.info(f"Generated {len(features)}D vector")
            return features
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return [0.0] * 128
    
    def _simple_lbp(self, image: np.ndarray) -> List[float]:
        """Simple Local Binary Pattern implementation (16D)"""
        try:
            h, w = image.shape
            lbp = np.zeros_like(image)
            
            for i in range(1, h-1):
                for j in range(1, w-1):
                    center = image[i, j]
                    code = 0
                    code |= (image[i-1, j-1] > center) << 7
                    code |= (image[i-1, j] > center) << 6
                    code |= (image[i-1, j+1] > center) << 5
                    code |= (image[i, j+1] > center) << 4
                    code |= (image[i+1, j+1] > center) << 3
                    code |= (image[i+1, j] > center) << 2
                    code |= (image[i+1, j-1] > center) << 1
                    code |= (image[i, j-1] > center) << 0
                    lbp[i, j] = code
            
            # Calculate histogram
            hist, _ = np.histogram(lbp.ravel(), bins=16, range=(0, 256))
            return hist.astype(float).tolist()
            
        except:
            return [0.0] * 16
    
    def _extract_texture_features(self, image: np.ndarray) -> List[float]:
        """Extract texture features (5D)"""
        try:
            features = []
            
            # Mean and standard deviation
            features.append(np.mean(image))
            features.append(np.std(image))
            
            # Gradient features
            grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
            features.append(np.mean(np.abs(grad_x)))
            features.append(np.mean(np.abs(grad_y)))
            
            # Edge density
            edges = cv2.Canny((image * 255).astype(np.uint8), 50, 150)
            features.append(np.sum(edges > 0) / (image.shape[0] * image.shape[1]))
            
            return features
            
        except:
            return [0.0] * 5
    
    def _extract_hog_features(self, image: np.ndarray) -> List[float]:
        """Extract HOG-like features (32D)"""
        try:
            # Simple HOG implementation
            features = []
            
            # Calculate gradients
            grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate magnitude and orientation
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            orientation = np.arctan2(grad_y, grad_x)
            
            # Create histogram of oriented gradients
            hist, _ = np.histogram(orientation.ravel(), bins=32, range=(-np.pi, np.pi), weights=magnitude.ravel())
            features.extend(hist.astype(float).tolist())
            
            return features
            
        except:
            return [0.0] * 32
    
    def _extract_gabor_features(self, image: np.ndarray) -> List[float]:
        """Extract Gabor features (16D)"""
        try:
            features = []
            
            # Different Gabor filters
            for theta in [0, 45, 90, 135]:
                for freq in [0.1, 0.2]:
                    kernel = cv2.getGaborKernel((21, 21), 5, np.radians(theta), 2*np.pi*freq, 0.5, 0, ktype=cv2.CV_32F)
                    filtered = cv2.filter2D(image, cv2.CV_8UC3, kernel)
                    features.append(np.mean(filtered))
                    features.append(np.std(filtered))
            
            return features
            
        except:
            return [0.0] * 16
    
    def _extract_statistical_features(self, image: np.ndarray) -> List[float]:
        """Extract statistical features (8D)"""
        try:
            features = []
            
            # Basic statistics
            features.append(np.mean(image))
            features.append(np.std(image))
            features.append(np.var(image))
            features.append(np.median(image))
            features.append(np.min(image))
            features.append(np.max(image))
            features.append(np.percentile(image, 25))
            features.append(np.percentile(image, 75))
            
            return features
            
        except:
            return [0.0] * 8
    
    def _extract_edge_features(self, image: np.ndarray) -> List[float]:
        """Extract edge features (16D)"""
        try:
            features = []
            
            # Different edge detection methods
            edges1 = cv2.Canny((image * 255).astype(np.uint8), 50, 150)
            edges2 = cv2.Canny((image * 255).astype(np.uint8), 100, 200)
            
            # Edge statistics
            features.append(np.sum(edges1 > 0) / (image.shape[0] * image.shape[1]))
            features.append(np.sum(edges2 > 0) / (image.shape[0] * image.shape[1]))
            
            # Edge direction histograms
            grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
            orientation = np.arctan2(grad_y, grad_x)
            
            hist, _ = np.histogram(orientation.ravel(), bins=14, range=(-np.pi, np.pi))
            features.extend(hist.astype(float).tolist())
            
            return features
            
        except:
            return [0.0] * 16
    
    def _extract_frequency_features(self, image: np.ndarray) -> List[float]:
        """Extract frequency domain features (16D)"""
        try:
            features = []
            
            # FFT
            fft = np.fft.fft2(image)
            fft_magnitude = np.abs(fft)
            
            # Frequency domain statistics
            features.append(np.mean(fft_magnitude))
            features.append(np.std(fft_magnitude))
            features.append(np.max(fft_magnitude))
            features.append(np.min(fft_magnitude))
            
            # Frequency bands
            h, w = fft_magnitude.shape
            center_h, center_w = h // 2, w // 2
            
            # Low frequency
            low_freq = fft_magnitude[center_h-8:center_h+8, center_w-8:center_w+8]
            features.append(np.mean(low_freq))
            
            # High frequency
            high_freq = fft_magnitude[0:8, :].flatten()
            high_freq = np.concatenate([high_freq, fft_magnitude[-8:, :].flatten()])
            high_freq = np.concatenate([high_freq, fft_magnitude[:, 0:8].flatten()])
            high_freq = np.concatenate([high_freq, fft_magnitude[:, -8:].flatten()])
            features.append(np.mean(high_freq))
            
            # Additional frequency features
            for i in range(10):
                features.append(np.mean(fft_magnitude[i*6:(i+1)*6, :]))
            
            return features
            
        except:
            return [0.0] * 16
    
    def _extract_additional_features(self, image: np.ndarray) -> List[float]:
        """Extract additional features (3D)"""
        try:
            features = []
            
            # Local binary patterns variance
            features.append(np.var(image))
            
            # Entropy
            hist, _ = np.histogram(image.ravel(), bins=256, range=(0, 1))
            hist = hist / hist.sum()
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            features.append(entropy)
            
            # Energy
            features.append(np.sum(image**2))
            
            return features
            
        except:
            return [0.0] * 3
    
    def extract_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract face embedding from image"""
        faces = self.detect_faces(image)
        
        if not faces:
            return None
        
        # Return embedding of the first (largest) face
        best_face = max(faces, key=lambda x: x['bbox']['width'] * x['bbox']['height'])
        return np.array(best_face['embedding'])
    
    def compare_faces(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compare two face embeddings using cosine similarity"""
        try:
            # Normalize embeddings
            emb1_norm = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
            emb2_norm = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
            
            # Calculate cosine similarity
            similarity = np.dot(emb1_norm, emb2_norm)
            
            return float(max(0.0, similarity))
            
        except Exception as e:
            logger.error(f"Error comparing faces: {str(e)}")
            return 0.0

# Global instance
improved_face_service = ImprovedFaceRecognitionService()
