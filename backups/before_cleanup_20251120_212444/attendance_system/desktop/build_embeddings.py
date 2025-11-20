"""
Build Face Embeddings Database
Đọc ảnh từ dataset/processed/ → Trích xuất embeddings → Lưu vào face_embeddings.pkl
"""
import cv2
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("❌ InsightFace not installed!")
    print("   Run: pip install insightface onnxruntime")


# ============================================================================
# CONFIGURATION
# ============================================================================

DATASET_ROOT = Path(r"d:\HUTECH\DACN\dataset")
DATASET_PROCESSED = DATASET_ROOT / "processed"
EMBEDDINGS_FILE = DATASET_ROOT / "face_embeddings.pkl"


# ============================================================================
# BUILD EMBEDDINGS
# ============================================================================

def build_embeddings_database():
    """Xây dựng embeddings database từ dataset/processed/"""
    
    if not INSIGHTFACE_AVAILABLE:
        print("\n❌ InsightFace không khả dụng!")
        print("   Cài đặt: pip install insightface onnxruntime")
        return False
    
    print("=" * 80)
    print("  🔧 BUILD FACE EMBEDDINGS DATABASE")
    print("=" * 80)
    print(f"📂 Dataset: {DATASET_PROCESSED}")
    print(f"💾 Output: {EMBEDDINGS_FILE}")
    print("=" * 80)
    
    # Kiểm tra dataset folder
    if not DATASET_PROCESSED.exists():
        print(f"\n❌ Dataset folder không tồn tại: {DATASET_PROCESSED}")
        return False
    
    # Load InsightFace model
    print("\n🔄 Loading InsightFace model...")
    try:
        app = FaceAnalysis(providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False
    
    # Build embeddings
    embeddings_db = {}
    total_students = 0
    total_images = 0
    failed_images = 0
    
    print(f"\n📸 Scanning student folders in {DATASET_PROCESSED}...\n")
    
    # Duyệt qua từng student folder
    student_folders = sorted([d for d in DATASET_PROCESSED.iterdir() if d.is_dir()])
    
    if len(student_folders) == 0:
        print("⚠️  Không tìm thấy folder sinh viên nào!")
        print("   Hãy chụp ảnh cho sinh viên trước (Student Module → 📷 Chụp ảnh)")
        return False
    
    for student_dir in student_folders:
        student_id = student_dir.name
        embeddings = []
        
        print(f"📁 Processing: {student_id}...", end=" ")
        
        # Đọc tất cả ảnh .jpg
        image_files = list(student_dir.glob("*.jpg"))
        
        if len(image_files) == 0:
            print("⚠️  No images")
            continue
        
        for img_path in image_files:
            try:
                # Đọc ảnh
                img = cv2.imread(str(img_path))
                if img is None:
                    failed_images += 1
                    continue
                
                # Detect faces
                faces = app.get(img)
                
                if len(faces) > 0:
                    # Lấy embedding của face đầu tiên
                    embedding = faces[0].embedding
                    embeddings.append(embedding)
                    total_images += 1
                else:
                    failed_images += 1
                    
            except Exception as e:
                print(f"\n   ⚠️  Error on {img_path.name}: {e}")
                failed_images += 1
                continue
        
        if len(embeddings) > 0:
            embeddings_db[student_id] = embeddings
            total_students += 1
            print(f"✅ {len(embeddings)} faces")
        else:
            print("❌ No valid faces")
    
    # Lưu vào file
    print(f"\n💾 Saving embeddings to {EMBEDDINGS_FILE}...")
    try:
        with open(EMBEDDINGS_FILE, 'wb') as f:
            pickle.dump(embeddings_db, f)
        print("✅ Saved successfully!")
    except Exception as e:
        print(f"❌ Save failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("  📊 BUILD SUMMARY")
    print("=" * 80)
    print(f"✅ Total students: {total_students}")
    print(f"✅ Total embeddings: {total_images}")
    print(f"⚠️  Failed images: {failed_images}")
    print(f"💾 Database size: {EMBEDDINGS_FILE.stat().st_size / 1024:.1f} KB")
    print("=" * 80)
    
    # List students
    if total_students > 0:
        print("\n📋 Students in database:")
        for idx, (student_id, embs) in enumerate(embeddings_db.items(), 1):
            print(f"   {idx}. {student_id}: {len(embs)} embeddings")
    
    print("\n🎉 BUILD COMPLETED!")
    print(f"   Embeddings saved to: {EMBEDDINGS_FILE}")
    print(f"   You can now use Attendance Module to recognize faces.\n")
    
    return True


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        success = build_embeddings_database()
        
        if success:
            input("\n✅ Press Enter to exit...")
        else:
            input("\n❌ Build failed. Press Enter to exit...")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
