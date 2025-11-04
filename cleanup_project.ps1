# Cleanup Script for DACN Project
# Giữ lại chỉ những file cần thiết: ESP32-CAM code + Stream viewer

Write-Host "`n=== DỌON DẸP THƯ MỤC DACN ===" -ForegroundColor Green

# Backup trước khi xóa
$backupDate = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFolder = "backup_$backupDate"

Write-Host "`n📦 Creating backup: $backupFolder" -ForegroundColor Yellow

# Files/folders cần GIỮ LẠI
$keepItems = @(
    ".git",
    ".gitignore",
    "esp32-camera/CameraWebServer/CameraWebServer_Optimized",
    "client/view_stream_v2.py",
    "client/requirements.txt",
    "README.md",
    "dataset",  # Giữ dataset đã chụp
    "cleanup_project.ps1"
)

Write-Host "`n✅ Files/Folders sẽ GIỮ LẠI:" -ForegroundColor Green
foreach ($item in $keepItems) {
    Write-Host "   - $item" -ForegroundColor White
}

# Files/folders sẽ XÓA
$deleteItems = @(
    "old_system",
    "docs",
    "models",
    "CHANGELOG.md",
    "COMPLETION_SUMMARY.md",
    "structure_backup.txt",
    "client/analyze_quality.py",
    "client/camera_client.py",
    "client/camera_client_improved.py",
    "client/face_preprocessing.py",
    "client/face_training.py",
    "client/users.json",
    "client/utils",
    "client/README.md",
    "client/view_stream.py",
    "esp32-camera/CameraWebServer/CameraWebServer.ino.old",
    "esp32-camera/CameraWebServer/CameraWebServer_Simple",
    "esp32-camera/libraries.txt",
    "esp32-camera/wiring_diagram_oled_speaker.md"
)

Write-Host "`n⚠️  Files/Folders sẽ XÓA:" -ForegroundColor Red
foreach ($item in $deleteItems) {
    if (Test-Path $item) {
        Write-Host "   - $item" -ForegroundColor Yellow
    }
}

# Hỏi xác nhận
Write-Host "`n"
$confirm = Read-Host "Bạn có chắc muốn xóa? (yes/no)"

if ($confirm -eq "yes") {
    Write-Host "`n🗑️  Đang xóa..." -ForegroundColor Yellow
    
    foreach ($item in $deleteItems) {
        if (Test-Path $item) {
            Remove-Item -Path $item -Recurse -Force
            Write-Host "   ✅ Deleted: $item" -ForegroundColor Green
        }
    }
    
    Write-Host "`n✅ Dọn dẹp hoàn tất!" -ForegroundColor Green
    Write-Host "`n📁 Cấu trúc thư mục sau khi dọn:" -ForegroundColor Cyan
    Write-Host "   DACN/" -ForegroundColor White
    Write-Host "   ├── esp32-camera/" -ForegroundColor White
    Write-Host "   │   └── CameraWebServer/" -ForegroundColor White
    Write-Host "   │       └── CameraWebServer_Optimized/" -ForegroundColor White
    Write-Host "   │           └── CameraWebServer_Optimized.ino" -ForegroundColor Green
    Write-Host "   ├── client/" -ForegroundColor White
    Write-Host "   │   ├── view_stream_v2.py" -ForegroundColor Green
    Write-Host "   │   └── requirements.txt" -ForegroundColor Green
    Write-Host "   ├── dataset/" -ForegroundColor White
    Write-Host "   │   └── user_X/ (giữ lại)" -ForegroundColor Green
    Write-Host "   ├── .gitignore" -ForegroundColor White
    Write-Host "   └── README.md" -ForegroundColor White
    
} else {
    Write-Host "`n❌ Hủy bỏ. Không có gì bị xóa." -ForegroundColor Red
}

Write-Host ""
