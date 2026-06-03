<#
.SYNOPSIS
    批量替换图片中指定颜色（保留透明区域），支持自动检测主色、容差控制。
.DESCRIPTION
    遍历当前目录下的常见图片，对每个非透明像素：
    - 如果其RGB颜色与源颜色的欧氏距离 ≤ 容差阈值，则替换为目标颜色（保留原Alpha）。
    - 完全透明（Alpha=0）的像素保持不变。
    支持格式：PNG, JPEG, BMP, GIF, TIFF。
#>

Add-Type -AssemblyName System.Drawing

# 颜色距离计算（欧氏距离，基于RGB，忽略Alpha）
function ColorDistance([System.Drawing.Color]$c1, [System.Drawing.Color]$c2) {
    $dr = $c1.R - $c2.R
    $dg = $c1.G - $c2.G
    $db = $c1.B - $c2.B
    return [Math]::Sqrt($dr*$dr + $dg*$dg + $db*$db)
}

# 将RGB值（0-255）转换为Color对象
function NewColor($r, $g, $b) {
    return [System.Drawing.Color]::FromArgb(255, $r, $g, $b)
}

# 将RGB整数（R<<16|G<<8|B）转换为Color
function IntToColor($intColor) {
    $r = ($intColor -shr 16) -band 0xFF
    $g = ($intColor -shr 8) -band 0xFF
    $b = $intColor -band 0xFF
    return NewColor $r $g $b
}

# 交互：获取源颜色
function GetSourceColor {
    Write-Host "`nSource color selection:" -ForegroundColor Cyan
    Write-Host "  1. Auto detect most frequent color (default)"
    Write-Host "  2. Manual input (R G B values 0-255)"
    $choice = Read-Host "Enter choice (1/2)"
    if ($choice -eq "2") {
        $r = [int](Read-Host "  Red (0-255)")
        $g = [int](Read-Host "  Green (0-255)")
        $b = [int](Read-Host "  Blue (0-255)")
        return NewColor $r $g $b
    } else {
        # 自动检测：统计所有非透明像素的RGB频率
        Write-Host "Auto detecting most frequent color..." -ForegroundColor Yellow
        $colorCount = @{}  # 键为 (R<<16|G<<8|B) 整数，值为计数
        $totalPixels = 0
        $extensions = @("*.png","*.jpg","*.jpeg","*.bmp","*.gif","*.tiff","*.tif")
        foreach ($pattern in $extensions) {
            Get-ChildItem -Path "." -Filter $pattern | ForEach-Object {
                $file = $_.FullName
                Write-Host "  Scanning: $_"
                try {
                    $img = [System.Drawing.Image]::FromFile($file)
                    $bmp = New-Object System.Drawing.Bitmap($img)
                    $img.Dispose()
                    for ($y = 0; $y -lt $bmp.Height; $y++) {
                        for ($x = 0; $x -lt $bmp.Width; $x++) {
                            $p = $bmp.GetPixel($x, $y)
                            if ($p.A -ne 0) {
                                $rgbInt = ($p.R -shl 16) -bor ($p.G -shl 8) -bor $p.B
                                $colorCount[$rgbInt] = $colorCount[$rgbInt] + 1
                                $totalPixels++
                            }
                        }
                    }
                    $bmp.Dispose()
                } catch {
                    Write-Host "    Error scanning $_ : $_" -ForegroundColor Red
                }
            }
        }
        if ($totalPixels -eq 0) {
            Write-Host "No non-transparent pixel found! Fallback to white." -ForegroundColor Red
            return NewColor 255 255 255
        }
        $maxCount = 0
        $maxColorInt = 0
        foreach ($kv in $colorCount.GetEnumerator()) {
            if ($kv.Value -gt $maxCount) {
                $maxCount = $kv.Value
                $maxColorInt = $kv.Key
            }
        }
        $dominantColor = IntToColor $maxColorInt
        $percentage = [Math]::Round(($maxCount / $totalPixels) * 100, 2)
        Write-Host "`nMost frequent color: R=$($dominantColor.R) G=$($dominantColor.G) B=$($dominantColor.B) (${percentage}% of non-transparent pixels)" -ForegroundColor Green
        $confirm = Read-Host "Use this color? (Y/n)"
        if ($confirm -eq "n" -or $confirm -eq "N") {
            return GetSourceColor   # 重新选择
        }
        return $dominantColor
    }
}

# 交互：获取目标颜色
function GetTargetColor {
    Write-Host "`nTarget color (to replace with):" -ForegroundColor Cyan
    Write-Host "Press Enter for white (255,255,255)"
    $input = Read-Host "Enter R G B separated by space (e.g. 255 0 0)"
    if ([string]::IsNullOrWhiteSpace($input)) {
        return NewColor 255 255 255
    }
    $parts = $input.Trim() -split '\s+'
    if ($parts.Count -ge 3) {
        $r = [Math]::Clamp([int]$parts[0], 0, 255)
        $g = [Math]::Clamp([int]$parts[1], 0, 255)
        $b = [Math]::Clamp([int]$parts[2], 0, 255)
        return NewColor $r $g $b
    } else {
        Write-Host "Invalid input, using white." -ForegroundColor Red
        return NewColor 255 255 255
    }
}

# 交互：获取容差（0-100）
function GetTolerance {
    Write-Host "`nTolerance (0-100):" -ForegroundColor Cyan
    Write-Host "  0 = exact match only, 100 = all colors"
    $tol = Read-Host "Enter tolerance [default 0]"
    if ([string]::IsNullOrWhiteSpace($tol)) { return 0 }
    $t = [int]$tol
    if ($t -lt 0) { $t = 0 }
    if ($t -gt 100) { $t = 100 }
    # 将0-100映射到欧氏距离最大值（0~441.67）
    $maxDist = [Math]::Sqrt(255*255*3)  # ≈441.67
    $threshold = ($t / 100.0) * $maxDist
    return $threshold
}

# ---------- 主程序 ----------
Clear-Host
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  批量图片颜色替换工具（保留透明像素）" -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Cyan

# 确认覆盖
Write-Host "`nWARNING: Original files will be OVERWRITTEN!" -ForegroundColor Red
$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") { exit }

# 获取源颜色
$srcColor = GetSourceColor
# 获取目标颜色
$dstColor = GetTargetColor
# 获取容差
$tolerance = GetTolerance

Write-Host "`nSettings:" -ForegroundColor Yellow
Write-Host "  Source color : R=$($srcColor.R) G=$($srcColor.G) B=$($srcColor.B)"
Write-Host "  Target color: R=$($dstColor.R) G=$($dstColor.G) B=$($dstColor.B)"
Write-Host "  Tolerance    : $([Math]::Round($tolerance,2)) (max distance)"
$finalConfirm = Read-Host "`nProceed with replacement? (Y/N)"
if ($finalConfirm -ne "Y" -and $finalConfirm -ne "y") { exit }

# 开始处理
$extensions = @("*.png","*.jpg","*.jpeg","*.bmp","*.gif","*.tiff","*.tif")
$processed = 0
$failed = 0

foreach ($pattern in $extensions) {
    Get-ChildItem -Path "." -Filter $pattern | ForEach-Object {
        $file = $_.FullName
        Write-Host "Processing: $_"
        try {
            # 加载原图
            $img = [System.Drawing.Image]::FromFile($file)
            $bmp = New-Object System.Drawing.Bitmap($img)
            $img.Dispose()

            # 创建新位图（32位ARGB，保留透明）
            $newBmp = New-Object System.Drawing.Bitmap($bmp.Width, $bmp.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)

            for ($y = 0; $y -lt $bmp.Height; $y++) {
                for ($x = 0; $x -lt $bmp.Width; $x++) {
                    $p = $bmp.GetPixel($x, $y)
                    if ($p.A -eq 0) {
                        # 完全透明：直接复制原像素（保持透明）
                        $newBmp.SetPixel($x, $y, $p)
                        continue
                    }
                    # 计算与源颜色的距离
                    $dist = ColorDistance $p $srcColor
                    if ($dist -le $tolerance) {
                        # 替换为目标颜色，保留原Alpha
                        $newColor = [System.Drawing.Color]::FromArgb($p.A, $dstColor.R, $dstColor.G, $dstColor.B)
                        $newBmp.SetPixel($x, $y, $newColor)
                    } else {
                        # 保持不变
                        $newBmp.SetPixel($x, $y, $p)
                    }
                }
            }
            $bmp.Dispose()

            # 保存（根据原始扩展名选择格式）
            $ext = [System.IO.Path]::GetExtension($file).ToLower()
            switch ($ext) {
                ".png"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Png }
                ".jpg"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Jpeg }
                ".jpeg" { $fmt = [System.Drawing.Imaging.ImageFormat]::Jpeg }
                ".bmp"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Bmp }
                ".gif"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Gif }
                ".tiff" { $fmt = [System.Drawing.Imaging.ImageFormat]::Tiff }
                ".tif"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Tiff }
                default { $fmt = [System.Drawing.Imaging.ImageFormat]::Png }
            }
            $newBmp.Save($file, $fmt)
            $newBmp.Dispose()
            Write-Host "  Success" -ForegroundColor Green
            $processed++
        } catch {
            Write-Host "  Error: $_" -ForegroundColor Red
            $failed++
        }
    }
}

Write-Host "`nAll done. Processed: $processed, Failed: $failed" -ForegroundColor Cyan
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")