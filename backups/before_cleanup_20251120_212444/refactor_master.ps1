<# 
===============================================================================
REFACTORING MASTER SCRIPT
Tự động tạo cấu trúc chuyên nghiệp cho toàn bộ project
===============================================================================
#>

param(
    [switch]$Backend,
    [switch]$Desktop,
    [switch]$All
)

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "   🚀 REFACTORING TO PROFESSIONAL STRUCTURE" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Display help if no parameters
if (-not ($Backend -or $Desktop -or $All)) {
    Write-Host "CÁCH SỬ DỤNG:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  .\refactor_master.ps1 -Backend    # Chỉ refactor Backend" -ForegroundColor White
    Write-Host "  .\refactor_master.ps1 -Desktop    # Chỉ refactor Desktop" -ForegroundColor White
    Write-Host "  .\refactor_master.ps1 -All        # Refactor cả hai (KHUYẾN NGHỊ)" -ForegroundColor White
    Write-Host ""
    Write-Host "VÍ DỤ:" -ForegroundColor Yellow
    Write-Host "  .\refactor_master.ps1 -All" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# Function to run script and check result
function Run-RefactorScript {
    param(
        [string]$ScriptPath,
        [string]$Name
    )
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  🔧 $Name" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path $ScriptPath) {
        try {
            & $ScriptPath
            Write-Host ""
            Write-Host "✅ $Name - HOÀN THÀNH!" -ForegroundColor Green
            return $true
        } catch {
            Write-Host ""
            Write-Host "❌ $Name - LỖI!" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ Không tìm thấy script: $ScriptPath" -ForegroundColor Red
        return $false
    }
}

# Track results
$results = @{
    "Backend" = $false
    "Desktop" = $false
}

# Execute based on parameters
if ($Backend -or $All) {
    Write-Host "📦 Bắt đầu refactor BACKEND..." -ForegroundColor Yellow
    $results["Backend"] = Run-RefactorScript -ScriptPath ".\refactor_backend_phase1.ps1" -Name "BACKEND REFACTORING"
}

if ($Desktop -or $All) {
    Write-Host "🖥️  Bắt đầu refactor DESKTOP..." -ForegroundColor Yellow
    $results["Desktop"] = Run-RefactorScript -ScriptPath ".\refactor_desktop_phase1.ps1" -Name "DESKTOP REFACTORING"
}

# Summary
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  📊 TỔNG KẾT" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

$totalSuccess = 0
$totalFailed = 0

foreach ($key in $results.Keys) {
    if ($results[$key]) {
        Write-Host "  ✅ $key : " -NoNewline -ForegroundColor Green
        Write-Host "Thành công" -ForegroundColor Green
        $totalSuccess++
    } else {
        if ($results[$key] -eq $false -and ($Backend -or $Desktop -or $All)) {
            Write-Host "  ❌ $key : " -NoNewline -ForegroundColor Red
            Write-Host "Thất bại" -ForegroundColor Red
            $totalFailed++
        }
    }
}

Write-Host ""

if ($totalFailed -eq 0 -and $totalSuccess -gt 0) {
    Write-Host "🎉 HOÀN THÀNH! Cấu trúc mới đã được tạo thành công." -ForegroundColor Green
    Write-Host ""
    Write-Host "📂 CẤU TRÚC MỚI ĐÃ SẴN SÀNG:" -ForegroundColor Cyan
    Write-Host ""
    
    if ($results["Backend"]) {
        Write-Host "  ✅ Backend: attendance_system/backend/app/" -ForegroundColor Green
    }
    if ($results["Desktop"]) {
        Write-Host "  ✅ Desktop: attendance_system/desktop/app/" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "📝 BƯỚC TIẾP THEO:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. Đọc kỹ file: REFACTORING_PLAN.md" -ForegroundColor White
    Write-Host "  2. PHASE 2: Di chuyển code vào cấu trúc mới" -ForegroundColor White
    Write-Host "     - Backend: Tách models.py, schemas.py, main.py" -ForegroundColor White
    Write-Host "     - Desktop: Di chuyển từng module" -ForegroundColor White
    Write-Host "  3. Test kỹ càng sau mỗi bước di chuyển" -ForegroundColor White
    Write-Host "  4. Commit thường xuyên: git commit -m 'refactor: ...'" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  QUAN TRỌNG:" -ForegroundColor Yellow
    Write-Host "  - Các file CŨ vẫn còn nguyên (models.py, main.py, ...)" -ForegroundColor Yellow
    Write-Host "  - Chỉ XÓA file cũ sau khi chắc chắn code mới hoạt động 100%" -ForegroundColor Yellow
    Write-Host "  - Nên tạo backup branch: git checkout -b refactor/backup" -ForegroundColor Yellow
    
} elseif ($totalSuccess -eq 0) {
    Write-Host "ℹ️  Chưa có tác vụ nào được thực hiện." -ForegroundColor Gray
    Write-Host "   Chạy với -Backend, -Desktop, hoặc -All" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Một số tác vụ thất bại. Vui lòng kiểm tra lại." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
