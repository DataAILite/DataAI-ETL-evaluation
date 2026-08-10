[CmdletBinding()]
param([string]$Version = "0.1.0-evaluation.1")

$ErrorActionPreference = "Stop"
$nugetRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$packageDirectory = Join-Path $nugetRoot "packages"
$runtimePackage = Join-Path $packageDirectory "Yanbor.DataAI.Etl.Spark.Runtime.$Version.nupkg"
$helperPackage = Join-Path $packageDirectory "Yanbor.DataAI.Etl.Spark.$Version.nupkg"
$checksumPath = Join-Path $nugetRoot "CHECKSUMS.sha256"

foreach ($path in @($runtimePackage, $helperPackage, $checksumPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required validation input is missing: $path"
    }
}

$recorded = @{}
foreach ($line in Get-Content -LiteralPath $checksumPath) {
    if ($line -match '^([0-9a-fA-F]{64})\s+(.+)$') {
        $recorded[$Matches[2]] = $Matches[1].ToLowerInvariant()
    }
}

foreach ($package in @($runtimePackage, $helperPackage)) {
    $name = Split-Path -Leaf $package
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $package).Hash.ToLowerInvariant()
    if ($recorded[$name] -ne $actual) {
        throw "Checksum mismatch for $name"
    }
}

Write-Output "NuGet package checksums are valid."
