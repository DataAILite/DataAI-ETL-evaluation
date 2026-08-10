[CmdletBinding()]
param(
    [string]$Version = "0.1.0-evaluation.1",
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"
$nugetRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$outputDirectory = [System.IO.Path]::GetFullPath((Join-Path $nugetRoot "packages"))
$restoreDirectory = [System.IO.Path]::GetFullPath((Join-Path $nugetRoot ".packages"))
$runtimeProject = Join-Path $nugetRoot "src\Yanbor.DataAI.Etl.Spark.Runtime\Yanbor.DataAI.Etl.Spark.Runtime.csproj"
$helperProject = Join-Path $nugetRoot "src\Yanbor.DataAI.Etl.Spark\Yanbor.DataAI.Etl.Spark.csproj"
$testProject = Join-Path $nugetRoot "tests\Yanbor.DataAI.Etl.Spark.Tests\Yanbor.DataAI.Etl.Spark.Tests.csproj"
$consumerProject = Join-Path $nugetRoot "validation\PackageConsumer\PackageConsumer.csproj"

foreach ($generatedDirectory in @($outputDirectory, $restoreDirectory)) {
    if (-not $generatedDirectory.StartsWith($nugetRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Generated directory is outside the NuGet workspace: $generatedDirectory"
    }

    if (Test-Path -LiteralPath $generatedDirectory) {
        Remove-Item -LiteralPath $generatedDirectory -Recurse -Force
    }
    New-Item -ItemType Directory -Path $generatedDirectory -Force | Out-Null
}

dotnet run --project $testProject --configuration $Configuration
if ($LASTEXITCODE -ne 0) { throw "Source-level .NET validation failed." }

dotnet pack $runtimeProject --configuration $Configuration --output $outputDirectory -p:PackageVersion=$Version
if ($LASTEXITCODE -ne 0) { throw "Runtime package build failed." }

dotnet pack $helperProject --configuration $Configuration --output $outputDirectory -p:PackageVersion=$Version
if ($LASTEXITCODE -ne 0) { throw "Helper package build failed." }

$runtimePackage = Join-Path $outputDirectory "Yanbor.DataAI.Etl.Spark.Runtime.$Version.nupkg"
$helperPackage = Join-Path $outputDirectory "Yanbor.DataAI.Etl.Spark.$Version.nupkg"
foreach ($package in @($runtimePackage, $helperPackage)) {
    if (-not (Test-Path -LiteralPath $package)) {
        throw "Expected package was not created: $package"
    }
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$runtimeArchive = [System.IO.Compression.ZipFile]::OpenRead($runtimePackage)
try {
    $entries = @($runtimeArchive.Entries | ForEach-Object FullName)
    $requiredEntries = @(
        "tools/jars/dataai-spark-api-0.1.0-SNAPSHOT.jar",
        "tools/jars/dataai-spark-quality-0.1.0-SNAPSHOT.jar",
        "tools/jars/dataai-spark-core-0.1.0-SNAPSHOT.jar",
        "tools/jars/dataai-spark-functions-0.1.0-SNAPSHOT.jar",
        "tools/cli/dataai-spark-cli-0.1.0-SNAPSHOT.jar",
        "buildTransitive/Yanbor.DataAI.Etl.Spark.Runtime.props",
        "buildTransitive/Yanbor.DataAI.Etl.Spark.Runtime.targets",
        "LICENSE.md",
        "README.md"
    )
    foreach ($entry in $requiredEntries) {
        if ($entries -notcontains $entry) {
            throw "Runtime package is missing required entry: $entry"
        }
    }
}
finally {
    $runtimeArchive.Dispose()
}

dotnet restore $consumerProject --source $outputDirectory --packages $restoreDirectory --force --no-cache
if ($LASTEXITCODE -ne 0) { throw "Local-feed package restore failed." }

dotnet build $consumerProject --configuration $Configuration --no-restore
if ($LASTEXITCODE -ne 0) { throw "Local-feed package consumer build failed." }

dotnet run --project $consumerProject --configuration $Configuration --no-build
if ($LASTEXITCODE -ne 0) { throw "Local-feed package consumer execution failed." }

$checksumPath = Join-Path $nugetRoot "CHECKSUMS.sha256"
$checksumLines = Get-FileHash -Algorithm SHA256 -LiteralPath $runtimePackage, $helperPackage |
    Sort-Object Path |
    ForEach-Object { "{0}  {1}" -f $_.Hash.ToLowerInvariant(), (Split-Path -Leaf $_.Path) }
[System.IO.File]::WriteAllLines($checksumPath, $checksumLines, [System.Text.UTF8Encoding]::new($false))

Write-Output "Created and validated:"
Write-Output $runtimePackage
Write-Output $helperPackage
Write-Output $checksumPath
