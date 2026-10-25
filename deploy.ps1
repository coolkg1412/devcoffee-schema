Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($args.Count -ne 0) {
    [Console]::Error.WriteLine("Usage: .\deploy.ps1")
    exit 2
}

function Get-PypiToken {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    $currentSection = ""
    foreach ($line in [System.IO.File]::ReadAllLines($Path)) {
        $trimmed = $line.Trim()

        if ($trimmed -match '^\[(.+)\]$') {
            $currentSection = $Matches[1].Trim()
            continue
        }

        if ($currentSection -eq "pypi" -and $trimmed -match '^password\s*=\s*(.+)$') {
            $token = $Matches[1].Trim()
            if (
                $token.Length -ge 2 -and
                (($token.StartsWith('"') -and $token.EndsWith('"')) -or
                ($token.StartsWith("'") -and $token.EndsWith("'")))
            ) {
                $token = $token.Substring(1, $token.Length - 2)
            }
            return $token
        }
    }

    return $null
}

$repositoryRoot = $PSScriptRoot
$javaBuilder = Join-Path $repositoryRoot "builder\jav"
$pythonBuilder = Join-Path $repositoryRoot "builder\pyt"
$pomPath = Join-Path $javaBuilder "pom.xml"
$pyprojectPath = Join-Path $pythonBuilder "pyproject.toml"
$pythonDist = Join-Path $pythonBuilder "dist"

$pomText = [System.IO.File]::ReadAllText($pomPath)
$pyprojectText = [System.IO.File]::ReadAllText($pyprojectPath)
$javaVersionMatch = [regex]::Match(
    $pomText,
    '<artifactId>devcoffee-event-schema</artifactId>[\t\r\n ]*<version>([^<\r\n]+)</version>'
)
$pythonVersionMatch = [regex]::Match(
    $pyprojectText,
    '(?m)^version[\t ]*=[\t ]*"([^"\r\n]+)"'
)

if (-not $javaVersionMatch.Success -or -not $pythonVersionMatch.Success) {
    throw "Unable to determine the Java and Python package versions."
}

$javaVersion = $javaVersionMatch.Groups[1].Value.Trim()
$pythonVersion = $pythonVersionMatch.Groups[1].Value.Trim()
if ($javaVersion -ne $pythonVersion) {
    throw "Package versions do not match: Java=$javaVersion, Python=$pythonVersion."
}

$mavenSettingsPath = Join-Path ([Environment]::GetFolderPath("UserProfile")) ".m2\settings.xml"
if (-not (Test-Path -LiteralPath $mavenSettingsPath -PathType Leaf)) {
    throw "Maven settings file not found at '$mavenSettingsPath'."
}

[xml] $mavenSettings = [System.IO.File]::ReadAllText($mavenSettingsPath)
$mavenServer = $mavenSettings.SelectSingleNode(
    "/*[local-name()='settings']/*[local-name()='servers']/*[local-name()='server'][*[local-name()='id']='devcoffee-github']"
)
if ($null -eq $mavenServer) {
    throw "Maven server credentials for 'devcoffee-github' are missing from '$mavenSettingsPath'."
}

$pypircCandidates = @(
    (Join-Path $repositoryRoot ".pypirc"),
    (Join-Path ([Environment]::GetFolderPath("UserProfile")) ".pypirc")
)
$pypiToken = $null
$pypircPath = $null
foreach ($candidate in $pypircCandidates) {
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        continue
    }

    $candidateToken = Get-PypiToken -Path $candidate
    if (-not [string]::IsNullOrWhiteSpace($candidateToken)) {
        $pypiToken = $candidateToken
        $pypircPath = $candidate
        break
    }
}

if ([string]::IsNullOrWhiteSpace($pypiToken)) {
    throw "A token is required in the [pypi] password field of .pypirc."
}

$wheelPath = Join-Path $pythonDist "devcoffee_integration_event-$pythonVersion-py3-none-any.whl"
$sourceDistributionPath = Join-Path $pythonDist "devcoffee_integration_event-$pythonVersion.tar.gz"
foreach ($artifactPath in @($wheelPath, $sourceDistributionPath)) {
    if (-not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) {
        throw "Python artifact not found: '$artifactPath'. Run build.ps1 for version $pythonVersion first."
    }
}

Write-Host "Deploying Java and Python packages with version $javaVersion"
Write-Host "Using PyPI credentials from $pypircPath"

Push-Location $javaBuilder
try {
    & .\mvnw.cmd --quiet clean deploy
    if ($LASTEXITCODE -ne 0) {
        throw "Java deployment failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

$previousPublishToken = $env:UV_PUBLISH_TOKEN
try {
    $env:UV_PUBLISH_TOKEN = $pypiToken

    Push-Location $pythonBuilder
    try {
        & uv publish $wheelPath $sourceDistributionPath
        if ($LASTEXITCODE -ne 0) {
            throw "Python deployment failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}
finally {
    if ($null -eq $previousPublishToken) {
        Remove-Item Env:UV_PUBLISH_TOKEN -ErrorAction SilentlyContinue
    }
    else {
        $env:UV_PUBLISH_TOKEN = $previousPublishToken
    }
}

Write-Host "Deployment completed successfully for version $javaVersion"
