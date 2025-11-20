"""
Quick Camera URL Updater
Script nhanh để cập nhật URL camera mà không cần mở config manager
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config import CAMERA_CONFIG
import re

def update_camera_url(new_url):
    """Cập nhật URL camera trong config file"""
    config_file = os.path.join(os.path.dirname(__file__), "config.py")
    
    # Read file
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace URL
    content = re.sub(
        r'"stream_url":\s*"[^"]*"',
        f'"stream_url": "{new_url}"',
        content
    )
    
    # Write back
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Đã cập nhật camera URL: {new_url}")
    print("⚠️ Khởi động lại ứng dụng để áp dụng!")


if __name__ == "__main__":
    print("=" * 60)
    print("📷 CẬP NHẬT URL CAMERA")
    print("=" * 60)
    print(f"\nURL hiện tại: {CAMERA_CONFIG['stream_url']}")
    print("\nNhập URL mới (hoặc Enter để giữ nguyên):")
    print("VD: http://192.168.1.169/stream")
    print("-" * 60)
    
    new_url = input("URL mới: ").strip()
    
    if not new_url:
        print("❌ Hủy bỏ")
        sys.exit(0)
    
    if not new_url.startswith("http"):
        print("❌ URL phải bắt đầu với http:// hoặc https://")
        sys.exit(1)
    
    try:
        update_camera_url(new_url)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)
