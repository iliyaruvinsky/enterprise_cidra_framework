<#
.SYNOPSIS
    CIDRA Bootstrap - One-shot mechanical setup for a new CIDRA project.

.DESCRIPTION
    Performs ALL mechanical steps of the CIDRA runbook in a single idempotent run:
      1. Verifies prerequisites (Git, Cursor/VS Code) with absolute-path fallback
         when GUI installers did not add the binaries to PATH.
      2. Clones (or pulls) the enterprise_cidra_framework repo into a canonical
         location -- with health checks, dirty-tree detection, and atomic-clone
         via temp-rename.
      3. Creates the project + Source Code directory (with sync-drive detection
         and existing-directory-collision protection).
      4. Copies source files from -SourcePath using literal-path enumeration with
         a default exclude-list for binary/data files. Writes a completion
         sentinel so partial copies are detected on re-run.
      5. Optionally copies reference materials into a dedicated Reference/
         subdirectory (so they cannot collide with downstream artifacts).
      6. Unblocks MOTW only on files that still carry the Zone.Identifier ADS
         (gated by a one-shot sentinel after the first full pass).
      7. Runs Scripts/install.ps1 -ProjectPath <project> as a CHILD process so
         its exit code can be observed and the bootstrap banner always prints.
      8. Verifies the install with a stricter check (expected agent folders,
         entry-point command files, optional install-complete sentinel).
      9. Opens the project in Cursor (fallback VS Code, fallback manual
         instruction), warning loudly if a fallback IDE is used.
     10. Writes a project-local cidra.env.ps1 so Step 10 (delivery) can
         dot-source instead of re-typing values.
     11. Prints the single next-step instruction:
         "Type /brainstorm in Claude Code (after confirming the extension is installed)".

    Idempotency model: every stage has a completion sentinel (or equivalent
    fingerprint check). A re-run after a partial failure does NOT silently
    assume success -- it re-does the failed stage, surfaces what changed, and
    refuses to declare green on a corrupted tree.

.PARAMETER ProjectFolder
    Short ASCII directory name for the project (e.g. "rk1_pharmacy"). Required.
    This becomes the leaf folder under -ProjectRoot.
    Unicode (Hebrew, etc.) is allowed but spaces and NTFS-illegal characters
    are rejected.

.PARAMETER ComponentId
    UPPER_SNAKE_CASE identifier flowing through CHUNKS/, Screens/<id>/,
    RECOMMENDATIONS/<id>/, and the delivery zip filename
    (e.g. "RK1_PHARMACY_JOURNAL"). Required.
    Constrained to ASCII alnum + . _ - because it lands in filenames.

.PARAMETER SourcePath
    Directory containing the source code files to copy into <project>\Source Code\.
    Required.

.PARAMETER ReferenceDocsPath
    Optional. Directory (or single file) of reference materials (spec docs, sample
    CSVs) to drop into <project>\Reference\ for the brainstormer to discover.

.PARAMETER SourceFilter
    Optional glob filter applied when enumerating files in -SourcePath
    (default '*').

.PARAMETER SourceExclude
    Optional array of glob exclusions applied during source copy. Defaults to
    common binary / sample-data extensions that should NOT enter Source Code/:
        *.csv, *.xlsx, *.xls, *.exe, *.dll, *.zip, *.tar, *.gz, *.7z, *.png,
        *.jpg, *.jpeg, *.gif, *.pdf
    Pass an empty array (@()) to disable all exclusions.

.PARAMETER SourceRenameTo
    Optional. Extension to APPEND to every copied source file after the copy
    completes. Designed for AS/400 source-library exports whose filenames are
    library.member style (e.g. QCBLLESRC.SEWKXFKB) and need a language hint
    suffix so downstream tooling (chunker, IDE syntax highlighting) recognizes
    them.

    Append semantics -- the original filename is preserved; only the new
    extension is added as a final suffix:
        QCBLLESRC.SEWKXFKB  ->  QCBLLESRC.SEWKXFKB.cob
        my_program          ->  my_program.cob
        README              ->  README.cob   (CAUTION: README is now COBOL!)
        report.txt          ->  report.txt.cob   (NOT replaced; appended)

    Idempotent -- files whose name already ends with this extension
    (case-insensitive) are left untouched (mixed-case suffixes are
    canonicalized to lowercase to keep downstream regex matching consistent).

    Collision handling -- if appending the extension would overwrite an
    existing file (e.g. both QCBLLESRC.SEWKXFKB AND QCBLLESRC.SEWKXFKB.cob
    are in the source), the rename is SKIPPED with a warning and the skipped
    count is surfaced in the completion sentinel. Re-run with -ForceSource
    after resolving collisions in the source library.

    MAX_PATH handling -- on Windows PowerShell 5.1 without LongPathsEnabled,
    rename is SKIPPED if the resulting path would exceed 259 characters.

    Re-run semantics -- changing -SourceRenameTo between runs requires
    -ForceSource. Without -ForceSource, the script refuses to mix a fresh
    rename value with stale renamed files from a prior run.

    Pass with the leading dot (e.g. ".cob"). A missing leading dot will be
    prepended automatically. Pass "" (default) to disable renaming.

    Example:
        -SourcePath C:\exports\QCBLLESRC -SourceRenameTo ".cob"

.PARAMETER ProjectRoot
    Optional parent directory where the project folder is created.
    Default: C:\projects

.PARAMETER FrameworkPath
    Optional local path where the framework repo lives / will be cloned.
    Default: C:\Users\<USERNAME>\tools\enterprise_cidra_framework

.PARAMETER FrameworkRepo
    Optional Git URL of the framework repo.
    Default: https://github.com/iliyaruvinsky/enterprise_cidra_framework.git

.PARAMETER Ide
    Optional. 'cursor' or 'vscode'. Which IDE to launch at the end.
    Default 'cursor'.

.PARAMETER SkipIdeLaunch
    Optional switch. Don't try to open the IDE; just print the manual instruction.

.PARAMETER ForceSource
    Optional switch. Re-copy source files even if a successful previous copy
    sentinel exists.

.PARAMETER ForceFramework
    Optional switch. Pass -Force to install.ps1 (overwrite an existing .cidra/)
    AND do a full replace of .claude\commands instead of a merge.

.PARAMETER AdoptExistingDirectory
    Optional switch. Allow bootstrap to write into a pre-existing non-empty
    project directory that does NOT already contain a .cidra/ install.

.PARAMETER AllowSyncDrive
    Optional switch. Suppress the cloud-sync-drive guard (OneDrive, Google Drive,
    Dropbox, iCloud). Use only if you have paused sync.

.PARAMETER AllowStaleFramework
    Optional switch. Allow continuing with an existing framework checkout that
    cannot be ff-pulled (diverged history). Default behavior is to fail loudly.

.PARAMETER SkipUnblock
    Optional switch. Skip Unblock-File entirely (useful on sync drives that
    lock files during cloud upload).

.PARAMETER GitTimeoutSec
    Optional. Hard timeout on git clone / git pull. Default 300 seconds.

.PARAMETER WhatIf
    Show what would happen without making any changes.

.EXAMPLE
    .\bootstrap.ps1 -ProjectFolder "rk1_pharmacy" -ComponentId "RK1_PHARMACY_JOURNAL" `
                    -SourcePath "C:\incoming\maccabi_rk1"

.EXAMPLE
    .\bootstrap.ps1 -ProjectFolder "demo" -ComponentId "DEMO_COMP" `
                    -SourcePath "C:\src\demo" -ReferenceDocsPath "C:\src\demo_docs" `
                    -Ide vscode -WhatIf

.EXAMPLE
    # Re-run after editing source: refresh Source Code, leave framework alone.
    .\bootstrap.ps1 -ProjectFolder "rk1_pharmacy" -ComponentId "RK1_PHARMACY_JOURNAL" `
                    -SourcePath "C:\incoming\maccabi_rk1_v2" -ForceSource

.NOTES
    Author guidance:
      - PowerShell 7 (pwsh) is strongly recommended. Windows PowerShell 5.1 will
        work for ASCII paths but Hebrew / Unicode parameter values may bind
        incorrectly under the default OEM code page.
      - Run from inside a freshly cloned framework checkout (Scripts\bootstrap.ps1)
        OR pass -FrameworkPath to point at an existing checkout. The script will
        detect whether it is running from inside the canonical framework path and
        avoid a redundant re-clone.
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    # Project directory name: Unicode-friendly (letters, digits, dot, underscore,
    # dash). Spaces and NTFS-illegal chars are rejected at runtime with a clearer
    # message than ValidatePattern would give.
    [Parameter(Mandatory = $true)]
    [string]$ProjectFolder,

    # Component identifier: ASCII only because it lands in filenames.
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9._-]+$')]
    [string]$ComponentId,

    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [string]$ReferenceDocsPath = "",

    [string]$SourceFilter = "*",

    [string[]]$SourceExclude = @(
        '*.csv','*.xlsx','*.xls','*.exe','*.dll','*.zip','*.tar','*.gz',
        '*.7z','*.png','*.jpg','*.jpeg','*.gif','*.pdf'
    ),

    # Optional: append this extension to every copied source file.
    # APPEND mode -- the original name is preserved; the new extension is added
    # as a final suffix (e.g. "QCBLLESRC.SEWKXFKB" -> "QCBLLESRC.SEWKXFKB.cob").
    # If a file already ends with this extension (case-insensitive on NTFS),
    # the file is canonicalized to lowercase suffix but not double-renamed.
    # Pass with leading dot (e.g. ".cob"); a missing leading dot is added.
    # Pass "" (default) to disable renaming.
    [string]$SourceRenameTo = "",

    [string]$ProjectRoot = "C:\projects",

    [string]$FrameworkPath = "",

    [string]$FrameworkRepo = "https://github.com/iliyaruvinsky/enterprise_cidra_framework.git",

    [ValidateSet('cursor', 'vscode')]
    [string]$Ide = "cursor",

    [switch]$SkipIdeLaunch,

    [switch]$ForceSource,

    [switch]$ForceFramework,

    [switch]$AdoptExistingDirectory,

    [switch]$AllowSyncDrive,

    [switch]$AllowStaleFramework,

    [switch]$SkipUnblock,

    [int]$GitTimeoutSec = 300
)

# ---------------------------------------------------------------------------
# Console encoding: force UTF-8 so Hebrew project names / paths render.
# Also flip the active code page (chcp 65001) when running on Windows
# PowerShell 5.1 so the parameter binder accepts non-ASCII paths.
# ---------------------------------------------------------------------------
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
    # chcp only meaningful on Windows. Swallow output silently.
    if ($IsWindows -or $env:OS -eq 'Windows_NT') {
        & chcp.com 65001 | Out-Null
    }
} catch {
    # Encoding adjustments are best-effort; continue without them.
}

$ErrorActionPreference = 'Stop'

# Warn early if running under Windows PowerShell 5.1 with non-ASCII params.
if ($PSVersionTable.PSEdition -ne 'Core') {
    Write-Host "    [INFO] Windows PowerShell 5.1 detected. PowerShell 7 (pwsh) is recommended" -ForegroundColor Yellow
    Write-Host "           for reliable Hebrew / Unicode path handling. Install via:" -ForegroundColor Yellow
    Write-Host "             winget install --id Microsoft.PowerShell -e" -ForegroundColor Yellow
}

# Resolve framework path default lazily (depends on $env:USERNAME at runtime).
if ([string]::IsNullOrWhiteSpace($FrameworkPath)) {
    $FrameworkPath = Join-Path "C:\Users\$env:USERNAME\tools" "enterprise_cidra_framework"
}

# Normalize -SourceRenameTo: ensure leading dot if non-empty; canonicalize to
# lowercase so the EndsWith / idempotency check has a stable target.
if (-not [string]::IsNullOrWhiteSpace($SourceRenameTo)) {
    if (-not $SourceRenameTo.StartsWith('.')) {
        $SourceRenameTo = '.' + $SourceRenameTo
    }
    $SourceRenameTo = $SourceRenameTo.ToLowerInvariant()
}

# Detect whether THIS script is running from inside a framework checkout. If so,
# treat that as the canonical framework location (avoids the cloned-twice
# anti-pattern called out in the runbook review).
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnclosingFramework = Split-Path -Parent $ScriptDir
$looksLikeFrameworkCheckout = (Test-Path -LiteralPath (Join-Path $EnclosingFramework "Agents")) -and `
                              (Test-Path -LiteralPath (Join-Path $EnclosingFramework "Scripts\install.ps1"))
if ($looksLikeFrameworkCheckout) {
    $FrameworkPath = (Resolve-Path -LiteralPath $EnclosingFramework).Path
    $FrameworkAlreadyAtScriptLocation = $true
} else {
    $FrameworkAlreadyAtScriptLocation = $false
}

$Project = Join-Path $ProjectRoot $ProjectFolder
$SourceCodeDir = Join-Path $Project "Source Code"
$ReferenceDir = Join-Path $Project "Reference"

# Per-stage completion sentinels live under .cidra\_bootstrap\ to keep them
# co-located with the framework install and out of the user's view.
$SentinelDir = Join-Path $Project ".cidra\_bootstrap"
$SrcCopyDoneSentinel = Join-Path $SentinelDir "source_copy_complete.json"
$MotwDoneSentinel    = Join-Path $FrameworkPath ".cidra_motw_unblocked"
$InstallDoneSentinel = Join-Path $Project ".cidra\.install_complete"

# Colors
$C_Cyan   = "Cyan"
$C_Green  = "Green"
$C_Yellow = "Yellow"
$C_Red    = "Red"
$C_Gray   = "Gray"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Write-Step {
    param([string]$Number, [string]$Title)
    Write-Host ""
    Write-Host "==[ $Number ]== $Title" -ForegroundColor $C_Cyan
}

function Write-Info {
    param([string]$Message)
    Write-Host "    $Message" -ForegroundColor $C_Gray
}

function Write-Ok {
    param([string]$Message)
    Write-Host "    [OK] $Message" -ForegroundColor $C_Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "    [WARN] $Message" -ForegroundColor $C_Yellow
}

function Write-Err {
    param([string]$Message)
    Write-Host "    [ERR] $Message" -ForegroundColor $C_Red
}

function Test-CommandOnPath {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    return [bool]$cmd
}

# Probe well-known install locations for Cursor / VS Code when the binary is
# not on PATH (winget GUI installers frequently skip PATH on Windows 11).
function Find-IdeExecutable {
    param([ValidateSet('cursor','vscode')] [string]$Name)

    if ($Name -eq 'cursor') {
        # 1. PATH
        $onPath = (Get-Command cursor -ErrorAction SilentlyContinue)
        if ($onPath) { return $onPath.Source }

        # 2. Standard install locations.
        $candidates = @(
            "$env:LOCALAPPDATA\Programs\cursor\resources\app\bin\cursor.cmd",
            "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe",
            "$env:ProgramFiles\Cursor\Cursor.exe"
        )
    } else {
        $onPath = (Get-Command code -ErrorAction SilentlyContinue)
        if ($onPath) { return $onPath.Source }

        $candidates = @(
            "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd",
            "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
            "$env:ProgramFiles\Microsoft VS Code\bin\code.cmd",
            "$env:ProgramFiles\Microsoft VS Code\Code.exe"
        )
    }

    foreach ($c in $candidates) {
        if ($c -and (Test-Path -LiteralPath $c)) { return $c }
    }
    return $null
}

function Invoke-Action {
    # Wrapper that honors -WhatIf via $PSCmdlet.ShouldProcess.
    param(
        [string]$Target,
        [string]$Action,
        [scriptblock]$Block
    )
    if ($PSCmdlet.ShouldProcess($Target, $Action)) {
        & $Block
    } else {
        Write-Info "[WhatIf] Would: $Action -> $Target"
    }
}

function Test-WhatIfMode {
    return [bool]$WhatIfPreference
}

# Single-line sync-drive detector. Returns the friendly name of the sync product
# if detected, else $null.
function Get-SyncDriveLabel {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    $lower = $Path.ToLowerInvariant()
    if ($lower -match '\\onedrive')      { return 'OneDrive' }
    if ($lower -match '\\google drive')  { return 'Google Drive' }
    if ($lower -match '\\my drive')      { return 'Google Drive (My Drive)' }
    if ($lower -match '\\googledrive')   { return 'Google Drive' }
    if ($lower -match '\\dropbox')       { return 'Dropbox' }
    if ($lower -match '\\icloud')        { return 'iCloud' }
    if ($lower -match '\\box sync')      { return 'Box' }
    return $null
}

function Test-ProjectFolderName {
    param([string]$Name)
    # NTFS-illegal: < > : " / \ | ? * and control chars 0-31.
    if ($Name -match '[<>:"/\\|?*\x00-\x1F]') {
        $offending = ($Name.ToCharArray() | Where-Object { $_ -match '[<>:"/\\|?*\x00-\x1F]' }) -join ''
        throw "ProjectFolder contains characters illegal on NTFS: '$offending'"
    }
    if ($Name -match '\s') {
        throw "ProjectFolder must not contain spaces (becomes a directory used in many paths). Got: '$Name'"
    }
    if ($Name -eq '.' -or $Name -eq '..') {
        throw "ProjectFolder cannot be '.' or '..'"
    }
}

function Show-Banner {
    Write-Host ""
    Write-Host "  +--------------------------------------------------+" -ForegroundColor $C_Cyan
    Write-Host "  |          CIDRA Bootstrap (one-shot setup)        |" -ForegroundColor $C_Cyan
    Write-Host "  +--------------------------------------------------+" -ForegroundColor $C_Cyan
    Write-Host ""
    Write-Host "  Project Folder : $ProjectFolder"
    Write-Host "  Component Id   : $ComponentId"
    Write-Host "  Source Path    : $SourcePath"
    if ($ReferenceDocsPath) {
        Write-Host "  Reference Path : $ReferenceDocsPath"
    }
    Write-Host "  Parent Dir     : $ProjectRoot"
    Write-Host "  Project Path   : $Project"
    Write-Host "  Framework Path : $FrameworkPath"
    if (-not [string]::IsNullOrWhiteSpace($SourceRenameTo)) {
        Write-Host "  Rename suffix  : $SourceRenameTo  (APPEND mode)" -ForegroundColor $C_Gray
    }
    if ($FrameworkAlreadyAtScriptLocation) {
        Write-Host "                   (detected: bootstrap is running from this framework)" -ForegroundColor $C_Gray
    }
    Write-Host "  IDE Preferred  : $Ide"
    if (Test-WhatIfMode) {
        Write-Host "  Mode           : WHAT-IF (no changes will be made)" -ForegroundColor $C_Yellow
    }
    Write-Host ""
}

# Run a native command with a hard timeout. Returns @{ Code = N; Output = ... }.
# Used for git so corporate proxies / captive portals cannot hang the script.
function Invoke-NativeWithTimeout {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [int]$TimeoutSec = 300,
        [string]$WorkingDirectory = $null
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath

    # PowerShell 7+ (built on .NET 5+) has ProcessStartInfo.ArgumentList -- a
    # Collection<string> that auto-quotes per-argument. Windows PowerShell 5.1
    # (built on .NET Framework 4.x) does NOT have that property; accessing it
    # silently returns $null. Detect and fall back to a manually-quoted single
    # Arguments string.
    if ($null -ne $psi.ArgumentList) {
        foreach ($a in $ArgumentList) { [void]$psi.ArgumentList.Add($a) }
    } else {
        $quoted = $ArgumentList | ForEach-Object {
            if ($_ -match '[\s"]') {
                '"' + ($_ -replace '"', '\"') + '"'
            } else {
                $_
            }
        }
        $psi.Arguments = ($quoted -join ' ')
    }

    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.UseShellExecute        = $false
    $psi.CreateNoWindow         = $true
    if ($WorkingDirectory) { $psi.WorkingDirectory = $WorkingDirectory }

    $proc = [System.Diagnostics.Process]::Start($psi)
    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()

    if (-not $proc.WaitForExit($TimeoutSec * 1000)) {
        try { $proc.Kill($true) } catch { }
        return @{ Code = -1; Output = "TIMEOUT after $TimeoutSec seconds" }
    }
    $proc.WaitForExit()
    $out = ($stdoutTask.Result + "`n" + $stderrTask.Result).Trim()
    return @{ Code = $proc.ExitCode; Output = $out }
}

# ---------------------------------------------------------------------------
# Top-level trap: any unhandled failure prints recovery guidance.
# ---------------------------------------------------------------------------
trap {
    Write-Host ""
    Write-Err "Bootstrap failed: $($_.Exception.Message)"
    if ($_.InvocationInfo -and $_.InvocationInfo.PositionMessage) {
        Write-Host ""
        Write-Host "  Failure location:" -ForegroundColor $C_Yellow
        $_.InvocationInfo.PositionMessage -split "`n" | ForEach-Object {
            Write-Host "    $_" -ForegroundColor $C_Gray
        }
        if ($_.Exception.GetType().FullName) {
            Write-Host "    Exception type : $($_.Exception.GetType().FullName)" -ForegroundColor $C_Gray
        }
        if ($_.FullyQualifiedErrorId) {
            Write-Host "    Error id       : $($_.FullyQualifiedErrorId)" -ForegroundColor $C_Gray
        }
    }
    Write-Host ""
    Write-Host "  State on disk:" -ForegroundColor $C_Yellow
    Write-Host "    Project        : $Project" -ForegroundColor $C_Gray
    Write-Host "    Framework      : $FrameworkPath" -ForegroundColor $C_Gray
    Write-Host "    Source sentinel: $(if (Test-Path -LiteralPath $SrcCopyDoneSentinel) { 'present' } else { 'absent' })" -ForegroundColor $C_Gray
    Write-Host "    Install sentinel: $(if (Test-Path -LiteralPath $InstallDoneSentinel) { 'present' } else { 'absent' })" -ForegroundColor $C_Gray
    Write-Host ""
    Write-Host "  Recovery:" -ForegroundColor $C_Yellow
    Write-Host "    1. Read the error above." -ForegroundColor $C_Gray
    Write-Host "    2. Re-run the same command. Sentinels make safe steps idempotent;" -ForegroundColor $C_Gray
    Write-Host "       failed steps will be retried automatically." -ForegroundColor $C_Gray
    Write-Host "    3. If retrying does not help, pass -ForceFramework to rebuild" -ForegroundColor $C_Gray
    Write-Host "       .cidra/ and .claude/commands/ from scratch." -ForegroundColor $C_Gray
    Write-Host ""
    exit 1
}

# ---------------------------------------------------------------------------
# 0. Banner + parameter validation
# ---------------------------------------------------------------------------
Test-ProjectFolderName -Name $ProjectFolder

if ($ProjectFolder -ieq $ComponentId) {
    Write-Warn "ProjectFolder and ComponentId are identical ('$ProjectFolder'). This is almost always a mistake."
    Write-Warn "Convention: ProjectFolder is short ASCII (e.g. 'rk1_pharmacy'); ComponentId is the logical"
    Write-Warn "identifier used inside artifacts (e.g. 'RK1_PHARMACY_JOURNAL'). Continuing in 3 seconds..."
    Start-Sleep -Seconds 3
}

Show-Banner

# ---------------------------------------------------------------------------
# 1. Prerequisites - check; do NOT auto-install. Print copy-paste commands.
# ---------------------------------------------------------------------------
Write-Step "1/9" "Checking prerequisites"

$missing = @()

if (-not (Test-CommandOnPath "git")) {
    $missing += [PSCustomObject]@{
        Name    = "Git"
        Install = "winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements"
    }
} else {
    $gitVer = ((git --version) 2>$null)
    Write-Ok "git found: $gitVer"
}

# Probe Cursor / VS Code via PATH then well-known install locations.
$cursorExe = Find-IdeExecutable -Name 'cursor'
$vscodeExe = Find-IdeExecutable -Name 'vscode'
$hasCursor = [bool]$cursorExe
$hasVscode = [bool]$vscodeExe

if (-not $hasCursor -and -not $hasVscode) {
    $missing += [PSCustomObject]@{
        Name    = "Cursor or VS Code"
        Install = "winget install --id Anysphere.Cursor -e --accept-source-agreements --accept-package-agreements`n   (or) winget install --id Microsoft.VisualStudioCode -e --accept-source-agreements --accept-package-agreements"
    }
} else {
    if ($hasCursor) {
        if ((Get-Command cursor -ErrorAction SilentlyContinue)) {
            Write-Ok "cursor found on PATH"
        } else {
            Write-Ok "cursor found at: $cursorExe (not on PATH; will use absolute path)"
        }
    }
    if ($hasVscode) {
        if ((Get-Command code -ErrorAction SilentlyContinue)) {
            Write-Ok "code (VS Code) found on PATH"
        } else {
            Write-Ok "code (VS Code) found at: $vscodeExe (not on PATH; will use absolute path)"
        }
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Err "Missing prerequisites. Install them, then close and reopen PowerShell, and re-run this script:"
    Write-Host ""
    foreach ($m in $missing) {
        Write-Host "  # $($m.Name)" -ForegroundColor $C_Yellow
        Write-Host "  $($m.Install)" -ForegroundColor $C_Yellow
        Write-Host ""
    }
    Write-Host "  After install: CLOSE THIS WINDOW and open a new PowerShell." -ForegroundColor $C_Gray
    Write-Host "  (refreshenv is a Chocolatey helper and does not exist on winget-only machines.)" -ForegroundColor $C_Gray
    exit 1
}

# Soft reminder about the Claude Code extension. The script can't reliably
# verify it without poking at IDE internals, but the user must have it for
# the next step to work.
Write-Info "Reminder: the Claude Code extension must be installed and signed-in inside Cursor / VS Code."
Write-Info "If you have not done that yet, do it before typing /brainstorm at the end."

# ---------------------------------------------------------------------------
# 2. Validate -SourcePath / -ReferenceDocsPath
# ---------------------------------------------------------------------------
Write-Step "2/9" "Validating input paths"
if (-not (Test-Path -LiteralPath $SourcePath)) {
    Write-Err "Source path does not exist: $SourcePath"
    exit 1
}
Write-Ok "Source path exists: $SourcePath"

if ($ReferenceDocsPath -and -not (Test-Path -LiteralPath $ReferenceDocsPath)) {
    Write-Err "Reference docs path does not exist: $ReferenceDocsPath"
    exit 1
}
if ($ReferenceDocsPath) {
    Write-Ok "Reference docs path exists: $ReferenceDocsPath"
}

# ---------------------------------------------------------------------------
# 3. Clone or pull the framework (with health checks + atomic semantics)
# ---------------------------------------------------------------------------
Write-Step "3/9" "Framework repo (clone or pull) with health checks"

$frameworkParent = Split-Path $FrameworkPath -Parent

if ($FrameworkAlreadyAtScriptLocation) {
    Write-Info "Bootstrap is running from $FrameworkPath. Skipping clone (treating this as canonical)."
    # Still optionally pull if it's a git checkout.
    if (Test-Path -LiteralPath (Join-Path $FrameworkPath ".git")) {
        Write-Info "Attempting fast-forward pull..."
        Invoke-Action -Target $FrameworkPath -Action "git pull --ff-only" -Block {
            $r = Invoke-NativeWithTimeout -FilePath "git" -ArgumentList @('-C', $FrameworkPath, 'pull', '--ff-only') -TimeoutSec $GitTimeoutSec
            if ($r.Code -ne 0) {
                Write-Warn "git pull returned $($r.Code). Output:"
                Write-Host $r.Output -ForegroundColor $C_Gray
                if (-not $AllowStaleFramework) {
                    throw "Framework checkout cannot be fast-forwarded. Pass -AllowStaleFramework to continue with the current SHA, or clean it manually."
                }
                Write-Warn "Continuing with current framework SHA because -AllowStaleFramework was passed."
            }
        }
    } else {
        Write-Info "Not a git checkout; treating as manually-placed framework."
    }
} else {
    if (-not (Test-Path -LiteralPath $frameworkParent)) {
        Invoke-Action -Target $frameworkParent -Action "Create framework parent directory" -Block {
            New-Item -ItemType Directory -Path $frameworkParent -Force | Out-Null
        }
    }

    $isGitCheckout = Test-Path -LiteralPath (Join-Path $FrameworkPath ".git")
    $hasInstallScript = Test-Path -LiteralPath (Join-Path $FrameworkPath "Scripts\install.ps1")
    $hasAgents = Test-Path -LiteralPath (Join-Path $FrameworkPath "Agents")
    $looksHealthy = $isGitCheckout -and $hasInstallScript -and $hasAgents

    if ($isGitCheckout -and -not $looksHealthy) {
        # Corrupted checkout: .git/ exists but key files don't. Atomic re-clone.
        Write-Warn "Framework at $FrameworkPath looks corrupted (.git/ present but Scripts/install.ps1 or Agents/ missing)."
        if (-not $ForceFramework) {
            throw "Refusing to silently use a corrupted framework checkout. Pass -ForceFramework to delete and re-clone."
        }
        Invoke-Action -Target $FrameworkPath -Action "Delete corrupted checkout" -Block {
            Remove-Item -LiteralPath $FrameworkPath -Recurse -Force
        }
        $isGitCheckout = $false
    }

    if ($looksHealthy) {
        # Check for dirty / mid-merge state BEFORE pulling.
        $statusR = Invoke-NativeWithTimeout -FilePath "git" -ArgumentList @('-C', $FrameworkPath, 'status', '--porcelain') -TimeoutSec 30
        if ($statusR.Code -ne 0) {
            throw "git status failed at $FrameworkPath. Output: $($statusR.Output)"
        }
        if (-not [string]::IsNullOrWhiteSpace($statusR.Output)) {
            Write-Err "Framework at $FrameworkPath has uncommitted changes or untracked files:"
            Write-Host $statusR.Output -ForegroundColor $C_Gray
            throw "Clean it (git stash / git reset --hard / remove untracked files) or pass -FrameworkPath to a fresh location."
        }
        $mergeHeadR = Invoke-NativeWithTimeout -FilePath "git" -ArgumentList @('-C', $FrameworkPath, 'rev-parse', '--verify', 'MERGE_HEAD') -TimeoutSec 10
        if ($mergeHeadR.Code -eq 0) {
            throw "Framework at $FrameworkPath has a stuck merge in progress. Run 'git -C $FrameworkPath merge --abort' and retry."
        }

        Write-Info "Framework healthy. Pulling latest (timeout ${GitTimeoutSec}s)..."
        Invoke-Action -Target $FrameworkPath -Action "git pull --ff-only" -Block {
            $r = Invoke-NativeWithTimeout -FilePath "git" -ArgumentList @('-C', $FrameworkPath, 'pull', '--ff-only') -TimeoutSec $GitTimeoutSec
            if ($r.Code -ne 0) {
                Write-Warn "git pull returned $($r.Code). Output:"
                Write-Host $r.Output -ForegroundColor $C_Gray
                if (-not $AllowStaleFramework) {
                    throw "Framework checkout cannot be fast-forwarded (diverged history?). Pass -AllowStaleFramework to continue."
                }
                Write-Warn "Continuing with current framework SHA because -AllowStaleFramework was passed."
            }
        }
        Write-Ok "Framework updated at $FrameworkPath"
    } elseif (Test-Path -LiteralPath $FrameworkPath) {
        Write-Warn "Path exists but is not a git checkout: $FrameworkPath"
        if (-not (Test-Path -LiteralPath (Join-Path $FrameworkPath "Scripts\install.ps1"))) {
            throw "Path $FrameworkPath has neither .git/ nor Scripts/install.ps1. Delete it or pass -FrameworkPath to a different location."
        }
        Write-Warn "Treating as manually-placed framework copy. Cannot pull updates."
    } else {
        # Fresh clone via temp-rename for atomicity: a Ctrl+C mid-clone leaves
        # the temp dir, not a half-FrameworkPath at the canonical location.
        $tempClone = "$FrameworkPath.cloning-$([guid]::NewGuid().ToString('N'))"
        Write-Info "Cloning from $FrameworkRepo (timeout ${GitTimeoutSec}s)..."
        Write-Info "(Will prompt for GitHub credentials if the repo is private.)"
        Invoke-Action -Target $FrameworkPath -Action "git clone $FrameworkRepo" -Block {
            $r = Invoke-NativeWithTimeout -FilePath "git" -ArgumentList @('clone', $FrameworkRepo, $tempClone) -TimeoutSec $GitTimeoutSec
            if ($r.Code -ne 0) {
                if (Test-Path -LiteralPath $tempClone) {
                    Remove-Item -LiteralPath $tempClone -Recurse -Force -ErrorAction SilentlyContinue
                }
                throw "git clone failed (exit $($r.Code)). Output: $($r.Output)"
            }
            # Sanity-check the freshly cloned tree BEFORE swapping it in.
            if (-not (Test-Path -LiteralPath (Join-Path $tempClone "Scripts\install.ps1"))) {
                Remove-Item -LiteralPath $tempClone -Recurse -Force -ErrorAction SilentlyContinue
                throw "Clone landed but Scripts\install.ps1 missing - aborting."
            }
            Move-Item -LiteralPath $tempClone -Destination $FrameworkPath
        }
        Write-Ok "Framework cloned to $FrameworkPath"
    }
}

# Sanity-check the framework looks right (regardless of clone vs pull path).
$installScript = Join-Path $FrameworkPath "Scripts\install.ps1"
$agentsDir     = Join-Path $FrameworkPath "Agents"
$commandsDir   = Join-Path $FrameworkPath "Protocols\.claude\commands"

if (-not (Test-WhatIfMode)) {
    if (-not (Test-Path -LiteralPath $installScript)) {
        Write-Err "install.ps1 not found at expected location: $installScript"
        exit 1
    }
    if (-not (Test-Path -LiteralPath $agentsDir)) {
        Write-Err "Agents/ not found in framework: $agentsDir"
        exit 1
    }
    if (-not (Test-Path -LiteralPath $commandsDir)) {
        Write-Warn "Protocols\.claude\commands not found at $commandsDir."
        Write-Warn "Slash commands will not be installed. Check that the framework is up to date."
    }
}

# ---------------------------------------------------------------------------
# 4. Unblock MOTW (selectively, with sentinel)
# ---------------------------------------------------------------------------
Write-Step "4/9" "Unblock Mark-of-the-Web on framework files (selective)"

if ($SkipUnblock) {
    Write-Info "Skipping (-SkipUnblock passed)."
} elseif ((Test-Path -LiteralPath $MotwDoneSentinel) -and -not $ForceFramework) {
    Write-Info "Already unblocked (sentinel present). Skipping. Pass -ForceFramework to redo."
} else {
    Invoke-Action -Target $FrameworkPath -Action "Selective Unblock-File" -Block {
        $unblocked = 0
        $errors = 0
        Get-ChildItem -LiteralPath $FrameworkPath -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
            # Only files actually carrying the Zone.Identifier ADS need work.
            $hasZone = $null
            try {
                $hasZone = Get-Item -LiteralPath $_.FullName -Stream Zone.Identifier -ErrorAction SilentlyContinue
            } catch { }
            if ($hasZone) {
                try {
                    Unblock-File -LiteralPath $_.FullName
                    $unblocked++
                } catch {
                    $errors++
                }
            }
        }
        Write-Ok "Unblocked $unblocked file(s); $errors error(s)."
        # Write sentinel only after a clean pass.
        if ($errors -eq 0) {
            New-Item -ItemType File -Path $MotwDoneSentinel -Force | Out-Null
        }
    }
}

# ---------------------------------------------------------------------------
# 5. Create project directory + subdirs (with collision + sync-drive guards)
# ---------------------------------------------------------------------------
Write-Step "5/9" "Project directory"

# Sync-drive detection by PATH NAME (drive-letter heuristic is too noisy).
$syncLabel = Get-SyncDriveLabel -Path $Project
if ($syncLabel) {
    if ($AllowSyncDrive) {
        Write-Warn "Detected $syncLabel sync path: $Project"
        Write-Warn "Proceeding because -AllowSyncDrive was passed. Pause sync before long agent runs."
    } else {
        Write-Err "Detected $syncLabel sync path: $Project"
        Write-Err "Cloud sync corrupts artifacts during long agent runs (file locks, partial uploads)."
        Write-Err "Recommended: use C:\projects\ instead. To override, pass -AllowSyncDrive AND pause sync first."
        exit 1
    }
}

if (-not (Test-Path -LiteralPath $ProjectRoot)) {
    Invoke-Action -Target $ProjectRoot -Action "Create project root" -Block {
        New-Item -ItemType Directory -Path $ProjectRoot -Force | Out-Null
    }
}

if (-not (Test-Path -LiteralPath $Project)) {
    Invoke-Action -Target $Project -Action "Create project directory" -Block {
        New-Item -ItemType Directory -Path $Project -Force | Out-Null
    }
    Write-Ok "Created $Project"
} else {
    # Existing-directory collision protection: if non-empty AND not already
    # a CIDRA project, demand explicit consent.
    $existingChildren = @(Get-ChildItem -LiteralPath $Project -Force -ErrorAction SilentlyContinue)
    $hasCidra = Test-Path -LiteralPath (Join-Path $Project ".cidra")
    if ($existingChildren.Count -gt 0 -and -not $hasCidra) {
        if (-not $AdoptExistingDirectory) {
            Write-Err "Project directory $Project already exists and contains $($existingChildren.Count) item(s)"
            Write-Err "but no .cidra/ install. Bootstrap will refuse to overwrite an unrelated directory."
            Write-Err "If you really want to use this directory, pass -AdoptExistingDirectory."
            exit 1
        }
        Write-Warn "Adopting existing non-empty directory $Project (-AdoptExistingDirectory passed)."
    } else {
        Write-Info "Project directory already exists: $Project (idempotent re-run)"
    }
}

# Source Code subdir
if (-not (Test-Path -LiteralPath $SourceCodeDir)) {
    Invoke-Action -Target $SourceCodeDir -Action "Create Source Code subdirectory" -Block {
        New-Item -ItemType Directory -Path $SourceCodeDir -Force | Out-Null
    }
    Write-Ok "Created $SourceCodeDir"
} else {
    Write-Info "Source Code\ already exists"
}

# Sentinel directory
if (-not (Test-WhatIfMode) -and -not (Test-Path -LiteralPath $SentinelDir)) {
    New-Item -ItemType Directory -Path $SentinelDir -Force | Out-Null
}

# ---------------------------------------------------------------------------
# 6. Copy source files (literal-path, exclude-list, completion sentinel)
# ---------------------------------------------------------------------------
Write-Step "6/9" "Copy source files"

function Get-SourceManifest {
    param([string]$Root, [string]$Filter, [string[]]$Exclude)
    # NOTE: do NOT use the -File switch here. In Windows PowerShell 5.1, the
    # combination `-LiteralPath + -File + -Filter` fails parameter-set
    # resolution ("Parameter set cannot be resolved using the specified
    # named parameters."). Filter to files via PSIsContainer post-enumeration
    # so the call works on both PS 5.1 and PS 7.
    Get-ChildItem -LiteralPath $Root -Recurse -Filter $Filter -ErrorAction SilentlyContinue | Where-Object {
        if ($_.PSIsContainer) { return $false }
        $file = $_
        $ok = $true
        foreach ($pat in $Exclude) {
            if ($file.Name -like $pat) { $ok = $false; break }
        }
        $ok
    }
}

$expectedFiles = Get-SourceManifest -Root $SourcePath -Filter $SourceFilter -Exclude $SourceExclude
$expectedCount = $expectedFiles.Count
$expectedExcludedCount = (Get-ChildItem -LiteralPath $SourcePath -Recurse -Filter $SourceFilter -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer }).Count - $expectedCount

# Decide whether we can skip the copy: only if a previous run wrote the
# sentinel AND its expected count matches today's enumeration.
$canSkip = $false
$prevRenameTo = $null
$prevSentinelHadRenameField = $false
if ((Test-Path -LiteralPath $SrcCopyDoneSentinel) -and -not $ForceSource) {
    try {
        $prev = Get-Content -LiteralPath $SrcCopyDoneSentinel -Raw | ConvertFrom-Json

        # Detect whether the prior sentinel was written by a pre-feature
        # bootstrap (no RenameTo field) or a feature-aware one (field present,
        # possibly empty). Cannot rely on $null coercion alone: PSCustomObject
        # missing-property semantics differ between PS 5.1 and PS 7.
        if ($prev.PSObject.Properties.Name -contains 'RenameTo') {
            $prevSentinelHadRenameField = $true
            $prevRenameTo = [string]$prev.RenameTo
        } else {
            $prevSentinelHadRenameField = $false
            $prevRenameTo = $null
        }

        $sourceMatches = ($prev.SourcePath -eq $SourcePath)
        $countMatches  = ($prev.ExpectedCount -eq $expectedCount)
        $filterMatches = ($prev.Filter -eq $SourceFilter)

        # RenameTo comparison: missing field on old sentinel is treated as ''
        # (since the old bootstrap could not rename). New runs with an empty
        # -SourceRenameTo match cleanly; new runs WITH -SourceRenameTo on an
        # old project force a re-copy (see message below).
        $effectivePrevRename = if ($prevSentinelHadRenameField) { $prevRenameTo } else { '' }
        $renameMatches = ($effectivePrevRename -eq $SourceRenameTo)

        if ($sourceMatches -and $countMatches -and $filterMatches -and $renameMatches) {
            $canSkip = $true
        } else {
            if (-not $renameMatches) {
                if (-not $prevSentinelHadRenameField) {
                    Write-Warn "Previous run used an older bootstrap that did not record RenameTo."
                    Write-Warn "Current run has -SourceRenameTo '$SourceRenameTo'. Re-copying from source."
                    Write-Warn "If 'Source Code\' contains hand-edits, back them up before continuing."
                } else {
                    Write-Warn "Previous -SourceRenameTo was '$prevRenameTo'; current is '$SourceRenameTo'."
                    if (-not $ForceSource) {
                        throw "Changing -SourceRenameTo between runs requires -ForceSource (so stale renamed files in 'Source Code\' are wiped first to avoid duplicate-detection downstream)."
                    }
                    Write-Warn "Re-copying from source ('-ForceSource' was passed)."
                }
            } else {
                Write-Info "Previous copy sentinel does not match current inputs (source moved or filter changed). Re-copying."
            }
        }
    } catch {
        # Rethrow our explicit -ForceSource guard so it's not swallowed.
        if ($_.Exception.Message -match 'requires -ForceSource') { throw }
        Write-Info "Previous copy sentinel is unreadable. Re-copying."
    }
}

if ($canSkip) {
    Write-Info "Source already copied successfully ($expectedCount file(s)). Skipping. Pass -ForceSource to redo."
} else {
    # Delete the stale sentinel so an interrupted copy is self-healing.
    if (Test-Path -LiteralPath $SrcCopyDoneSentinel) {
        Remove-Item -LiteralPath $SrcCopyDoneSentinel -Force
    }

    # When -SourceRenameTo changes between runs (or pre-feature sentinel -> new
    # rename value), we MUST wipe Source Code\ before recopying. Otherwise
    # stale "QCBLLESRC.X.cob" files from a prior run sit next to the freshly
    # copied "QCBLLESRC.X" and the chunker double-counts.
    $shouldWipeSourceCode = $false
    if (-not [string]::IsNullOrWhiteSpace($SourceRenameTo) -or `
        ($prevSentinelHadRenameField -and -not [string]::IsNullOrWhiteSpace($prevRenameTo))) {
        if ((Test-Path -LiteralPath $SourceCodeDir) -and -not (Test-WhatIfMode)) {
            # Avoid -File switch (PS 5.1 parameter-set issue with -LiteralPath).
            $existing = @(Get-ChildItem -LiteralPath $SourceCodeDir -Recurse -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer })
            if ($existing.Count -gt 0) {
                $shouldWipeSourceCode = $true
            }
        }
    }
    if ($shouldWipeSourceCode) {
        Write-Info "Wiping Source Code\ contents before re-copy (-SourceRenameTo changed or new run with rename suffix)."
        Get-ChildItem -LiteralPath $SourceCodeDir -Recurse -Force -ErrorAction SilentlyContinue |
            Sort-Object -Property FullName -Descending |
            Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
    }

    # Initialize counters in SCRIPT scope so they survive the Invoke-Action
    # scriptblock invocation pattern (& $Block creates a child scope; vars
    # declared inside don't leak out). Sentinel write also happens INSIDE the
    # block as before -- this is belt-and-suspenders for any future refactor
    # that moves the sentinel write outside.
    $script:srcCopied   = 0
    $script:srcRenamed  = 0
    $script:srcSkipped  = 0   # rename skips (collision / MAX_PATH)

    Invoke-Action -Target $SourceCodeDir -Action "Copy source files (literal-path enumeration)" -Block {
        $copied   = 0
        $renamed  = 0
        $skipped  = 0
        $sourceRoot = (Resolve-Path -LiteralPath $SourcePath).Path.TrimEnd('\','/')

        foreach ($f in $expectedFiles) {
            $rel = $f.FullName.Substring($sourceRoot.Length).TrimStart('\','/')
            $dest = Join-Path $SourceCodeDir $rel
            $destDir = Split-Path -LiteralPath $dest -Parent
            if (-not (Test-Path -LiteralPath $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item -LiteralPath $f.FullName -Destination $dest -Force
            $copied++

            # APPEND-rename pass: add -SourceRenameTo as a final suffix when set.
            if (-not [string]::IsNullOrWhiteSpace($SourceRenameTo)) {
                $leaf = Split-Path -LiteralPath $dest -Leaf
                $leafLower = $leaf.ToLowerInvariant()
                $suffixLower = $SourceRenameTo.ToLowerInvariant()

                if ($leafLower.EndsWith($suffixLower)) {
                    # Already ends with the suffix (any case). Canonicalize to
                    # lowercase suffix so source_library_patterns regexes (which
                    # we keep case-insensitive but document as preferring
                    # lowercase) match deterministically. NTFS preserves case
                    # but is case-insensitive on lookup; rename to lowercase
                    # works without collision against itself.
                    if (-not $leaf.EndsWith($SourceRenameTo, [System.StringComparison]::Ordinal)) {
                        $canonical = $leaf.Substring(0, $leaf.Length - $SourceRenameTo.Length) + $SourceRenameTo
                        $canonicalPath = Join-Path $destDir $canonical
                        # Two-step rename to force case change on case-insensitive FS.
                        try {
                            $tmpName = $leaf + '.cidra-case-tmp'
                            Rename-Item -LiteralPath $dest -NewName $tmpName -ErrorAction Stop
                            Rename-Item -LiteralPath (Join-Path $destDir $tmpName) -NewName $canonical -ErrorAction Stop
                        } catch {
                            Write-Warn "Could not canonicalize case for '$leaf': $($_.Exception.Message)"
                            $skipped++
                        }
                    }
                    # else: already canonical lowercase, nothing to do.
                    continue
                }

                $newLeaf = $leaf + $SourceRenameTo
                $newPath = Join-Path $destDir $newLeaf

                # MAX_PATH guard (260 incl. terminator -> 259 usable on PS 5.1
                # without LongPathsEnabled). Skip rather than fail the whole run.
                if ($newPath.Length -gt 259) {
                    Write-Warn "Skipping rename of '$leaf' -- target path would exceed 259 chars ($($newPath.Length))."
                    $skipped++
                    continue
                }

                # Collision guard: refuse to silently overwrite an existing
                # file at the target name. Surface in sentinel; user resolves
                # at the source library.
                if (Test-Path -LiteralPath $newPath) {
                    Write-Warn "Skipping rename of '$leaf' -- target '$newLeaf' already exists in destination."
                    $skipped++
                    continue
                }

                try {
                    Rename-Item -LiteralPath $dest -NewName $newLeaf -ErrorAction Stop
                    $renamed++
                } catch {
                    Write-Warn "Rename failed for '$leaf': $($_.Exception.Message)"
                    $skipped++
                }
            }
        }

        # Propagate counters to script scope so any future sentinel write or
        # diagnostic outside this block sees real numbers, not $null.
        $script:srcCopied  = $copied
        $script:srcRenamed = $renamed
        $script:srcSkipped = $skipped

        if (-not (Test-WhatIfMode)) {
            $manifest = @{
                SchemaVersion  = 2
                SourcePath     = $SourcePath
                Filter         = $SourceFilter
                Exclude        = $SourceExclude
                RenameTo       = $SourceRenameTo
                ExpectedCount  = $expectedCount
                CopiedCount    = $copied
                RenamedCount   = $renamed
                SkippedRenames = $skipped
                ExcludedCount  = $expectedExcludedCount
                CopiedAt       = (Get-Date -Format "o")
            } | ConvertTo-Json -Depth 4
            Set-Content -LiteralPath $SrcCopyDoneSentinel -Value $manifest -Encoding UTF8
        }
        Write-Ok "Copied $copied file(s) to Source Code\. Excluded $expectedExcludedCount file(s) by extension."
        if (-not [string]::IsNullOrWhiteSpace($SourceRenameTo)) {
            Write-Ok "Renamed $renamed file(s) with suffix '$SourceRenameTo' ($skipped skipped due to collision / MAX_PATH)."
        }
        if ($expectedExcludedCount -gt 0) {
            Write-Info "Excluded extensions: $($SourceExclude -join ', '). Pass -SourceExclude @() to disable."
        }
    }
}

# Reference materials -> dedicated Reference\ subdir (not project root).
if ($ReferenceDocsPath) {
    Write-Info "Copying reference materials to $ReferenceDir ..."
    if (-not (Test-Path -LiteralPath $ReferenceDir)) {
        Invoke-Action -Target $ReferenceDir -Action "Create Reference directory" -Block {
            New-Item -ItemType Directory -Path $ReferenceDir -Force | Out-Null
        }
    }
    Invoke-Action -Target $ReferenceDir -Action "Copy reference docs literal-path" -Block {
        $refRoot = $null
        $isContainer = $false
        try {
            $refItem = Get-Item -LiteralPath $ReferenceDocsPath
            $isContainer = $refItem.PSIsContainer
            $refRoot = $refItem.FullName.TrimEnd('\','/')
        } catch {
            throw "Cannot stat reference path: $ReferenceDocsPath"
        }
        if ($isContainer) {
            $refFiles = Get-ChildItem -LiteralPath $ReferenceDocsPath -File -Recurse -ErrorAction SilentlyContinue
            foreach ($f in $refFiles) {
                $rel = $f.FullName.Substring($refRoot.Length).TrimStart('\','/')
                $dest = Join-Path $ReferenceDir $rel
                $destDir = Split-Path -LiteralPath $dest -Parent
                if (-not (Test-Path -LiteralPath $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                Copy-Item -LiteralPath $f.FullName -Destination $dest -Force
            }
            Write-Ok "Reference materials copied ($($refFiles.Count) file(s)) to Reference\"
        } else {
            Copy-Item -LiteralPath $ReferenceDocsPath -Destination $ReferenceDir -Force
            Write-Ok "Reference file copied to Reference\"
        }
    }
}

# Selective Unblock-File on the copied source (only files with Zone.Identifier).
if (-not $SkipUnblock -and -not (Test-WhatIfMode)) {
    Invoke-Action -Target $SourceCodeDir -Action "Selective Unblock-File on copied source" -Block {
        Get-ChildItem -LiteralPath $SourceCodeDir -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
            $hasZone = $null
            try {
                $hasZone = Get-Item -LiteralPath $_.FullName -Stream Zone.Identifier -ErrorAction SilentlyContinue
            } catch { }
            if ($hasZone) {
                Unblock-File -LiteralPath $_.FullName -ErrorAction SilentlyContinue
            }
        }
    }
}

# ---------------------------------------------------------------------------
# 7. Run install.ps1 (child process for reliable exit-code handling)
# ---------------------------------------------------------------------------
Write-Step "7/9" "Run framework installer"

if (Test-WhatIfMode) {
    Write-Info "[WhatIf] Would run: $installScript -ProjectPath $Project $(if ($ForceFramework) { '-Force' })"
} else {
    # Remove a stale install-done sentinel so we don't false-pass verification.
    if (Test-Path -LiteralPath $InstallDoneSentinel) {
        Remove-Item -LiteralPath $InstallDoneSentinel -Force -ErrorAction SilentlyContinue
    }

    $psExe = (Get-Command pwsh -ErrorAction SilentlyContinue)
    if (-not $psExe) {
        $psExe = (Get-Command powershell -ErrorAction SilentlyContinue)
    }
    if (-not $psExe) {
        throw "Neither pwsh nor powershell is on PATH. This should be impossible (you ran this script)."
    }

    $installArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $installScript, '-ProjectPath', $Project)
    if ($ForceFramework) { $installArgs += '-Force' }

    Write-Info "Invoking: $($psExe.Source) $($installArgs -join ' ')"
    $r = Invoke-NativeWithTimeout -FilePath $psExe.Source -ArgumentList $installArgs -TimeoutSec 600
    if ($r.Output) {
        Write-Host $r.Output -ForegroundColor $C_Gray
    }
    if ($r.Code -ne 0) {
        throw "install.ps1 returned exit code $($r.Code)"
    }

    # Write our own install-complete sentinel only after a clean run.
    New-Item -ItemType File -Path $InstallDoneSentinel -Force | Out-Null
    Write-Ok "install.ps1 completed cleanly"
}

# ---------------------------------------------------------------------------
# 8. Verify install (strict)
# ---------------------------------------------------------------------------
Write-Step "8/9" "Verify installation"

if (Test-WhatIfMode) {
    Write-Info "[WhatIf] Would verify .cidra\Agents\ and .claude\commands\"
} else {
    $cidraAgents   = Join-Path $Project ".cidra\Agents"
    $claudeCmdsDir = Join-Path $Project ".claude\commands"

    if (-not (Test-Path -LiteralPath $cidraAgents)) {
        throw ".cidra\Agents not found after install. install.ps1 failed silently or partially."
    }
    $agentDirs = Get-ChildItem -LiteralPath $cidraAgents -Directory -ErrorAction SilentlyContinue
    Write-Ok ".cidra\Agents present ($($agentDirs.Count) agent folder(s))"
    foreach ($a in $agentDirs) {
        Write-Info "  - $($a.Name)"
    }

    # Soft check: which canonical agents are expected. Names are matched
    # case-insensitively because some installs use slightly different casings.
    $expectedAgentTokens = @('CHUNKER', 'DOCUMENTER', 'RECOMMENDER')
    $missingAgents = @()
    foreach ($tok in $expectedAgentTokens) {
        if (-not ($agentDirs | Where-Object { $_.Name -match $tok })) {
            $missingAgents += $tok
        }
    }
    if ($missingAgents.Count -gt 0) {
        Write-Warn "Expected agent folders missing: $($missingAgents -join ', ')"
    }
    if (-not ($agentDirs | Where-Object { $_.Name -match 'BRAINSTORMER' })) {
        Write-Warn "THE_BRAINSTORMER_AGENT folder not found - the /brainstorm command may fail."
    }

    if (-not (Test-Path -LiteralPath $claudeCmdsDir)) {
        throw ".claude\commands not found after install. Slash commands will not autocomplete in the IDE."
    }
    $cmdFiles = Get-ChildItem -LiteralPath $claudeCmdsDir -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue
    Write-Ok ".claude\commands present ($($cmdFiles.Count) command template(s))"
    $expectedEntryPoints = @('brainstorm.md', 'chunk.md', 'document.md', 'recommend.md')
    $missingEntry = @()
    foreach ($e in $expectedEntryPoints) {
        if (-not (Test-Path -LiteralPath (Join-Path $claudeCmdsDir $e))) {
            $missingEntry += $e
        }
    }
    if ($missingEntry.Count -gt 0) {
        Write-Warn "Missing expected entry-point commands: $($missingEntry -join ', ')"
    }
}

# Write the cidra.env.ps1 hint file so Step 10 can dot-source instead of
# requiring the user to re-type values.
if (-not (Test-WhatIfMode)) {
    $envFile = Join-Path $Project "cidra.env.ps1"
    $envContent = @"
# CIDRA project variables - dot-source this file in any new PowerShell session:
#   . .\cidra.env.ps1
# Then `$project, `$component, and `$framework will be defined.

`$projectFolder = "$ProjectFolder"
`$component     = "$ComponentId"
`$projectRoot   = "$ProjectRoot"
`$project       = "$Project"
`$framework     = "$FrameworkPath"

Write-Output "Loaded: projectFolder=`$projectFolder, component=`$component"
Write-Output "        project=`$project"
"@
    Set-Content -LiteralPath $envFile -Value $envContent -Encoding UTF8
    Write-Ok "Wrote cidra.env.ps1 (dot-source it in future shells)"
}

# ---------------------------------------------------------------------------
# 9. Open the IDE (warn loudly on fallback)
# ---------------------------------------------------------------------------
Write-Step "9/9" "Open project in IDE"

if ($SkipIdeLaunch) {
    Write-Info "Skipping IDE launch (-SkipIdeLaunch). Open it manually:"
    Write-Info "  Cursor / VS Code -> File -> Open Folder -> $Project"
} else {
    # Re-probe at launch time (PATH may have shifted since Step 1).
    $launchCursor = Find-IdeExecutable -Name 'cursor'
    $launchVscode = Find-IdeExecutable -Name 'vscode'
    $launched = $false
    $launchedWhich = $null

    function Start-Ide {
        param([string]$ExePath, [string]$ProjectArg)
        # Capture process to surface launch failures.
        try {
            $p = Start-Process -FilePath $ExePath -ArgumentList "`"$ProjectArg`"" -PassThru
            # Give it a brief moment; if it exited non-zero almost immediately, flag it.
            Start-Sleep -Milliseconds 800
            if ($p.HasExited -and $p.ExitCode -ne 0) {
                Write-Warn "IDE process exited immediately with code $($p.ExitCode). Open manually."
                return $false
            }
            return $true
        } catch {
            Write-Warn "Failed to launch $ExePath : $($_.Exception.Message)"
            return $false
        }
    }

    if ($Ide -eq 'cursor') {
        if ($launchCursor) {
            if (Invoke-Action -Target $Project -Action "Launch Cursor" -Block { Start-Ide -ExePath $launchCursor -ProjectArg $Project }) { }
            $launched = $true; $launchedWhich = 'cursor'
        } elseif ($launchVscode) {
            Write-Warn "Requested -Ide cursor, but Cursor is not on PATH or in standard install locations."
            Write-Warn "Falling back to VS Code. The Claude Code extension must be installed there too;"
            Write-Warn "otherwise the next step (/brainstorm) will not work."
            if (Invoke-Action -Target $Project -Action "Launch VS Code (fallback)" -Block { Start-Ide -ExePath $launchVscode -ProjectArg $Project }) { }
            $launched = $true; $launchedWhich = 'vscode (fallback)'
        }
    } else {
        if ($launchVscode) {
            if (Invoke-Action -Target $Project -Action "Launch VS Code" -Block { Start-Ide -ExePath $launchVscode -ProjectArg $Project }) { }
            $launched = $true; $launchedWhich = 'vscode'
        } elseif ($launchCursor) {
            Write-Warn "Requested -Ide vscode, but VS Code is not on PATH or in standard install locations."
            Write-Warn "Falling back to Cursor."
            if (Invoke-Action -Target $Project -Action "Launch Cursor (fallback)" -Block { Start-Ide -ExePath $launchCursor -ProjectArg $Project }) { }
            $launched = $true; $launchedWhich = 'cursor (fallback)'
        }
    }

    if ($launched) {
        Write-Ok "Launched: $launchedWhich"
    } else {
        Write-Warn "Could not auto-launch an IDE. Open it manually:"
        Write-Warn "  File -> Open Folder -> $Project"
    }
}

# ---------------------------------------------------------------------------
# Final message
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "  +--------------------------------------------------+" -ForegroundColor $C_Green
Write-Host "  |          Bootstrap complete                      |" -ForegroundColor $C_Green
Write-Host "  +--------------------------------------------------+" -ForegroundColor $C_Green
Write-Host ""
Write-Host "  Project      : $Project" -ForegroundColor $C_Cyan
Write-Host "  Component Id : $ComponentId" -ForegroundColor $C_Cyan
Write-Host ""
Write-Host "  NEXT STEP - this is a THINKING step, not a script:" -ForegroundColor $C_Yellow
Write-Host ""
Write-Host "    1) In the IDE that just opened, confirm the Claude Code extension is" -ForegroundColor $C_Gray
Write-Host "       installed and you are signed in with your Anthropic account." -ForegroundColor $C_Gray
Write-Host "       (Extensions panel -> search 'Claude Code' -> Install -> Sign in.)" -ForegroundColor $C_Gray
Write-Host ""
Write-Host "    2) Open a Claude Code chat panel:" -ForegroundColor $C_Gray
Write-Host "       - Cursor:  View -> Claude Code  (or Ctrl+L)" -ForegroundColor $C_Gray
Write-Host "       - VS Code: View -> Command Palette -> 'Claude Code: New Chat'" -ForegroundColor $C_Gray
Write-Host ""
Write-Host "    3) In that chat, type:" -ForegroundColor $C_Gray
Write-Host ""
Write-Host "          /brainstorm" -ForegroundColor $C_Green
Write-Host ""
Write-Host "    The brainstormer will ask 3 pivotal questions (Purpose, Audience," -ForegroundColor $C_Gray
Write-Host "    Timeline) and walk you through MISSING_INPUTS.md. Take your time -" -ForegroundColor $C_Gray
Write-Host "    these answers shape every downstream artifact." -ForegroundColor $C_Gray
Write-Host ""
Write-Host "  For later PowerShell steps (e.g. Step 10 packaging) you can recover" -ForegroundColor $C_Gray
Write-Host "  the project variables without re-typing them by dot-sourcing:" -ForegroundColor $C_Gray
Write-Host ""
Write-Host "      cd `"$Project`"" -ForegroundColor $C_Gray
Write-Host "      . .\cidra.env.ps1" -ForegroundColor $C_Gray
Write-Host ""

exit 0
