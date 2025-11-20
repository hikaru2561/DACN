<# 
===============================================================================
SCRIPT CLEANUP - XÓA FILE CŨ VÀ RÁC
An toàn - Backup trước - Confirm trước khi xóa
===============================================================================
#>

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  🗑️  CLEANUP PROJECT - XÓA FILE CŨ VÀ RÁC" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra
if (-not (Test-Path "attendance_system")) {
    Write-Host "❌ LỖI: Vui lòng chạy từ thư mục gốc project!" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Bước 1: Tạo backup trước khi xóa..." -ForegroundColor Yellow
Write-Host ""

# Create backup directory
$backupDir = "backups/before_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "  ✅ Đã tạo: $backupDir" -ForegroundColor Green

Write-Host ""
Write-Host "📋 Bước 2: Liệt kê file sẽ XÓA..." -ForegroundColor Yellow
Write-Host ""

# Define files to delete
$filesToDelete = @{
    "Desktop - Old Modules" = @(
        "attendance_system/desktop/main.py",
        "attendance_system/desktop/api_client.py",
        "attendance_system/desktop/config.py",
        "attendance_system/desktop/student_module_new.py",
        "attendance_system/desktop/teacher_module.py",
        "attendance_system/desktop/subject_module.py",
        "attendance_system/desktop/class_module.py",
        "attendance_system/desktop/session_module.py",
        "attendance_system/desktop/attendance_module.py",
        "attendance_system/desktop/attendance_session_module.py",
        "attendance_system/desktop/attendance_live_module.py",
        "attendance_system/desktop/attendance_history_module.py",
        "attendance_system/desktop/camera_management_module.py",
        "attendance_system/desktop/camera_capture_module.py",
        "attendance_system/desktop/report_module.py",
        "attendance_system/desktop/build_embeddings.py"
    )
    
    "Backend - Old Files (⚠️ ĐANG DÙNG)" = @(
        # "attendance_system/backend/main.py",      # ⚠️ Comment out - đang chạy!
        # "attendance_system/backend/models.py",    # ⚠️ Comment out - đang dùng!
        # "attendance_system/backend/schemas.py",   # ⚠️ Comment out - đang dùng!
        # "attendance_system/backend/database.py"   # ⚠️ Comment out - đang dùng!
    )
    
    "Refactor Scripts (có thể xóa)" = @(
        "refactor_backend_phase1.ps1",
        "refactor_backend_phase2.ps1",
        "refactor_desktop_phase1.ps1",
        "refactor_desktop_phase2.ps1",
        "refactor_master.ps1",
        "refactor_master_phase2.ps1",
        "refactor_phase3_desktop_imports.ps1",
        "cleanup_project.ps1"
    )
    
    "Temporary Files" = @(
        "project_structure_full.txt"
    )
    
    "Backup Files (giữ lại)" = @(
        # "attendance_system/desktop/app/_main_old.py",    # GIỮ
        # "attendance_system/desktop/app/_config_old.py",  # GIỮ
        # "attendance_system/backend/app/_main_old.py",    # GIỮ
        # "attendance_system/backend/app/_models_old.py",  # GIỮ
        # "attendance_system/backend/app/_schemas_old.py"  # GIỮ
    )
}

# Calculate sizes and display
$totalSize = 0
$totalFiles = 0

foreach ($category in $filesToDelete.GetEnumerator()) {
    if ($category.Value.Count -eq 0) {
        continue
    }
    
    Write-Host "  📁 $($category.Key):" -ForegroundColor Cyan
    
    foreach ($file in $category.Value) {
        if (Test-Path $file) {
            $size = (Get-Item $file).Length
            $totalSize += $size
            $totalFiles++
            
            $sizeStr = if ($size -lt 1KB) {
                "$size bytes"
            } elseif ($size -lt 1MB) {
                "{0:N2} KB" -f ($size / 1KB)
            } else {
                "{0:N2} MB" -f ($size / 1MB)
            }
            
            Write-Host "    ✓ $file" -ForegroundColor White -NoNewline
            Write-Host " ($sizeStr)" -ForegroundColor Gray
        } else {
            Write-Host "    ⊘ $file (không tồn tại)" -ForegroundColor DarkGray
        }
    }
    Write-Host ""
}

Write-Host "📊 TỔNG KẾT:" -ForegroundColor Cyan
Write-Host "  Số file: $totalFiles" -ForegroundColor White
Write-Host "  Tổng dung lượng: " -NoNewline -ForegroundColor White
Write-Host ("{0:N2} MB" -f ($totalSize / 1MB)) -ForegroundColor Yellow
Write-Host ""

# Confirm
Write-Host "⚠️  CẢNH BÁO:" -ForegroundColor Red
Write-Host ""
Write-Host "  • File sẽ được backup trước khi xóa" -ForegroundColor Yellow
Write-Host "  • Backend files CŨ VẪN GIỮ (vì đang chạy)" -ForegroundColor Yellow
Write-Host "  • Backup files (_*_old.py) VẪN GIỮ" -ForegroundColor Yellow
Write-Host "  • CHỈ XÓA file Desktop modules cũ + scripts" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Bạn có chắc muốn XÓA? (yes để xác nhận)"

if ($confirmation -ne "yes") {
    Write-Host ""
    Write-Host "❌ Đã hủy. Không có thay đổi." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "📦 Bước 3: Backup files..." -ForegroundColor Yellow
Write-Host ""

$backedUpCount = 0

foreach ($category in $filesToDelete.GetEnumerator()) {
    foreach ($file in $category.Value) {
        if (Test-Path $file) {
            try {
                $destPath = Join-Path $backupDir $file
                $destDir = Split-Path $destPath -Parent
                
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                
                Copy-Item $file $destPath -Force
                $backedUpCount++
            } catch {
                Write-Host "  ⚠️  Lỗi backup: $file" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host "  ✅ Đã backup: $backedUpCount files" -ForegroundColor Green

Write-Host ""
Write-Host "🗑️  Bước 4: Xóa files..." -ForegroundColor Yellow
Write-Host ""

$deletedCount = 0
$errorCount = 0

# Only delete Desktop old modules and scripts
$categoriesToDelete = @("Desktop - Old Modules", "Refactor Scripts (có thể xóa)", "Temporary Files")

foreach ($categoryName in $categoriesToDelete) {
    $category = $filesToDelete[$categoryName]
    
    foreach ($file in $category) {
        if (Test-Path $file) {
            try {
                Remove-Item $file -Force
                Write-Host "  ✅ Đã xóa: $file" -ForegroundColor Green
                $deletedCount++
            } catch {
                Write-Host "  ❌ Lỗi xóa: $file" -ForegroundColor Red
                $errorCount++
            }
        }
    }
}

Write-Host ""
Write-Host "🧹 Bước 5: Dọn dẹp __pycache__..." -ForegroundColor Yellow
Write-Host ""

$pycacheDirs = Get-ChildItem -Path "attendance_system" -Recurse -Directory -Filter "__pycache__"
$pycacheCount = 0

foreach ($dir in $pycacheDirs) {
    try {
        Remove-Item $dir.FullName -Recurse -Force
        Write-Host "  ✅ Đã xóa: $($dir.FullName)" -ForegroundColor Green
        $pycacheCount++
    } catch {
        Write-Host "  ⚠️  Lỗi xóa: $($dir.FullName)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  📊 KẾT QUẢ" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Đã backup: $backedUpCount files → $backupDir" -ForegroundColor Green
Write-Host "✅ Đã xóa: $deletedCount files" -ForegroundColor Green
Write-Host "✅ Đã xóa: $pycacheCount __pycache__ folders" -ForegroundColor Green
Write-Host "❌ Lỗi: $errorCount files" -ForegroundColor Red
Write-Host ""

if ($errorCount -eq 0) {
    Write-Host "🎉 HOÀN THÀNH! Project đã được dọn dẹp." -ForegroundColor Green
    Write-Host ""
    Write-Host "📂 CẤU TRÚC SAU KHI DỌN DẸP:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "attendance_system/" -ForegroundColor White
    Write-Host "├── backend/" -ForegroundColor White
    Write-Host "│   ├── main.py              ⚠️  (CŨ - vẫn giữ vì đang chạy)" -ForegroundColor Yellow
    Write-Host "│   ├── models.py            ⚠️  (CŨ - vẫn giữ vì đang dùng)" -ForegroundColor Yellow
    Write-Host "│   ├── schemas.py           ⚠️  (CŨ - vẫn giữ vì đang dùng)" -ForegroundColor Yellow
    Write-Host "│   └── app/                 ✅ (MỚI - sẵn sàng)" -ForegroundColor Green
    Write-Host "│" -ForegroundColor White
    Write-Host "└── desktop/" -ForegroundColor White
    Write-Host "    ├── app/                 ✅ (MỚI - đã dọn sạch)" -ForegroundColor Green
    Write-Host "    └── [old files]          ❌ (ĐÃ XÓA)" -ForegroundColor Green
    Write-Host ""
    Write-Host "💾 Backup location: $backupDir" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 BƯỚC TIẾP THEO:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Commit changes:" -ForegroundColor White
    Write-Host "   git add ." -ForegroundColor Gray
    Write-Host "   git status  # Xem file đã xóa" -ForegroundColor Gray
    Write-Host "   git commit -m 'refactor: cleanup old files, keep new structure'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Test Desktop app:" -ForegroundColor White
    Write-Host "   cd attendance_system/desktop" -ForegroundColor Gray
    Write-Host "   python -m app.main  # Hoặc python main.py (nếu còn backup)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Sau khi test OK → Có thể xóa backend old files:" -ForegroundColor White
    Write-Host "   (Chỉnh sửa script này, uncomment backend files)" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "⚠️  Hoàn thành với $errorCount lỗi." -ForegroundColor Yellow
}

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
