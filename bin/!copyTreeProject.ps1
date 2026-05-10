# Функция для рекурсивного вывода дерева с файлами
function Get-Tree {
    param([string]$Path = ".", [int]$Depth = 0, [string[]]$Exclude = @(".venv", ".pytest_cache", "__pycache__"))
    
    $items = Get-ChildItem $Path | Where-Object { $Exclude -notcontains $_.Name }
    $prefix = "|   " * $Depth
    $lines = @()
    
    for ($i = 0; $i -lt $items.Count; $i++) {
        $item = $items[$i]
        $isLast = ($i -eq $items.Count - 1)
        
        if ($isLast) {
            $connector = "`-- "
            $childPrefix = "    "
        } else {
            $connector = "|-- "
            $childPrefix = "|   "
        }
        
        if ($item.PSIsContainer) {
            $lines += "$prefix$connector$($item.Name)/"
            $lines += Get-Tree $item.FullName ($Depth + 1) $Exclude
        } else {
            $lines += "$prefix$connector$($item.Name)"
        }
    }
    
    return $lines
}

# Запуск и копирование в буфер
$output = Get-Tree
$output | Set-Clipboard
Write-Host $output