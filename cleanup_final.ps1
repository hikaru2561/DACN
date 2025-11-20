<# 
===============================================================================
SCRIPT FINAL CLEANUP - XÓA DOCS CŨ VÀ SCRIPTS THỪA
An toàn - Backup trước - Confirm trước khi xóa
===============================================================================
#>

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  🧹 FINAL CLEANUP - DỌN DẸP DOCS & SCRIPTS" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra
if (-not (Test-Path "attendance_system")) {
    Write-Host "❌ LỖI: Vui lòng chạy từ thư mục gốc project!" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Bước 1: Tạo backup..." -ForegroundColor Yellow
Write-Host ""

# Create backup directory
$backupDir = "backups/final_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "  ✅ Đã tạo: $backupDir" -ForegroundColor Green

Write-Host ""
Write-Host "📋 Bước 2: Xác định file cần xóa..." -ForegroundColor Yellow
Write-Host ""

# Define files to delete
$filesToDelete = @{
    "Old Documentation (Đã gộp vào PROJECT_DOCUMENTATION.md)" = @(
        "README.md",
        "PROJECT_STRUCTURE.md",
        "SYSTEM_PIPELINE.md",
        "PHASE2_GUIDE.md",
        "PROFESSIONAL_ASSESSMENT.md",
        "REFACTORING_PLAN.md",
        "PROJECT_STATUS.md",
        "attendance_system/backend/README.md",
        "attendance_system/desktop/README.md",
        "docs/MODEL_INFO.md",
        "esp32-camera/README.md"
    )
    
    "Unnecessary Scripts (Đã chạy xong)" = @(
        "refactor_backend_phase2.ps1",
        "refactor_desktop_phase2.ps1",
        "refactor_master_phase2.ps1",
        "refactor_phase3_desktop_imports.ps1",
        "cleanup_old_files.ps1"
    )
}

# Calculate sizes and display
$totalSize = 0
$totalFiles = 0

foreach ($category in $filesToDelete.GetEnumerator()) {
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
            Write-Host "    ⊘ $file (không tìm thấy)" -ForegroundColor DarkGray
        }
    }
    Write-Host ""
}

Write-Host "📊 TỔNG KẾT:" -ForegroundColor Cyan
Write-Host "  Số file: $totalFiles" -ForegroundColor White
Write-Host "  Tổng dung lượng: " -NoNewline -ForegroundColor White
Write-Host ("{0:N2} KB" -f ($totalSize / 1KB)) -ForegroundColor Yellow
Write-Host ""

# Confirm
Write-Host "⚠️  CẢNH BÁO:" -ForegroundColor Red
Write-Host "  • Tất cả file trên sẽ bị XÓA." -ForegroundColor Yellow
Write-Host "  • PROJECT_DOCUMENTATION.md sẽ được GIỮ LẠI." -ForegroundColor Yellow
Write-Host "  • Backup sẽ được tạo tại $backupDir" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Bạn có chắc muốn XÓA? (yes để xác nhận)"

if ($confirmation -ne "yes") {
    Write-Host ""
    Write-Host "❌ Đã hủy. Không có thay đổi." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "📦 Bước 3: Backup & Xóa..." -ForegroundColor Yellow
Write-Host ""

$deletedCount = 0
$errorCount = 0

foreach ($category in $filesToDelete.GetEnumerator()) {
    foreach ($file in $category.Value) {
        if (Test-Path $file) {
            try {
                # Backup
                $destPath = Join-Path $backupDir $file
                $destDir = Split-Path $destPath -Parent
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Copy-Item $file $destPath -Force
                
                # Delete
                Remove-Item $file -Force
                Write-Host "  ✅ Đã xóa: $file" -ForegroundColor Green
                $deletedCount++
            } catch {
                Write-Host "  ❌ Lỗi: $file - $($_.Exception.Message)" -ForegroundColor Red
                $errorCount++
            }
        }
    }
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  🎉 HOÀN THÀNH FINAL CLEANUP" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Đã xóa: $deletedCount files" -ForegroundColor Green
Write-Host "💾 Backup: $backupDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Project bây giờ rất gọn gàng!" -ForegroundColor Green
Write-Host "   Chỉ còn lại PROJECT_DOCUMENTATION.md và Source Code." -ForegroundColor Green
Write-Host ""
