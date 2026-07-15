$base = "c:\Users\Acer Nitro\Documents\KasirGordenApp_Mobile_Flet"
$files = @(
    "main_mobile.py",
    "views_mobile\login_view.py",
    "views_mobile\dashboard_view.py",
    "views_mobile\inventory_view.py",
    "views_mobile\order_new_view.py",
    "views_mobile\order_history_view.py"
)

foreach ($f in $files) {
    $path = Join-Path $base $f
    if (Test-Path $path) {
        $content = Get-Content $path -Raw -Encoding UTF8
        $newContent = $content -creplace 'ft\.colors\.', 'ft.Colors.' -creplace 'ft\.icons\.', 'ft.Icons.'
        Set-Content $path $newContent -NoNewline -Encoding UTF8
        Write-Host "Fixed: $f"
    } else {
        Write-Host "NOT FOUND: $f"
    }
}

Write-Host "Done!"
