"""
API Client - Kết nối với Backend API Access Control
"""
import requests
from typing import List, Dict, Optional

class APIClient:
    """Client để gọi Backend REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: dict = None) -> dict:
        """GET request"""
        try:
            # Xử lý endpoint có hoặc không có / ở đầu
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint
            
            # Nếu endpoint đã có /api thì giữ nguyên, nếu chưa thì thêm vào (tùy backend config)
            # Ở đây backend config là /api/v1 hoặc /api. Giả sử endpoint truyền vào là "users/" -> "/api/users/"
            # Tuy nhiên để linh hoạt, ta sẽ quy ước endpoint truyền vào phải đầy đủ sau base_url/api
            # Ví dụ: get("users/") -> http://localhost:8000/api/users/
            
            url = f"{self.base_url}/api{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
    
    def post(self, endpoint: str, data: dict) -> dict:
        """POST request"""
        try:
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint
                
            url = f"{self.base_url}/api{endpoint}"
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
    
    def put(self, endpoint: str, data: dict) -> dict:
        """PUT request"""
        try:
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint
                
            url = f"{self.base_url}/api{endpoint}"
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None
            
    def delete(self, endpoint: str) -> dict:
        """DELETE request"""
        try:
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint
                
            url = f"{self.base_url}/api{endpoint}"
            response = self.session.delete(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return None

    def health_check(self) -> bool:
        """Kiểm tra kết nối API"""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            return response.status_code == 200
        except:
            return False
