import requests
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Cấu hình IP Camera (Nên để trong DB system_settings, tạm thời hardcode)
# Cấu hình IP Camera (Nên để trong DB system_settings, tạm thời hardcode)
ESP32_IP = "192.168.1.231" 

class DoorControlResponse(BaseModel):
    success: bool
    message: str

@router.post("/open", response_model=DoorControlResponse)
def open_door() -> Any:
    """
    Send command to ESP32 to open the door.
    """
    try:
        url = f"http://{ESP32_IP}/open"
        # Timeout ngắn để tránh treo server
        response = requests.get(url, timeout=2.0) 
        
        if response.status_code == 200:
            return {"success": True, "message": "Door opening signal sent"}
        else:
            raise HTTPException(status_code=502, detail=f"ESP32 returned {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to ESP32: {str(e)}")

@router.get("/open", response_model=DoorControlResponse)
def open_door_get() -> Any:
    """
    GET version - Same as POST, for compatibility
    """
    return open_door()
