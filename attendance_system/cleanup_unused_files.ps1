# ============================================================================
# CLEANUP UNUSED FILES IN ATTENDANCE_SYSTEM
# Script dọn dẹp các file không còn sử dụng trong hệ thống
# ============================================================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  CLEANUP UNUSED FILES" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Đường dẫn thư mục gốc
$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopPath = Join-Path $rootPath "desktop"

# Tạo thư mục backup
$backupPath = Join-Path $rootPath "backup_unused_files"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFolder = Join-Path $backupPath $timestamp

if (-not (Test-Path $backupPath)) {
    New-Item -ItemType Directory -Path $backupPath | Out-Null
}
New-Item -ItemType Directory -Path $backupFolder | Out-Null

Write-Host "📁 Backup folder: $backupFolder" -ForegroundColor Yellow
Write-Host ""

# ============================================================================
# DANH SÁCH FILE KHÔNG CÒN SỬ DỤNG
# ============================================================================

$unusedFiles = @(
    # File cũ đã được thay thế bởi student_module_new.py
    @{
        Path = "desktop\student_module.py"
        Reason = "Đã được thay thế bởi student_module_new.py"
        Status = "DEPRECATED"
    },
    
    # Config manager không được import trong main.py
    @{
        Path = "desktop\config_manager.py"
        Reason = "Không được sử dụng (config đã tích hợp vào config.py)"
        Status = "UNUSED"
    },
    
    # Update camera script đơn giản, không cần thiết
    @{
        Path = "desktop\update_camera.py"
        Reason = "Không cần thiết (có thể cập nhật trực tiếp trong config.py)"
        Status = "UNUSED"
    },
    
    # Thư mục temp rỗng
    @{
        Path = "temp"
        Reason = "Thư mục rỗng, không sử dụng"
        Status = "EMPTY"
    }
)

# ============================================================================
# HIỂN thị DANH SÁCH
# ============================================================================

Write-Host "📋 Files sẽ được dọn dẹp:" -ForegroundColor Cyan
Write-Host ""

$totalSize = 0
foreach ($file in $unusedFiles) {
    $fullPath = Join-Path $rootPath $file.Path
    
    if (Test-Path $fullPath) {
        $item = Get-Item $fullPath
        
        if ($item -is [System.IO.DirectoryInfo]) {
            $size = (Get-ChildItem $fullPath -Recurse | Measure-Object -Property Length -Sum).Sum
            $sizeStr = "{0:N2} KB" -f ($size / 1KB)
            $icon = "📁"
        } else {
            $size = $item.Length
            $sizeStr = "{0:N2} KB" -f ($size / 1KB)
            $icon = "📄"
            $totalSize += $size
        }
        
        Write-Host "  $icon $($file.Path)" -ForegroundColor White
        Write-Host "     Size: $sizeStr" -ForegroundColor Gray
        Write-Host "     Status: $($file.Status)" -ForegroundColor Yellow
        Write-Host "     Reason: $($file.Reason)" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "  ⚠️  $($file.Path) - NOT FOUND" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host "📊 Total size: {0:N2} KB" -f ($totalSize / 1KB) -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# XÁC NHẬN
# ============================================================================

Write-Host "⚠️  CÁC FILE NÀY SẼ ĐƯỢC:" -ForegroundColor Yellow
Write-Host "   1. Backup vào: backup_unused_files\$timestamp" -ForegroundColor White
Write-Host "   2. Xóa khỏi thư mục gốc" -ForegroundColor White
Write-Host ""

$confirmation = Read-Host "Bạn có chắc muốn tiếp tục? (y/N)"

if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host ""
    Write-Host "❌ Đã hủy. Không có file nào bị xóa." -ForegroundColor Red
    exit
}

# ============================================================================
# BACKUP VÀ XÓA
# ============================================================================

Write-Host ""
Write-Host "🔄 Đang xử lý..." -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($file in $unusedFiles) {
    $fullPath = Join-Path $rootPath $file.Path
    
    if (Test-Path $fullPath) {
        try {
            # Backup
            $relativePath = $file.Path
            $backupFilePath = Join-Path $backupFolder $relativePath
            $backupFileDir = Split-Path -Parent $backupFilePath
            
            if (-not (Test-Path $backupFileDir)) {
                New-Item -ItemType Directory -Path $backupFileDir -Force | Out-Null
            }
            
            # Copy to backup
            if ((Get-Item $fullPath) -is [System.IO.DirectoryInfo]) {
                Copy-Item -Path $fullPath -Destination $backupFilePath -Recurse -Force
            } else {
                Copy-Item -Path $fullPath -Destination $backupFilePath -Force
            }
            
            Write-Host "  ✅ Backed up: $($file.Path)" -ForegroundColor Green
            
            # Xóa file gốc
            Remove-Item -Path $fullPath -Recurse -Force
            Write-Host "  🗑️  Deleted: $($file.Path)" -ForegroundColor Yellow
            Write-Host ""
            
            $successCount++
        }
        catch {
            Write-Host "  ❌ Error: $($file.Path)" -ForegroundColor Red
            Write-Host "     $($_.Exception.Message)" -ForegroundColor Red
            Write-Host ""
            $failCount++
        }
    }
}

# ============================================================================
# KẾT QUẢ
# ============================================================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  HOÀN TẤT" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Success: $successCount files" -ForegroundColor Green
Write-Host "❌ Failed: $failCount files" -ForegroundColor Red
Write-Host ""
Write-Host "📁 Backup location: $backupFolder" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Lưu ý:" -ForegroundColor Cyan
Write-Host "   - Backup sẽ được giữ trong thư mục 'backup_unused_files'" -ForegroundColor White
Write-Host "   - Nếu cần khôi phục, copy từ backup về thư mục gốc" -ForegroundColor White
Write-Host "   - Có thể xóa thư mục backup sau khi chắc chắn hệ thống hoạt động tốt" -ForegroundColor White
Write-Host ""

# Tạo file README trong backup
$readmePath = Join-Path $backupFolder "README.txt"
$readmeContent = @"
BACKUP UNUSED FILES
===================
Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Files trong thư mục này đã được dọn dẹp khỏi attendance_system.

DANH SÁCH FILES:
"@

foreach ($file in $unusedFiles) {
    $readmeContent += "`n`n$($file.Path)"
    $readmeContent += "`n  Status: $($file.Status)"
    $readmeContent += "`n  Reason: $($file.Reason)"
}

$readmeContent += @"


CÁCH KHÔI PHỤC:
===============
Nếu cần khôi phục file nào đó, copy từ thư mục này về thư mục gốc:

    Copy-Item -Path "backup_unused_files\$timestamp\[file_path]" -Destination "attendance_system\[file_path]" -Force

VÍ DỤ:
    Copy-Item -Path "backup_unused_files\$timestamp\desktop\student_module.py" -Destination "attendance_system\desktop\student_module.py" -Force


SAU KHI TEST HỆ THỐNG:
======================
Nếu hệ thống hoạt động tốt, có thể xóa toàn bộ thư mục backup này để tiết kiệm dung lượng.

"@

Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8

Write-Host "📝 README file created: README.txt" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
