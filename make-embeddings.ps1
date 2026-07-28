# Generates public/assets/embeddings.json for the Ask the Guide RAG pipeline.
# Run from the repo root AFTER updating the Cloudflare Worker to support embed requests.
# Usage: powershell -ExecutionPolicy Bypass -File make-embeddings.ps1

$worker = "https://jolly-waterfall-d01a.nicholas-morlin.workers.dev/"
$dim = 256
$idxPath = "public/assets/search.json"
$outPath = "public/assets/embeddings.json"

$idx = Get-Content $idxPath -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Host "Embedding $($idx.Count) chunks in batches of 100..."

$vecs = New-Object System.Collections.Generic.List[string]
for ($i = 0; $i -lt $idx.Count; $i += 100) {
    $end = [Math]::Min($i + 99, $idx.Count - 1)
    $batch = @()
    foreach ($e in $idx[$i..$end]) {
        $text = "$($e.t). $($e.b)"
        if ($text.Length -gt 1200) { $text = $text.Substring(0, 1200) }
        $batch += $text
    }
    $body = @{ embed = $true; input = $batch } | ConvertTo-Json -Depth 4
    $resp = Invoke-RestMethod -Uri $worker -Method Post -ContentType "application/json" `
        -Headers @{ Origin = "http://localhost" } -Body $body
    if (-not $resp.data) { throw "No data returned at batch $i - is the Worker updated?" }
    foreach ($d in $resp.data) {
        $v = $d.embedding[0..($dim - 1)]
        $norm = 0.0
        foreach ($x in $v) { $norm += $x * $x }
        $norm = [Math]::Sqrt($norm)
        if ($norm -eq 0) { $norm = 1 }
        $bytes = [byte[]]::new($dim)
        for ($j = 0; $j -lt $dim; $j++) {
            $q = [int][Math]::Round($v[$j] / $norm * 127)
            if ($q -gt 127) { $q = 127 }
            if ($q -lt -127) { $q = -127 }
            $bytes[$j] = [byte](($q + 256) % 256)
        }
        $vecs.Add([Convert]::ToBase64String($bytes))
    }
    Write-Host "  $($end + 1) / $($idx.Count) done"
    Start-Sleep -Seconds 1
}

@{ dim = $dim; v = $vecs } | ConvertTo-Json -Compress | Set-Content $outPath -Encoding UTF8
Write-Host "Wrote $outPath ($([Math]::Round((Get-Item $outPath).Length / 1KB)) KB)"
