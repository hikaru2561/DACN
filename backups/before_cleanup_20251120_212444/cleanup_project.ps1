<# 
===============================================================================
SCRIPT DỌN DẸP CẤU TRÚC PROJECT
Chức năng: Xóa file/folder không cần thiết, tổ chức lại structure
===============================================================================
#>

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  DỌN DẸP CẤU TRÚC PROJECT - FACE RECOGNITION ATTENDANCE SYSTEM" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra xem đang ở đúng thư mục project không
if (-not (Test-Path "attendance_system")) {
    Write-Host "❌ LỖI: Vui lòng chạy script từ thư mục gốc của project (d:\HUTECH\DACN)" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Bước 1: Kiểm tra các file/folder cần xóa..." -ForegroundColor Yellow
Write-Host ""

# Danh sách các items cần xóa
$itemsToRemove = @(
    @{
        Path = "attendance_system\dataset"
        Reason = "Thư mục trùng (dataset chính ở root)"
        Type = "Directory"
    },
    @{
        Path = "attendance_system\temp"
        Reason = "Thư mục tạm thời trống"
        Type = "Directory"
    },
    @{
        Path = "attendance_system\logs"
        Reason = "Thư mục logs trống"
        Type = "Directory"
    },
    @{
        Path = "attendance_system\models"
        Reason = "Thư mục models trống (model code ở backend/models.py)"
        Type = "Directory"
    },
    @{
        Path = "attendance_system\backup_unused_files"
        Reason = "Backup cũ (đã commit vào git)"
        Type = "Directory"
    },
    @{
        Path = "attendance_system\README.md"
        Reason = "README trùng (giữ README ở root)"
        Type = "File"
    },
    @{
        Path = "attendance_system\desktop\README.md"
        Reason = "README trùng (giữ README ở root)"
        Type = "File"
    }
)

# Hiển thị danh sách
$totalSize = 0
foreach ($item in $itemsToRemove) {
    $fullPath = Join-Path $PWD $item.Path
    
    if (Test-Path $fullPath) {
        if ($item.Type -eq "Directory") {
            $size = (Get-ChildItem -Path $fullPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
            if ($null -eq $size) { $size = 0 }
            $sizeStr = "{0:N2} MB" -f ($size / 1MB)
        } else {
            $size = (Get-Item $fullPath).Length
            $sizeStr = "{0:N2} KB" -f ($size / 1KB)
        }
        
        $totalSize += $size
        
        Write-Host "  ✓ [$($item.Type)]" -ForegroundColor Green -NoNewline
        Write-Host " $($item.Path)" -ForegroundColor White -NoNewline
        Write-Host " ($sizeStr)" -ForegroundColor Gray
        Write-Host "    → $($item.Reason)" -ForegroundColor DarkGray
    } else {
        Write-Host "  ⊘ [$($item.Type)]" -ForegroundColor DarkGray -NoNewline
        Write-Host " $($item.Path)" -ForegroundColor DarkGray -NoNewline
        Write-Host " (Không tồn tại)" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "💾 Tổng dung lượng sẽ được giải phóng: " -NoNewline -ForegroundColor Cyan
Write-Host ("{0:N2} MB" -f ($totalSize / 1MB)) -ForegroundColor Yellow
Write-Host ""

# Xác nhận
$confirmation = Read-Host "⚠️  Bạn có chắc muốn XÓA các file/folder trên? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host ""
    Write-Host "❌ Hủy bỏ. Không có thay đổi nào được thực hiện." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🗑️  Bước 2: Đang xóa..." -ForegroundColor Yellow
Write-Host ""

$deletedCount = 0
$errorCount = 0

foreach ($item in $itemsToRemove) {
    $fullPath = Join-Path $PWD $item.Path
    
    if (Test-Path $fullPath) {
        try {
            Remove-Item -Path $fullPath -Recurse -Force -ErrorAction Stop
            Write-Host "  ✅ Đã xóa: $($item.Path)" -ForegroundColor Green
            $deletedCount++
        } catch {
            Write-Host "  ❌ Lỗi khi xóa: $($item.Path)" -ForegroundColor Red
            Write-Host "     $($_.Exception.Message)" -ForegroundColor DarkRed
            $errorCount++
        }
    }
}

Write-Host ""
Write-Host "📁 Bước 3: Tổ chức lại documentation..." -ForegroundColor Yellow
Write-Host ""

# Tạo thư mục docs nếu chưa có
if (-not (Test-Path "docs")) {
    New-Item -ItemType Directory -Path "docs" -Force | Out-Null
    Write-Host "  ✅ Đã tạo thư mục: docs\" -ForegroundColor Green
}

# Di chuyển MODEL_INFO.md
$modelInfoSrc = "attendance_system\MODEL_INFO.md"
$modelInfoDest = "docs\MODEL_INFO.md"

if (Test-Path $modelInfoSrc) {
    try {
        Move-Item -Path $modelInfoSrc -Destination $modelInfoDest -Force -ErrorAction Stop
        Write-Host "  ✅ Đã di chuyển: MODEL_INFO.md → docs\" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Lỗi khi di chuyển MODEL_INFO.md" -ForegroundColor Red
        Write-Host "     $($_.Exception.Message)" -ForegroundColor DarkRed
        $errorCount++
    }
} else {
    Write-Host "  ⊘ MODEL_INFO.md không tồn tại" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "📊 Bước 4: Tạo .gitignore mới..." -ForegroundColor Yellow
Write-Host ""

# Nội dung .gitignore mới
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
*.log

# Dataset
dataset/raw/
dataset/processed/
*.pkl

# Temporary
temp/
logs/
*.tmp

# OS
.DS_Store
Thumbs.db

# Project-specific
attendance_system/models/*.pth
attendance_system/models/*.h5
attendance_system/backup_unused_files/
"@

try {
    $gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8 -Force
    Write-Host "  ✅ Đã cập nhật .gitignore" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Lỗi khi cập nhật .gitignore" -ForegroundColor Red
    $errorCount++
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  KẾT QUẢ" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Đã xóa: " -NoNewline -ForegroundColor Green
Write-Host "$deletedCount items" -ForegroundColor White
Write-Host "❌ Lỗi: " -NoNewline -ForegroundColor Red
Write-Host "$errorCount items" -ForegroundColor White
Write-Host "💾 Dung lượng giải phóng: " -NoNewline -ForegroundColor Cyan
Write-Host ("{0:N2} MB" -f ($totalSize / 1MB)) -ForegroundColor Yellow
Write-Host ""

if ($errorCount -eq 0) {
    Write-Host "🎉 HOÀN THÀNH! Project đã được dọn dẹp." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Các bước tiếp theo:" -ForegroundColor Cyan
    Write-Host "  1. Chạy: git status" -ForegroundColor White
    Write-Host "  2. Chạy: git add ." -ForegroundColor White
    Write-Host "  3. Chạy: git commit -m 'refactor: clean up project structure'" -ForegroundColor White
    Write-Host "  4. Chạy: git push" -ForegroundColor White
} else {
    Write-Host "⚠️  HOÀN THÀNH với $errorCount lỗi. Vui lòng kiểm tra lại." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
