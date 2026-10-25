Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Usage {
    [Console]::Error.WriteLine("Usage: .\build.ps1 --build-version <version>")
}

if ($args.Count -ne 2 -or $args[0] -ne "--build-version") {
    Write-Usage
    exit 2
}

$buildVersion = [string]$args[1]
if ([string]::IsNullOrWhiteSpace($buildVersion) -or $buildVersion -notmatch "^[0-9A-Za-z][0-9A-Za-z._+-]*$") {
    [Console]::Error.WriteLine("Invalid build version: '$buildVersion'")
    Write-Usage
    exit 2
}

$repositoryRoot = $PSScriptRoot
$javaBuilder = Join-Path $repositoryRoot "builder\jav"
$pythonBuilder = Join-Path $repositoryRoot "builder\pyt"
$pomPath = Join-Path $javaBuilder "pom.xml"
$pyprojectPath = Join-Path $pythonBuilder "pyproject.toml"

$utf8 = [System.Text.UTF8Encoding]::new($false)
$pomText = [System.IO.File]::ReadAllText($pomPath, $utf8)
$pyprojectText = [System.IO.File]::ReadAllText($pyprojectPath, $utf8)

$pomVersionPattern = [regex]::new(
    '(<artifactId>devcoffee-event-schema</artifactId>[\t\r\n ]*<version>)[^<\r\n]+(</version>)'
)
$pyprojectVersionPattern = [regex]::new(
    '(?m)^(version[\t ]*=[\t ]*")[^"\r\n]+("[\t ]*)(\r?)$'
)

if ($pomVersionPattern.Matches($pomText).Count -ne 1) {
    throw "Expected exactly one Java project version in '$pomPath'."
}
if ($pyprojectVersionPattern.Matches($pyprojectText).Count -ne 1) {
    throw "Expected exactly one Python project version in '$pyprojectPath'."
}

$pomReplacement = [System.Text.RegularExpressions.MatchEvaluator] {
    param([System.Text.RegularExpressions.Match] $match)
    return $match.Groups[1].Value + $buildVersion + $match.Groups[2].Value
}
$pyprojectReplacement = [System.Text.RegularExpressions.MatchEvaluator] {
    param([System.Text.RegularExpressions.Match] $match)
    return $match.Groups[1].Value + $buildVersion + $match.Groups[2].Value + $match.Groups[3].Value
}

$buildPom = $pomVersionPattern.Replace($pomText, $pomReplacement, 1)
$buildPyproject = $pyprojectVersionPattern.Replace($pyprojectText, $pyprojectReplacement, 1)

Write-Host "Building Java and Python packages with version $buildVersion"

[System.IO.File]::WriteAllText($pomPath, $buildPom, $utf8)
[System.IO.File]::WriteAllText($pyprojectPath, $buildPyproject, $utf8)

Push-Location $pythonBuilder
try {
    & uv lock
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to update the Python lockfile; uv exited with code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Push-Location $javaBuilder
try {
    & .\mvnw.cmd --quiet clean install
    if ($LASTEXITCODE -ne 0) {
        throw "Java build failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Push-Location $pythonBuilder
try {
    & uv build
    if ($LASTEXITCODE -ne 0) {
        throw "Python build failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Write-Host "Build completed successfully for version $buildVersion"
