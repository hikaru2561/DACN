# 📚 API Documentation

## 🎯 Tổng quan
RESTful API cho hệ thống điểm danh bằng nhận dạng khuôn mặt.

**Base URL**: `http://localhost:5000`

## 🔧 Endpoints

### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "face_recognition": "disabled (test mode)",
  "timestamp": "2025-10-17T14:55:22.535472"
}
```

### 2. Điểm danh
```http
POST /checkin
Content-Type: application/json

{
  "image": "base64_encoded_image"
}
```
**Response:**
```json
{
  "success": true,
  "message": "Điểm danh thành công (test mode)",
  "user": {
    "user_id": 1,
    "name": "Nguyễn Văn A",
    "student_code": "SV001",
    "confidence": 0.923
  },
  "log_id": 1
}
```

### 3. Đăng ký người dùng
```http
POST /register
Content-Type: application/json

{
  "name": "Tên người dùng",
  "student_code": "SV001",
  "email": "email@example.com",
  "phone": "0123456789"
}
```
**Response:**
```json
{
  "success": true,
  "message": "Đăng ký thành công (test mode)",
  "user_id": 1,
  "embedding_id": 1
}
```

### 4. Danh sách người dùng
```http
GET /users
```
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "user_id": 1,
      "name": "Nguyễn Văn A",
      "student_code": "SV001",
      "email": "nguyenvana@email.com",
      "phone": "0123456789",
      "is_active": true,
      "created_at": "2025-10-17T13:20:46Z"
    }
  ],
  "count": 1
}
```

### 5. Lịch sử điểm danh
```http
GET /attendance?user_id=1&limit=10
```
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "log_id": 1,
      "user_id": 1,
      "timestamp": "2025-10-17T14:55:22Z",
      "confidence": 0.923,
      "status": "present"
    }
  ],
  "count": 1
}
```

### 6. Thống kê
```http
GET /stats
```
**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 3,
    "total_checkins": 5,
    "today_checkins": 2,
    "avg_confidence": 0.89
  }
}
```

## 🔧 Cài đặt

### 1. Cài đặt dependencies
```bash
cd python-server
pip install -r requirements.txt
```

### 2. Chạy server
```bash
python app_simple.py
```

### 3. Test API
```bash
curl http://localhost:5000/health
```

## 📊 Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

## 🚨 Error Handling

```json
{
  "error": "Error message",
  "details": "Detailed error information"
}
```

## 🔐 Authentication
Hiện tại API không yêu cầu authentication. Trong production nên thêm JWT token.

## 📈 Rate Limiting
Không có rate limiting. Trong production nên thêm để bảo vệ server.

## 🧪 Testing

### Test với curl
```bash
# Health check
curl http://localhost:5000/health

# Checkin
curl -X POST http://localhost:5000/checkin \
  -H "Content-Type: application/json" \
  -d '{"image":"test"}'

# Users
curl http://localhost:5000/users
```

### Test với Python
```python
import requests

# Health check
response = requests.get('http://localhost:5000/health')
print(response.json())

# Checkin
response = requests.post('http://localhost:5000/checkin', 
                        json={'image': 'test'})
print(response.json())
```