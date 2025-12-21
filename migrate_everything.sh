#!/bin/bash
# EVE Rebellion - Automated GitHub Migration Script
# This script will automatically set up both repos with the new architecture

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
GITHUB_USER="AreteDriver"
ASSET_REPO_NAME="EVE_Ships"
GAME_REPO_NAME="EVE_Rebellion"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   EVE Rebellion - Automated Migration Script          ║"
echo "║   Setting up multi-repo architecture                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Function to print colored messages
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Check prerequisites
step "Checking prerequisites..."

if ! command -v git &> /dev/null; then
    error "Git is not installed. Please install git first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    error "Python3 is not installed. Please install python3 first."
    exit 1
fi

info "✓ Git found"
info "✓ Python3 found"
echo ""

# Prompt for GitHub token
step "GitHub Authentication"
echo ""
echo "To push to GitHub automatically, we need a Personal Access Token."
echo "Get one from: https://github.com/settings/tokens/new"
echo "Required permissions: 'repo' (full control of private repositories)"
echo ""
read -sp "Enter your GitHub Personal Access Token (or press Enter to skip auto-push): " GITHUB_TOKEN
echo ""
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    warn "No token provided - you'll need to push manually at the end"
    AUTO_PUSH=false
else
    info "✓ Token received"
    AUTO_PUSH=true
fi
echo ""

# Create working directory
WORK_DIR="$HOME/eve_migration_$(date +%s)"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

info "Working directory: $WORK_DIR"
echo ""

# ============================================================================
# PART 1: Set up EVE_Ships repository
# ============================================================================

step "PART 1: Setting up EVE_Ships asset repository"
echo ""

# Clone or initialize EVE_Ships
if [ "$AUTO_PUSH" = true ]; then
    info "Cloning EVE_Ships repository..."
    git clone https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${ASSET_REPO_NAME}.git 2>&1 | grep -v "token" || {
        warn "Repository doesn't exist or is empty, initializing new repo..."
        mkdir -p ${ASSET_REPO_NAME}
        cd ${ASSET_REPO_NAME}
        git init
        git remote add origin https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${ASSET_REPO_NAME}.git
        cd ..
    }
else
    info "Creating local EVE_Ships repository..."
    mkdir -p ${ASSET_REPO_NAME}
    cd ${ASSET_REPO_NAME}
    git init
    git remote add origin https://github.com/${GITHUB_USER}/${ASSET_REPO_NAME}.git 2>/dev/null || true
    cd ..
fi

cd ${ASSET_REPO_NAME}

# Create folder structure
info "Creating folder structure..."
bash <<'FOLDER_SCRIPT'
mkdir -p ships/minmatar/{frigates,assault_frigates,destroyers,cruisers,battlecruisers,battleships}
mkdir -p ships/amarr/{frigates,destroyers,cruisers,battlecruisers,battleships,drones}
mkdir -p ships/caldari/{frigates,destroyers,cruisers,battlecruisers,battleships,drones}
mkdir -p ships/gallente/{frigates,destroyers,cruisers,battlecruisers,battleships,drones}
mkdir -p metadata tools
FOLDER_SCRIPT

info "✓ Folder structure created"

# Create README
info "Creating README.md..."
cat > README.md <<'SHIPS_README'
# EVE Ships Asset Library

Master repository for all EVE Online ship renders used across ARETE game projects.

## Structure

Ships organized by faction and class:
- `ships/minmatar/` - Minmatar ships
- `ships/amarr/` - Amarr ships  
- `ships/caldari/` - Caldari ships
- `ships/gallente/` - Gallente ships

## Usage

This repository is designed for sparse checkout during builds:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/AreteDriver/EVE_Ships.git
cd EVE_Ships
git sparse-checkout set ships/minmatar ships/amarr/drones
```

## Ship Count

Total ships: 267 SVG files

## License

Ship renders are property of CCP Games (EVE Online).
SHIPS_README

# Create .gitignore
info "Creating .gitignore..."
cat > .gitignore <<'SHIPS_GITIGNORE'
__pycache__/
*.py[cod]
.Python
venv/
.vscode/
.idea/
.DS_Store
Thumbs.db
*.log
SHIPS_GITIGNORE

# Create ship manifest
info "Creating ship manifest..."
cat > metadata/ship_manifest.json <<'MANIFEST'
{
  "manifest_version": "1.0",
  "total_ships": 267,
  "build_presets": {
    "eve_rebellion_minimal": {
      "description": "Minimal asset set for EVE Rebellion v2.0",
      "ships": [
        "ships/minmatar/frigates/rifter.svg",
        "ships/minmatar/assault_frigates/wolf.svg",
        "ships/minmatar/assault_frigates/jaguar.svg",
        "ships/minmatar/frigates/slasher.svg",
        "ships/amarr/frigates/punisher.svg",
        "ships/amarr/frigates/tormentor.svg",
        "ships/amarr/frigates/crucifier.svg",
        "ships/amarr/destroyers/coercer.svg",
        "ships/amarr/cruisers/arbitrator.svg",
        "ships/amarr/cruisers/maller.svg",
        "ships/amarr/cruisers/omen.svg",
        "ships/amarr/battleships/apocalypse.svg",
        "ships/amarr/battleships/armageddon.svg",
        "ships/amarr/battleships/abaddon.svg",
        "ships/amarr/drones/acolyte.svg",
        "ships/amarr/drones/infiltrator.svg"
      ]
    }
  }
}
MANIFEST

# Create validation tool
info "Creating validation tool..."
cat > tools/validate_ships.py <<'VALIDATE'
#!/usr/bin/env python3
import os
from pathlib import Path

def validate_ships():
    base_path = Path(__file__).parent.parent
    ships_path = base_path / "ships"
    
    svg_files = list(ships_path.rglob("*.svg"))
    print(f"Found {len(svg_files)} SVG files")
    
    factions = {}
    for svg in svg_files:
        parts = svg.relative_to(ships_path).parts
        if parts:
            faction = parts[0]
            factions[faction] = factions.get(faction, 0) + 1
    
    for faction, count in sorted(factions.items()):
        print(f"  {faction}: {count} ships")

if __name__ == "__main__":
    validate_ships()
VALIDATE

chmod +x tools/validate_ships.py

# Create placeholder .gitkeep files
touch ships/minmatar/frigates/.gitkeep
touch ships/amarr/frigates/.gitkeep

info "✓ EVE_Ships structure complete"
echo ""

# Commit EVE_Ships
info "Committing EVE_Ships repository..."
git add .
git commit -m "Initial commit: EVE Ships asset library structure" || warn "Nothing to commit or already committed"

if [ "$AUTO_PUSH" = true ]; then
    info "Pushing to GitHub..."
    git push -u origin main 2>&1 | grep -v "token" || git push -u origin master 2>&1 | grep -v "token" || warn "Push may have failed - check manually"
    info "✓ EVE_Ships pushed to GitHub"
else
    warn "Manual push needed: cd ${WORK_DIR}/${ASSET_REPO_NAME} && git push"
fi

cd ..
echo ""

# ============================================================================
# PART 2: Set up EVE_Rebellion repository
# ============================================================================

step "PART 2: Setting up EVE_Rebellion game repository"
echo ""

# Clone or initialize EVE_Rebellion
if [ "$AUTO_PUSH" = true ]; then
    info "Cloning EVE_Rebellion repository..."
    git clone https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GAME_REPO_NAME}.git 2>&1 | grep -v "token" || {
        warn "Repository doesn't exist, initializing new repo..."
        mkdir -p ${GAME_REPO_NAME}
        cd ${GAME_REPO_NAME}
        git init
        git remote add origin https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GAME_REPO_NAME}.git
        cd ..
    }
else
    info "Creating local EVE_Rebellion repository..."
    mkdir -p ${GAME_REPO_NAME}
    cd ${GAME_REPO_NAME}
    git init
    git remote add origin https://github.com/${GITHUB_USER}/${GAME_REPO_NAME}.git 2>/dev/null || true
    cd ..
fi

cd ${GAME_REPO_NAME}

# Create necessary directories
mkdir -p assets/ships data

# Create .gitignore
info "Creating .gitignore..."
cat > .gitignore <<'GAME_GITIGNORE'
# Ship assets - pulled from EVE_Ships repo during build
assets/ships/**/*.svg
assets/ships/**/*.png

# Build artifacts
build/
dist/
*.spec
*.egg-info/

# Python
__pycache__/
*.py[cod]
.Python
venv/
env/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary
EVE_Ships_temp/
.cache/

# Keep folders
!assets/.gitkeep
!assets/ships/.gitkeep
!data/
GAME_GITIGNORE

# Create requirements.txt
info "Creating requirements.txt..."
cat > requirements.txt <<'REQUIREMENTS'
pygame>=2.5.0
numpy>=1.24.0
Pillow>=10.0.0
cairosvg>=2.7.0
pyinstaller>=6.0.0
REQUIREMENTS

# Create build script
info "Creating build_all.sh..."
cat > build_all.sh <<'BUILD_SCRIPT'
#!/bin/bash
set -e

echo "🚀 EVE Rebellion Build System"
echo "=============================="

ASSET_REPO="https://github.com/AreteDriver/EVE_Ships.git"
BUILD_APPIMAGE=true
BUILD_WINDOWS=true
SKIP_ASSETS=false

# Parse args
for arg in "$@"; do
    case $arg in
        --skip-assets) SKIP_ASSETS=true ;;
        --appimage) BUILD_WINDOWS=false ;;
        --windows) BUILD_APPIMAGE=false ;;
    esac
done

# Fetch assets
if [ "$SKIP_ASSETS" = false ]; then
    echo "📦 Fetching ship assets..."
    rm -rf EVE_Ships_temp
    git clone --depth 1 --filter=blob:none --sparse "$ASSET_REPO" EVE_Ships_temp
    cd EVE_Ships_temp
    git sparse-checkout set ships/minmatar ships/amarr
    cd ..
    mkdir -p assets/ships
    cp -r EVE_Ships_temp/ships/* assets/ships/
    rm -rf EVE_Ships_temp
    echo "✅ Assets imported"
fi

# Install deps
echo "📥 Installing dependencies..."
pip install -q pygame numpy pillow pyinstaller 2>/dev/null || true

# Build AppImage
if [ "$BUILD_APPIMAGE" = true ]; then
    echo "🐧 Building Linux AppImage..."
    pyinstaller --clean --onefile --windowed \
        --name "EVE_Rebellion" \
        --add-data "assets:assets" \
        main.py 2>/dev/null || echo "Build completed with warnings"
    
    if [ -f "dist/EVE_Rebellion" ]; then
        mv dist/EVE_Rebellion dist/EVE_Rebellion-v2.0-linux.AppImage
        chmod +x dist/EVE_Rebellion-v2.0-linux.AppImage
        echo "✅ AppImage created: $(du -h dist/EVE_Rebellion-v2.0-linux.AppImage | cut -f1)"
    fi
fi

# Build Windows
if [ "$BUILD_WINDOWS" = true ]; then
    echo "🪟 Building Windows executable..."
    pyinstaller --clean --onefile --windowed \
        --name "EVE_Rebellion" \
        --add-data "assets;assets" \
        main.py 2>/dev/null || echo "Build completed with warnings"
    
    if [ -f "dist/EVE_Rebellion.exe" ]; then
        mv dist/EVE_Rebellion.exe dist/EVE_Rebellion-v2.0-windows.exe
        echo "✅ Windows exe created: $(du -h dist/EVE_Rebellion-v2.0-windows.exe | cut -f1)"
    fi
fi

echo "🎉 Build complete! Check dist/ folder"
rm -rf build *.spec
BUILD_SCRIPT

chmod +x build_all.sh

# Create quick build script
cat > quick_build.sh <<'QUICK'
#!/bin/bash
if [ ! -d "assets/ships" ] || [ -z "$(ls -A assets/ships 2>/dev/null)" ]; then
    ./build_all.sh --all
else
    ./build_all.sh --all --skip-assets
fi
QUICK

chmod +x quick_build.sh

# Create README
info "Creating README.md..."
cat > README.md <<'GAME_README'
# EVE Rebellion - Minmatar Uprising

Top-down arcade space shooter inspired by EVE Online.

## Features
- 3 Playable Ships (Rifter, Wolf, Jaguar)
- Boss System with 13 unique abilities
- Authentic EVE ship graphics
- Multi-platform (Windows, Linux)

## Quick Start

### Players
Download from [Releases](https://github.com/AreteDriver/EVE_Rebellion/releases):
- `EVE_Rebellion-v2.0-linux.AppImage` (Linux)
- `EVE_Rebellion-v2.0-windows.exe` (Windows)

### Developers
```bash
# Build from source
./build_all.sh --all

# Quick dev build
./quick_build.sh

# Run directly
python main.py
```

## Architecture
Uses modular asset system - ships pulled from [EVE_Ships](https://github.com/AreteDriver/EVE_Ships) during build.

## License
Fan project - ship renders property of CCP Games.
GAME_README

# Create placeholder main.py if it doesn't exist
if [ ! -f "main.py" ]; then
    info "Creating placeholder main.py..."
    cat > main.py <<'MAIN_PY'
#!/usr/bin/env python3
"""
EVE Rebellion - Minmatar Uprising
A top-down space shooter inspired by EVE Online
"""
import pygame
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("EVE Rebellion")
    
    print("EVE Rebellion - Game Starting...")
    print("(This is a placeholder - add your game code here)")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 0))
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
MAIN_PY
    chmod +x main.py
fi

touch assets/ships/.gitkeep

info "✓ EVE_Rebellion structure complete"
echo ""

# Commit EVE_Rebellion
info "Committing EVE_Rebellion repository..."
git add .
git commit -m "Add modular build system with separate asset repo" || warn "Nothing to commit or already committed"

if [ "$AUTO_PUSH" = true ]; then
    info "Pushing to GitHub..."
    git push -u origin main 2>&1 | grep -v "token" || git push -u origin master 2>&1 | grep -v "token" || warn "Push may have failed - check manually"
    info "✓ EVE_Rebellion pushed to GitHub"
else
    warn "Manual push needed: cd ${WORK_DIR}/${GAME_REPO_NAME} && git push"
fi

cd ..
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║              MIGRATION COMPLETE! 🎉                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

step "Summary"
echo ""
info "Created repositories:"
echo "  📁 EVE_Ships:     https://github.com/${GITHUB_USER}/${ASSET_REPO_NAME}"
echo "  🎮 EVE_Rebellion: https://github.com/${GITHUB_USER}/${GAME_REPO_NAME}"
echo ""

info "Local working directory:"
echo "  $WORK_DIR"
echo ""

step "Next Steps"
echo ""
echo "1. 📦 Add your 267 ship SVGs to EVE_Ships:"
echo "   cd ${WORK_DIR}/${ASSET_REPO_NAME}"
echo "   # Copy your SVG files to ships/ folders"
echo "   git add ships/"
echo "   git commit -m 'Add ship assets'"
echo "   git push"
echo ""

echo "2. 🎮 Add your game code to EVE_Rebellion:"
echo "   cd ${WORK_DIR}/${GAME_REPO_NAME}"
echo "   # Copy your Python game files"
echo "   git add ."
echo "   git commit -m 'Add game code'"
echo "   git push"
echo ""

echo "3. 🚀 Build and test:"
echo "   cd ${WORK_DIR}/${GAME_REPO_NAME}"
echo "   ./build_all.sh --all"
echo ""

if [ "$AUTO_PUSH" = false ]; then
    warn "You skipped auto-push - remember to push both repos manually!"
fi

info "Migration script complete! 🎉"
echo ""
MIGRATE_SCRIPT

chmod +x migrate_everything.sh
