# ============================================================================
# CLEANUP SCRIPT - Dọn dẹp file/folder cũ không dùng
# ============================================================================
# Tạo: November 7, 2025
# Mục đích: Xóa các file thử nghiệm, code cũ, backup không cần thiết

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  🧹 CLEANUP SCRIPT - Dọn dẹp thư mục DACN" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$itemsToDelete = @()

# ============================================================================
# 1. CLIENT FOLDER - Code thử nghiệm cũ (ĐÃ TÍCH HỢP VÀO DESKTOP APP)
# ============================================================================
Write-Host "📁 Checking CLIENT folder..." -ForegroundColor Yellow

$clientDebugFiles = @(
    "d:\HUTECH\DACN\client\compare_histeq_vs_clahe.py",
    "d:\HUTECH\DACN\client\debug_compare_preprocessing.py",
    "d:\HUTECH\DACN\client\debug_preprocessing.py",
    "d:\HUTECH\DACN\client\debug_test_similarity.py",
    "d:\HUTECH\DACN\client\direct_face_comparison.py",
    "d:\HUTECH\DACN\client\face_recognition_system.py",
    "d:\HUTECH\DACN\client\insightface_onnx.py",
    "d:\HUTECH\DACN\client\test.py",
    "d:\HUTECH\DACN\client\test_crop_accuracy.py",
    "d:\HUTECH\DACN\client\view_preprocessing_result.py",
    "d:\HUTECH\DACN\client\live.py"
)

foreach ($file in $clientDebugFiles) {
    if (Test-Path $file) {
        $itemsToDelete += [PSCustomObject]@{
            Type = "File"
            Path = $file
            Reason = "Debug/test file - Chức năng đã tích hợp vào Desktop App"
        }
    }
}

# Client folder models (nếu có)
if (Test-Path "d:\HUTECH\DACN\client\models") {
    $itemsToDelete += [PSCustomObject]@{
        Type = "Folder"
        Path = "d:\HUTECH\DACN\client\models"
        Reason = "Model cache - InsightFace tự download"
    }
}

# Client pycache
if (Test-Path "d:\HUTECH\DACN\client\__pycache__") {
    $itemsToDelete += [PSCustomObject]@{
        Type = "Folder"
        Path = "d:\HUTECH\DACN\client\__pycache__"
        Reason = "Python cache - Tự động tạo lại"
    }
}

# ============================================================================
# 2. FACE_RECOGNITION_V2 - Code thử nghiệm cũ (THAY THẾ BỞI attendance_system)
# ============================================================================
Write-Host "📁 Checking FACE_RECOGNITION_V2 folder..." -ForegroundColor Yellow

if (Test-Path "d:\HUTECH\DACN\face_recognition_v2") {
    $itemsToDelete += [PSCustomObject]@{
        Type = "Folder"
        Path = "d:\HUTECH\DACN\face_recognition_v2"
        Reason = "Version cũ - Đã thay thế bởi attendance_system"
    }
}

# ============================================================================
# 3. ARCHIVE - Dataset cũ (ĐÃ BACKUP)
# ============================================================================
Write-Host "📁 Checking ARCHIVE folder..." -ForegroundColor Yellow

if (Test-Path "d:\HUTECH\DACN\archive.zip") {
    $itemsToDelete += [PSCustomObject]@{
        Type = "File"
        Path = "d:\HUTECH\DACN\archive.zip"
        Reason = "Archive đã nén - Giữ folder gốc"
    }
}

# Không xóa archive folder vì có thể cần dataset mẫu

# ============================================================================
# 4. CLEANUP SCRIPTS CŨ
# ============================================================================
Write-Host "📁 Checking old cleanup scripts..." -ForegroundColor Yellow

if (Test-Path "d:\HUTECH\DACN\cleanup_project.ps1") {
    $itemsToDelete += [PSCustomObject]@{
        Type = "File"
        Path = "d:\HUTECH\DACN\cleanup_project.ps1"
        Reason = "Script cũ - Thay thế bởi cleanup_old_files.ps1"
    }
}

# ============================================================================
# 5. README FILES
# ============================================================================
Write-Host "📁 Checking README files..." -ForegroundColor Yellow

if ((Test-Path "d:\HUTECH\DACN\README.md") -and (Test-Path "d:\HUTECH\DACN\README_NEW.md")) {
    $itemsToDelete += [PSCustomObject]@{
        Type = "File"
        Path = "d:\HUTECH\DACN\README.md"
        Reason = "README cũ - Đã có README_NEW.md"
    }
}

# ============================================================================
# 6. DATASET - Ảnh cũ với preprocessing SAI
# ============================================================================
Write-Host "📁 Checking DATASET folder..." -ForegroundColor Yellow

if (Test-Path "d:\HUTECH\DACN\dataset\processed\2280602549") {
    $itemsToDelete += [PSCustomObject]@{
        Type = "Folder"
        Path = "d:\HUTECH\DACN\dataset\processed\2280602549"
        Reason = "Ảnh cũ với preprocessing sai - Cần chụp lại"
    }
}

if (Test-Path "d:\HUTECH\DACN\dataset\face_embeddings.pkl") {
    $itemsToDelete += [PSCustomObject]@{
        Type = "File"
        Path = "d:\HUTECH\DACN\dataset\face_embeddings.pkl"
        Reason = "Embeddings cũ - Cần training lại"
    }
}

# ============================================================================
# HIỂN THỊ DANH SÁCH
# ============================================================================
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  📋 ITEMS TO DELETE ($($itemsToDelete.Count) items)" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

if ($itemsToDelete.Count -eq 0) {
    Write-Host "✅ No items to delete. Project is clean!" -ForegroundColor Green
    exit 0
}

$totalSize = 0
foreach ($item in $itemsToDelete) {
    $size = 0
    if ($item.Type -eq "File" -and (Test-Path $item.Path)) {
        $size = (Get-Item $item.Path).Length
        $totalSize += $size
    } elseif ($item.Type -eq "Folder" -and (Test-Path $item.Path)) {
        $size = (Get-ChildItem $item.Path -Recurse -File | Measure-Object -Property Length -Sum).Sum
        $totalSize += $size
    }
    
    $sizeStr = if ($size -gt 1MB) {
        "{0:N2} MB" -f ($size / 1MB)
    } elseif ($size -gt 1KB) {
        "{0:N2} KB" -f ($size / 1KB)
    } else {
        "{0} bytes" -f $size
    }
    
    Write-Host "[$($item.Type)] " -NoNewline -ForegroundColor Yellow
    Write-Host "$($item.Path)" -ForegroundColor White
    Write-Host "  └─ Reason: $($item.Reason)" -ForegroundColor Gray
    Write-Host "  └─ Size: $sizeStr" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Total size: " -NoNewline
Write-Host ("{0:N2} MB" -f ($totalSize / 1MB)) -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# XÁC NHẬN XÓA
# ============================================================================
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "⚠️  WARNING: This action CANNOT be undone!" -ForegroundColor Red
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$confirmation = Read-Host "Do you want to DELETE these items? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host ""
    Write-Host "❌ Cleanup cancelled." -ForegroundColor Yellow
    exit 0
}

# ============================================================================
# THỰC HIỆN XÓA
# ============================================================================
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  🗑️  DELETING..." -ForegroundColor Red
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($item in $itemsToDelete) {
    try {
        if (Test-Path $item.Path) {
            Remove-Item -Path $item.Path -Recurse -Force -ErrorAction Stop
            Write-Host "✅ Deleted: $($item.Path)" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "⚠️  Not found: $($item.Path)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Failed: $($item.Path)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

# ============================================================================
# KẾT QUẢ
# ============================================================================
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  ✅ CLEANUP COMPLETED" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Success: $successCount items" -ForegroundColor Green
Write-Host "Failed:  $failCount items" -ForegroundColor Red
Write-Host "Freed:   " -NoNewline
Write-Host ("{0:N2} MB" -f ($totalSize / 1MB)) -ForegroundColor Cyan
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  📁 REMAINING STRUCTURE" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "d:\HUTECH\DACN\" -ForegroundColor White
Write-Host "  ├── attendance_system/      ✅ Main application" -ForegroundColor Green
Write-Host "  │   ├── backend/            ✅ FastAPI server" -ForegroundColor Green
Write-Host "  │   └── desktop/            ✅ Tkinter UI" -ForegroundColor Green
Write-Host "  ├── dataset/                ✅ Face images & embeddings" -ForegroundColor Green
Write-Host "  ├── archive/                📦 Old dataset (backup)" -ForegroundColor Yellow
Write-Host "  ├── client/                 📝 Capture tools (keep 3 files)" -ForegroundColor Yellow
Write-Host "  │   ├── capture_faces_mediapipe.py  ✅ MediaPipe capture" -ForegroundColor Green
Write-Host "  │   ├── capture_faces_xga.py        ✅ XGA capture" -ForegroundColor Green
Write-Host "  │   └── view_stream_xga.py          ✅ Stream viewer" -ForegroundColor Green
Write-Host "  ├── esp32-camera/           📡 ESP32 firmware" -ForegroundColor Cyan
Write-Host "  ├── db.sql                  🗄️  Database schema" -ForegroundColor Cyan
Write-Host "  └── MODEL_ARCHITECTURE.md   📚 Documentation" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# NEXT STEPS
# ============================================================================
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  🚀 NEXT STEPS" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Chụp lại ảnh sinh viên (ảnh GỐC, không preprocessing):" -ForegroundColor White
Write-Host "   cd attendance_system\desktop" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host "   → Quản lý Sinh viên → 📷 Lấy ảnh sinh viên" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Training embeddings:" -ForegroundColor White
Write-Host "   → Click '🔄 Training Data'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test recognition:" -ForegroundColor White
Write-Host "   → Module Điểm danh → ▶️ Bắt đầu" -ForegroundColor Gray
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
