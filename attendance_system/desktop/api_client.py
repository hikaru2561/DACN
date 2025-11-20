"""
API Client - Kết nối với Backend API
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime


class APIClient:
    """Client để gọi Backend REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def _get(self, endpoint: str, params: dict = None) -> dict:
        """GET request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
    
    def _post(self, endpoint: str, data: dict) -> dict:
        """POST request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
    
    def _put(self, endpoint: str, data: dict) -> dict:
        """PUT request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
    
    def _delete(self, endpoint: str) -> dict:
        """DELETE request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.delete(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
    
    # ========================================================================
    # HEALTH CHECK
    # ========================================================================
    
    def health_check(self) -> bool:
        """Kiểm tra kết nối API"""
        result = self._get("/health")
        return result is not None and result.get("status") == "healthy"
    
    # ========================================================================
    # STUDENTS
    # ========================================================================
    
    def get_students(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Lấy danh sách sinh viên"""
        result = self._get("/api/students", params={"skip": skip, "limit": limit})
        return result if result else []
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """Lấy thông tin một sinh viên"""
        return self._get(f"/api/students/{student_id}")
    
    def create_student(self, student_data: dict) -> Optional[Dict]:
        """Tạo sinh viên mới"""
        return self._post("/api/students", student_data)
    
    def update_student(self, student_id: str, student_data: dict) -> Optional[Dict]:
        """Cập nhật sinh viên"""
        return self._put(f"/api/students/{student_id}", student_data)
    
    def delete_student(self, student_id: str) -> bool:
        """Xóa sinh viên"""
        result = self._delete(f"/api/students/{student_id}")
        return result is not None
    
    # ========================================================================
    # TEACHERS
    # ========================================================================
    
    def get_teachers(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Lấy danh sách giảng viên"""
        result = self._get("/api/teachers", params={"skip": skip, "limit": limit})
        return result if result else []
    
    def get_teacher(self, teacher_id: str) -> Optional[Dict]:
        """Lấy thông tin một giảng viên"""
        return self._get(f"/api/teachers/{teacher_id}")
    
    def create_teacher(self, teacher_data: dict) -> Optional[Dict]:
        """Tạo giảng viên mới"""
        return self._post("/api/teachers", teacher_data)
    
    def update_teacher(self, teacher_id: str, teacher_data: dict) -> Optional[Dict]:
        """Cập nhật giảng viên"""
        return self._put(f"/api/teachers/{teacher_id}", teacher_data)
    
    def delete_teacher(self, teacher_id: str) -> bool:
        """Xóa giảng viên"""
        result = self._delete(f"/api/teachers/{teacher_id}")
        return result is not None
    
    # ========================================================================
    # SUBJECTS
    # ========================================================================
    
    def get_subjects(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Lấy danh sách môn học"""
        result = self._get("/api/subjects", params={"skip": skip, "limit": limit})
        return result if result else []
    
    def get_subject(self, subject_id: str) -> Optional[Dict]:
        """Lấy thông tin một môn học"""
        return self._get(f"/api/subjects/{subject_id}")
    
    def create_subject(self, subject_data: dict) -> Optional[Dict]:
        """Tạo môn học mới"""
        return self._post("/api/subjects", subject_data)
    
    def update_subject(self, subject_id: str, subject_data: dict) -> Optional[Dict]:
        """Cập nhật môn học"""
        return self._put(f"/api/subjects/{subject_id}", subject_data)
    
    def delete_subject(self, subject_id: str) -> bool:
        """Xóa môn học"""
        result = self._delete(f"/api/subjects/{subject_id}")
        return result is not None
    
    # ========================================================================
    # CLASSES
    # ========================================================================
    
    def get_classes(self, is_active: bool = None, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Lấy danh sách lớp học"""
        params = {"skip": skip, "limit": limit}
        if is_active is not None:
            params["is_active"] = is_active
        result = self._get("/api/classes", params=params)
        return result if result else []
    
    def get_class(self, class_id: int) -> Optional[Dict]:
        """Lấy thông tin một lớp học"""
        return self._get(f"/api/classes/{class_id}")
    
    def create_class(self, class_data: dict) -> Optional[Dict]:
        """Tạo lớp học mới"""
        return self._post("/api/classes", class_data)
    
    def update_class(self, class_id: int, class_data: dict) -> Optional[Dict]:
        """Cập nhật lớp học"""
        return self._put(f"/api/classes/{class_id}", class_data)
    
    def delete_class(self, class_id: int) -> bool:
        """Xóa lớp học"""
        result = self._delete(f"/api/classes/{class_id}")
        return result is not None
    
    def get_class_students(self, class_id: int) -> List[Dict]:
        """Lấy danh sách sinh viên trong lớp"""
        result = self._get(f"/api/classes/{class_id}/students")
        return result if result else []
    
    def enroll_student(self, class_id: int, student_id: str) -> Optional[Dict]:
        """Đăng ký sinh viên vào lớp"""
        return self._post(f"/api/classes/{class_id}/students", {"student_id": student_id})
    
    def unenroll_student(self, class_id: int, student_id: str) -> bool:
        """Xóa sinh viên khỏi lớp"""
        result = self._delete(f"/api/classes/{class_id}/students/{student_id}")
        return result is not None
    
    # ========================================================================
    # SESSIONS
    # ========================================================================
    
    def get_sessions(self, class_id: int = None, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Lấy danh sách buổi học"""
        params = {"skip": skip, "limit": limit}
        if class_id:
            params["class_id"] = class_id
        result = self._get("/api/sessions", params=params)
        return result if result else []
    
    def get_session(self, session_id: int) -> Optional[Dict]:
        """Lấy thông tin một buổi học"""
        return self._get(f"/api/sessions/{session_id}")
    
    def create_session(self, session_data: dict) -> Optional[Dict]:
        """Tạo buổi học mới"""
        return self._post("/api/sessions", session_data)
    
    def update_session(self, session_id: int, session_data: dict) -> Optional[Dict]:
        """Cập nhật buổi học"""
        return self._put(f"/api/sessions/{session_id}", session_data)
    
    def delete_session(self, session_id: int) -> bool:
        """Xóa buổi học"""
        result = self._delete(f"/api/sessions/{session_id}")
        return result is not None
    
    # ========================================================================
    # ATTENDANCE
    # ========================================================================
    
    def get_attendance(self, session_id: int = None, student_id: str = None, 
                       skip: int = 0, limit: int = 1000) -> List[Dict]:
        """Lấy danh sách điểm danh"""
        params = {"skip": skip, "limit": limit}
        if session_id:
            params["session_id"] = session_id
        if student_id:
            params["student_id"] = student_id
        result = self._get("/api/attendance", params=params)
        return result if result else []
    
    def get_attendance_by_id(self, attendance_id: int) -> Optional[Dict]:
        """Lấy thông tin một bản ghi điểm danh"""
        return self._get(f"/api/attendance/{attendance_id}")
    
    def create_attendance(self, attendance_data: dict) -> Optional[Dict]:
        """Tạo bản ghi điểm danh"""
        return self._post("/api/attendance", attendance_data)
    
    def update_attendance(self, attendance_id: int, attendance_data: dict) -> Optional[Dict]:
        """Cập nhật bản ghi điểm danh"""
        return self._put(f"/api/attendance/{attendance_id}", attendance_data)
    
    def delete_attendance(self, attendance_id: int) -> bool:
        """Xóa bản ghi điểm danh"""
        result = self._delete(f"/api/attendance/{attendance_id}")
        return result is not None
    
    # ========================================================================
    # CAMERAS
    # ========================================================================
    
    def get_cameras(self, is_active: bool = None) -> List[Dict]:
        """Lấy danh sách camera"""
        params = {}
        if is_active is not None:
            params["is_active"] = is_active
        result = self._get("/api/cameras", params=params)
        return result if result else []


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Testing API Client")
    print("=" * 80)
    
    client = APIClient()
    
    # Health check
    print("\n1️⃣ Health Check...")
    if client.health_check():
        print("✅ API is healthy")
    else:
        print("❌ API is not available")
        exit(1)
    
    # Get teachers
    print("\n2️⃣ Get Teachers...")
    teachers = client.get_teachers()
    print(f"✅ Found {len(teachers)} teachers")
    for t in teachers[:3]:
        print(f"   - {t['teacher_id']}: {t['full_name']}")
    
    # Get subjects
    print("\n3️⃣ Get Subjects...")
    subjects = client.get_subjects()
    print(f"✅ Found {len(subjects)} subjects")
    for s in subjects[:3]:
        print(f"   - {s['subject_id']}: {s['subject_name']}")
    
    # Get classes
    print("\n4️⃣ Get Classes...")
    classes = client.get_classes(is_active=True)
    print(f"✅ Found {len(classes)} active classes")
    for c in classes[:3]:
        print(f"   - {c['class_id']}: {c['class_name']}")
    
    # Get sessions
    if classes:
        class_id = classes[0]['class_id']
        print(f"\n5️⃣ Get Sessions for class {class_id}...")
        sessions = client.get_sessions(class_id=class_id)
        print(f"✅ Found {len(sessions)} sessions")
        for s in sessions[:3]:
            print(f"   - {s['session_id']}: {s['session_date']} {s['start_time']}")
    
    # Get cameras
    print("\n6️⃣ Get Cameras...")
    cameras = client.get_cameras(is_active=True)
    print(f"✅ Found {len(cameras)} active cameras")
    for c in cameras[:3]:
        print(f"   - {c['device_id']}: {c['device_name']}")
    
    print("\n" + "=" * 80)
    print("✅ All API tests passed!")
    print("=" * 80)
