# ============================================================================
# PREVIEW UNUSED FILES - Xem trước files sẽ bị dọn dẹp
# Script này CHỈ HIỂN THỊ, không xóa gì cả
# ============================================================================

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  PREVIEW: FILES SẼ BỊ DỌN DẸP" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path

$unusedFiles = @(
    "desktop\student_module.py",
    "desktop\config_manager.py", 
    "desktop\update_camera.py",
    "temp"
)

$totalSize = 0
$existingFiles = @()

Write-Host "📋 Phân tích files..." -ForegroundColor Yellow
Write-Host ""

foreach ($file in $unusedFiles) {
    $fullPath = Join-Path $rootPath $file
    
    if (Test-Path $fullPath) {
        $item = Get-Item $fullPath
        
        if ($item -is [System.IO.DirectoryInfo]) {
            $fileCount = (Get-ChildItem $fullPath -Recurse -File).Count
            $size = (Get-ChildItem $fullPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
            $type = "FOLDER"
            $icon = "📁"
            $details = "$fileCount files"
        } else {
            $size = $item.Length
            $lines = (Get-Content $fullPath -ErrorAction SilentlyContinue).Count
            $type = "FILE"
            $icon = "📄"
            $details = "$lines lines"
        }
        
        $totalSize += $size
        $existingFiles += @{
            Path = $file
            FullPath = $fullPath
            Size = $size
            Type = $type
            Icon = $icon
            Details = $details
        }
        
        # Hiển thị
        Write-Host "  $icon $file" -ForegroundColor White
        Write-Host "     Type: $type" -ForegroundColor Gray
        Write-Host "     Size: $("{0:N2}" -f ($size / 1KB)) KB" -ForegroundColor Gray
        Write-Host "     Details: $details" -ForegroundColor Gray
        
        # Kiểm tra có được import không
        $isImported = $false
        if ($type -eq "FILE") {
            $fileName = [System.IO.Path]::GetFileNameWithoutExtension($file)
            $desktopPath = Join-Path $rootPath "desktop"
            
            Get-ChildItem $desktopPath -Filter "*.py" | ForEach-Object {
                $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
                # Kiểm tra chính xác: không match student_module_new khi tìm student_module
                if ($content -match "import\s+$fileName[^\w]|from\s+$fileName\s+import") {
                    Write-Host "     ⚠️  WARNING: Được import trong $($_.Name)" -ForegroundColor Red
                    $isImported = $true
                }
            }
            
            if (-not $isImported) {
                Write-Host "     ✅ Safe to delete: Không có module nào import" -ForegroundColor Green
            }
        } elseif ($fileCount -eq 0) {
            Write-Host "     ✅ Safe to delete: Thư mục rỗng" -ForegroundColor Green
        }
        
        Write-Host ""
    } else {
        Write-Host "  ⚠️  $file - NOT FOUND" -ForegroundColor Yellow
        Write-Host ""
    }
}

# ============================================================================
# TỔNG KẾT
# ============================================================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  TỔNG KẾT" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Tổng số files: $($existingFiles.Count)" -ForegroundColor White
Write-Host "📦 Tổng dung lượng: $("{0:N2}" -f ($totalSize / 1KB)) KB ($("{0:N2}" -f ($totalSize / 1MB)) MB)" -ForegroundColor White
Write-Host ""

Write-Host "📁 Chi tiết:" -ForegroundColor Cyan
$fileCount = ($existingFiles | Where-Object { $_.Type -eq "FILE" }).Count
$folderCount = ($existingFiles | Where-Object { $_.Type -eq "FOLDER" }).Count
Write-Host "   - Files: $fileCount" -ForegroundColor White
Write-Host "   - Folders: $folderCount" -ForegroundColor White
Write-Host ""

# ============================================================================
# BƯỚC TIẾP THEO
# ============================================================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  BƯỚC TIẾP THEO" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Đây chỉ là PREVIEW, chưa xóa gì cả!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Để dọn dẹp thực sự, chạy:" -ForegroundColor White
Write-Host ""
Write-Host "   .\cleanup_unused_files.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Script đó sẽ:" -ForegroundColor Yellow
Write-Host "   1. Backup tất cả files vào 'backup_unused_files\'" -ForegroundColor White
Write-Host "   2. Xóa files khỏi thư mục gốc" -ForegroundColor White
Write-Host "   3. Tạo README để hướng dẫn khôi phục" -ForegroundColor White
Write-Host ""
Write-Host "📚 Đọc hướng dẫn chi tiết:" -ForegroundColor Cyan
Write-Host "   Get-Content CLEANUP_GUIDE.md" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
