"""
ESP32-CAM Stream Viewer - XGA 1024×768 @ 100 FPS
Synchronized with ESP32 XGA_FLUSH_v7.0 firmware
Ultra low latency with aggressive frame skipping
"""

import cv2
import numpy as np
import requests
import sys
import time
from threading import Thread

# ==========================================
# CONFIGURATION - Must match ESP32 settings
# ==========================================
ESP32_CAM_IP = "192.168.1.12"
STREAM_URL = f"http://{ESP32_CAM_IP}/stream"

# Expected from ESP32:
# - Resolution: XGA 1024×768
# - JPEG Quality: 12 (~30-35 KB/frame)
# - FPS: ~100 (delay 10ms)
# - Mode: CAMERA_GRAB_LATEST

class ESP32StreamViewer:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.frame = None
        self.stopped = False
        self.connected = False
        
    def start(self):
        """Start stream reading thread"""
        Thread(target=self.update, daemon=True).start()
        return self
        
    def update(self):
        """Main stream reading loop - ULTRA LOW LATENCY"""
        try:
            print(f"🔄 Connecting to {self.stream_url}...")
            
            # ⚡ Force fresh connection - no cache
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'ESP32-XGA-Viewer-v7',
                'Connection': 'close',  # Force new connection every time
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            })
            
            # ⚡ Connect with aggressive timeout
            response = session.get(
                self.stream_url, 
                stream=True, 
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                self.stopped = True
                return
                
            # Connection info
            print("✅ Connected successfully!")
            print(f"📡 Server: {response.headers.get('Server', 'Unknown')}")
            print(f"🔗 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print("⚡ XGA 1024×768 @ 100 FPS mode active")
            self.connected = True
            
            # Stream reading variables
            bytes_data = bytes()
            frame_count = 0
            skip_count = 0
            first_frame_verified = False
            last_report_time = time.time()
            
            # ⚡ Main streaming loop
            for chunk in response.iter_content(chunk_size=8192):  # 8KB chunks for XGA
                if self.stopped:
                    break
                    
                bytes_data += chunk
                
                # ⚡ AGGRESSIVE BUFFER MANAGEMENT for XGA
                # Keep only last 60KB (~2 XGA frames max)
                if len(bytes_data) > 60000:
                    # Find last JPEG start marker
                    last_start = bytes_data.rfind(b'\xff\xd8')
                    if last_start > 0:
                        bytes_data = bytes_data[last_start:]
                        skip_count += 1
                
                # Parse JPEG boundaries
                a = bytes_data.find(b'\xff\xd8')  # JPEG start (SOI)
                b = bytes_data.find(b'\xff\xd9')  # JPEG end (EOI)
                
                if a != -1 and b != -1:
                    # Extract complete JPEG
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    try:
                        # Decode JPEG to frame
                        frame = cv2.imdecode(
                            np.frombuffer(jpg, dtype=np.uint8), 
                            cv2.IMREAD_COLOR
                        )
                        
                        if frame is not None:
                            # ✅ VERIFY FIRST FRAME
                            if not first_frame_verified:
                                h, w = frame.shape[:2]
                                print(f"\n📊 First Frame Analysis:")
                                print(f"   Resolution: {w}×{h}")
                                print(f"   JPEG Size: {len(jpg):,} bytes")
                                
                                if w == 1024 and h == 768:
                                    print("   ✅ XGA 1024×768 CONFIRMED!")
                                elif w == 1600 and h == 1200:
                                    print("   ⚠️  WARNING: UXGA 1600×1200 detected!")
                                    print("   → ESP32 buffer not flushed properly")
                                    print("   → Try: Power cycle ESP32-CAM")
                                else:
                                    print(f"   ℹ️  Resolution: {w}×{h}")
                                
                                first_frame_verified = True
                                print()
                            
                            # ⚡ Direct frame update (no queue for lowest latency)
                            self.frame = frame
                            frame_count += 1
                            
                            # Performance reporting every 5 seconds
                            current_time = time.time()
                            if current_time - last_report_time > 5.0:
                                elapsed = current_time - last_report_time
                                fps = frame_count / elapsed
                                skip_ratio = (skip_count / max(frame_count, 1)) * 100
                                
                                print(f"📊 Performance: {fps:.1f} FPS | "
                                      f"Frames: {frame_count} | "
                                      f"Skipped: {skip_count} ({skip_ratio:.0f}%)")
                                
                                frame_count = 0
                                skip_count = 0
                                last_report_time = current_time
                                
                    except Exception as e:
                        # Skip corrupted frames
                        continue
                    
        except requests.exceptions.Timeout:
            print("\n❌ Connection timeout!")
            print("   ESP32-CAM not responding")
        except requests.exceptions.ConnectionError:
            print("\n❌ Connection error!")
            print("   Cannot reach ESP32-CAM")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stopped = True
            self.connected = False
            
    def read(self):
        """Get current frame"""
        return self.frame
        
    def stop(self):
        """Stop streaming"""
        self.stopped = True


def main():
    """Main application"""
    print("=" * 70)
    print("  ESP32-CAM XGA STREAM VIEWER")
    print("  Synchronized with XGA_FLUSH_v7.0 firmware")
    print("=" * 70)
    print(f"📡 Stream URL: {STREAM_URL}")
    print(f"🎯 Expected: XGA 1024×768 @ ~100 FPS")
    print(f"👁️  Press 'q' or ESC to quit")
    print("=" * 70)
    
    # Initialize viewer
    viewer = ESP32StreamViewer(STREAM_URL)
    viewer.start()
    
    # Wait for connection
    timeout = 20
    start_time = time.time()
    
    print("\n⏳ Waiting for connection...")
    while not viewer.connected and not viewer.stopped:
        time.sleep(0.1)
        if time.time() - start_time > timeout:
            print(f"\n❌ Timeout after {timeout} seconds")
            print("\n📋 Troubleshooting:")
            print(f"   1. Check ESP32-CAM is powered on")
            print(f"   2. Verify IP address: {ESP32_CAM_IP}")
            print(f"   3. Check Serial Monitor for errors")
            print(f"   4. Try: ping {ESP32_CAM_IP}")
            print(f"   5. Try browser: http://{ESP32_CAM_IP}/capture")
            viewer.stop()
            return
    
    if viewer.stopped:
        print("\n❌ Failed to connect to ESP32-CAM")
        return
    
    print("\n📺 Displaying stream...\n")
    
    # Display loop
    frame_count = 0
    fps_counter = 0
    fps_start = time.time()
    display_fps = 0
    
    while not viewer.stopped:
        frame = viewer.read()
        
        if frame is None:
            time.sleep(0.001)
            continue
        
        frame_count += 1
        fps_counter += 1
        
        # Calculate display FPS
        if fps_counter >= 30:
            elapsed = time.time() - fps_start
            display_fps = fps_counter / elapsed
            fps_counter = 0
            fps_start = time.time()
        
        # Add overlay info
        h, w = frame.shape[:2]
        
        # Header
        cv2.putText(frame, f"ESP32-CAM XGA Stream - v7.0", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Stats
        cv2.putText(frame, f"Frame: {frame_count}", (10, 65), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Display FPS: {display_fps:.1f}", (10, 95), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Resolution: {w}×{h}", (10, 125), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Mode indicator
        mode_color = (0, 255, 255) if w == 1024 and h == 768 else (0, 0, 255)
        mode_text = "XGA Mode ✓" if w == 1024 and h == 768 else f"Wrong Resolution!"
        cv2.putText(frame, mode_text, (10, 155), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)
        
        # Footer
        cv2.putText(frame, "Press 'q' or ESC to quit", (10, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Display frame
        cv2.imshow('ESP32-CAM XGA Stream', frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            print("\n👋 Closing stream...")
            break
    
    # Cleanup
    viewer.stop()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 70)
    print("✅ Stream closed successfully!")
    print(f"📊 Total frames displayed: {frame_count:,}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()
        sys.exit(1)
