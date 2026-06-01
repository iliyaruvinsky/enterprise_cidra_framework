# CIDRA Framework Setup Wizard (PowerShell)
# Version: 1.0.0

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      CIDRA Framework Configuration Wizard               ║" -ForegroundColor Cyan
Write-Host "║  Chunker + Interpreter + Documenter + Recommender + AI  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if update mode
$UPDATE_MODE = $false
if ($args[0] -eq "--update") {
    $UPDATE_MODE = $true
    Write-Host "🔄 Update mode - will preserve existing settings" -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Technology Selection
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "1️⃣  Select Technology" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "  a) SAP (WebDynpro, ABAP, FI/CO, HR, BW)"
Write-Host "  b) AS/400 (RPG, COBOL, CL, DDS)"
Write-Host "  c) React/JavaScript (React, Node.js, TypeScript)"
Write-Host "  d) Python (Django, FastAPI, Flask)"
Write-Host "  e) Custom (I'll configure manually)"
Write-Host ""
$tech_choice = Read-Host "Choose technology [a/b/c/d/e]"

switch ($tech_choice) {
    {$_ -in 'a','A'} { $TECHNOLOGY = "SAP"; $PLUGIN = "sap_plugin.yaml" }
    {$_ -in 'b','B'} { $TECHNOLOGY = "AS400"; $PLUGIN = "as400_plugin.yaml" }
    {$_ -in 'c','C'} { $TECHNOLOGY = "React"; $PLUGIN = "react_plugin.yaml" }
    {$_ -in 'd','D'} { $TECHNOLOGY = "Python"; $PLUGIN = "python_plugin.yaml" }
    {$_ -in 'e','E'} { $TECHNOLOGY = "Custom"; $PLUGIN = "custom_plugin.yaml" }
    default { $TECHNOLOGY = "SAP"; $PLUGIN = "sap_plugin.yaml" }
}

Write-Host "✅ Selected: $TECHNOLOGY" -ForegroundColor Green
Write-Host ""

# Step 2: Project Name
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "2️⃣  Project Name" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
$project_name = Read-Host "Enter project name (e.g., FINANCE_SYSTEM)"

if ([string]::IsNullOrWhiteSpace($project_name)) {
    $project_name = "MY_PROJECT"
}

Write-Host "✅ Project name: $project_name" -ForegroundColor Green
Write-Host ""

# Step 3: Code Location
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "3️⃣  Source Code Location" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
$code_location = Read-Host "Enter source code directory path"

if ([string]::IsNullOrWhiteSpace($code_location)) {
    $code_location = ".\src"
}

Write-Host "✅ Code location: $code_location" -ForegroundColor Green
Write-Host ""

# Step 4: Documentation Language
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "4️⃣  Documentation Language" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "  a) Hebrew (עברית)"
Write-Host "  b) English"
Write-Host ""
$lang_choice = Read-Host "Choose language [a/b]"

switch ($lang_choice) {
    {$_ -in 'a','A'} { $LANGUAGE = "he" }
    {$_ -in 'b','B'} { $LANGUAGE = "en" }
    default { $LANGUAGE = "he" }
}

Write-Host "✅ Language: $LANGUAGE" -ForegroundColor Green
Write-Host ""

# Step 5: Advanced Settings
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "5️⃣  Advanced Settings (Optional)" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
$strict_mode = Read-Host "Enable strict validation mode? [y/N]"

if ($strict_mode -in 'y','Y') {
    $STRICT_MODE = $true
} else {
    $STRICT_MODE = $false
}

$min_score = Read-Host "Minimum quality score (0-100) [100]"
if ([string]::IsNullOrWhiteSpace($min_score)) {
    $min_score = 100
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📝 Generating Configuration..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Generate timestamp
$TIMESTAMP = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

# Create configuration JSON
$config = @{
    project_name = $project_name
    technology = $TECHNOLOGY
    plugin = "Plugins/$PLUGIN"
    code_location = $code_location
    documentation_language = $LANGUAGE
    created_at = $TIMESTAMP
    updated_at = $TIMESTAMP
    
    agents = @{
        the_chunker = @{
            enabled = $true
            strategy = "adaptive"
            chunk_size = "2K-4K tokens"
            optimization = "llm-friendly"
        }
        the_documenter = @{
            enabled = $true
            anti_hallucination = $true
            file_count = 7
            citation_required = $true
            exact_counting = $true
        }
        the_recommender = @{
            enabled = $true
            roi_analysis = $true
            risk_assessment = $true
            multi_criteria = $true
        }
    }
    
    validation = @{
        strict_mode = $STRICT_MODE
        min_quality_score = [int]$min_score
        required_sections = "all"
        code_verification = $true
    }
    
    output = @{
        directory = "./documentation"
        format = "markdown"
        include_validation_reports = $true
    }
}

# Write to file
$config | ConvertTo-Json -Depth 10 | Set-Content .cidra-config.json -Encoding UTF8

Write-Host "✅ Configuration file created: .cidra-config.json" -ForegroundColor Green
Write-Host ""

# Create necessary directories
New-Item -ItemType Directory -Force -Path documentation | Out-Null
New-Item -ItemType Directory -Force -Path chunks | Out-Null
New-Item -ItemType Directory -Force -Path validation | Out-Null

Write-Host "✅ Created directories: documentation/, chunks/, validation/" -ForegroundColor Green
Write-Host ""

# IDE Integration
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "6️⃣  IDE Integration (Optional)" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

$install_vscode = Read-Host "Install VS Code templates? [y/N]"
if ($install_vscode -in 'y','Y') {
    $CIDRA_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    Copy-Item -Recurse "$CIDRA_DIR\Protocols\.vscode" .\.vscode -Force
    Write-Host "✅ VS Code templates installed in .vscode/" -ForegroundColor Green
}

$install_cursor = Read-Host "Install Cursor rules? [y/N]"
if ($install_cursor -in 'y','Y') {
    $CIDRA_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $cursorRulesContent = Get-Content "$CIDRA_DIR\Protocols\.cursorrules" -Encoding UTF8 -Raw
    [System.IO.File]::AppendAllText(
        (Join-Path (Get-Location) ".cursorrules"),
        $cursorRulesContent,
        (New-Object System.Text.UTF8Encoding($false))
    )
    Write-Host "✅ Cursor rules appended to .cursorrules" -ForegroundColor Green
}

$install_claude = Read-Host "Install Claude Code rules? [y/N]"
if ($install_claude -in 'y','Y') {
    $CIDRA_DIR = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    Copy-Item -Recurse "$CIDRA_DIR\Protocols\.claude" .\.claude -Force
    Write-Host "✅ Claude Code rules installed in .claude/" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              ✅ CIDRA Setup Complete!                    ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Configuration Summary:" -ForegroundColor White
Write-Host "  • Project: $project_name"
Write-Host "  • Technology: $TECHNOLOGY"
Write-Host "  • Plugin: $PLUGIN"
Write-Host "  • Language: $LANGUAGE"
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review .cidra-config.json"
Write-Host "  2. Start chunking: @THE_CHUNKER_AGENT analyze $project_name"
Write-Host "  3. Start documenting: @THE_DOCUMENTER_AGENT document [COMPONENT]"
Write-Host ""
Write-Host "📚 Documentation: See Documentation/USER_GUIDE.md" -ForegroundColor Cyan
Write-Host ""

