# Setup Guide - EVE Rebellion Multi-Repo Architecture

This guide will help you set up the new modular architecture that separates game code from ship assets.

## Overview

We're splitting your project into two repositories:
1. **EVE_Ships** - Asset library (all 267 ship SVGs)
2. **EVE_Rebellion** - Game code (pulls assets during build)

This solves your GitHub storage problem and creates a professional, scalable structure.

## Part 1: Set Up EVE_Ships Repository

### 1.1 Upload the Structure

You've already created the EVE_Ships repo. Now upload these files:

```bash
# In your local EVE_Ships folder
EVE_Ships/
├── README.md
├── .gitignore
├── setup_structure.sh
├── metadata/
│   └── ship_manifest.json
└── tools/
    └── validate_ships.py
```

### 1.2 Organize Your 267 Ship SVGs

Run the setup script to create the folder structure:

```bash
cd EVE_Ships
chmod +x setup_structure.sh
./setup_structure.sh
```

This creates:
```
ships/
├── minmatar/
│   ├── frigates/
│   ├── assault_frigates/
│   ├── destroyers/
│   └── ...
├── amarr/
│   ├── frigates/
│   ├── cruisers/
│   ├── battleships/
│   └── drones/
└── ...
```

### 1.3 Move Your SVG Files

Copy your 267 SVG files into the appropriate folders:

**Example:**
- `rifter.svg` → `ships/minmatar/frigates/rifter.svg`
- `wolf.svg` → `ships/minmatar/assault_frigates/wolf.svg`
- `apocalypse.svg` → `ships/amarr/battleships/apocalypse.svg`

Use the ship manifest (metadata/ship_manifest.json) as a guide for which ships go where.

### 1.4 Validate and Commit

```bash
# Check everything is organized correctly
python3 tools/validate_ships.py

# Should show:
# - Total ship count
# - Ships by faction
# - Repository size

# Commit to GitHub
git add .
git commit -m "Initial commit: 267 EVE ship assets organized by faction"
git push origin main
```

### 1.5 Enable Git LFS (Optional but Recommended)

If your repo is still over the limit:

```bash
git lfs install
git lfs track "*.svg"
git lfs track "*.png"
git add .gitattributes
git commit -m "Add Git LFS for large assets"
git push origin main
```

---

## Part 2: Set Up EVE_Rebellion Repository

### 2.1 Clean Your Existing Repo

**CRITICAL: Back up first!**

```bash
# In your existing EVE_Rebellion repo
# Remove ALL ship SVGs and PNGs
git rm -r assets/ships/*.svg
git rm -r assets/ships/*.png

# Keep the folders but empty
mkdir -p assets/ships
touch assets/ships/.gitkeep

# Commit the cleanup
git commit -m "Remove ship assets - now pulled from EVE_Ships repo"
```

### 2.2 Upload New Build System

Upload these files to your EVE_Rebellion repo:

```
EVE_Rebellion/
├── README.md (new version)
├── .gitignore (new version)
├── requirements.txt
├── build_all.sh (NEW - main build script)
├── quick_build.sh (NEW - dev build)
└── ... (your existing game code)
```

### 2.3 Update Your Repository URL in Build Script

Edit `build_all.sh` and make sure this line is correct:

```bash
ASSET_REPO="https://github.com/aretecaresolutions/EVE_Ships.git"
```

### 2.4 Test the Build System

```bash
# First build - will download assets
chmod +x build_all.sh quick_build.sh
./build_all.sh --all

# Should output:
# - Fetching ships from EVE_Ships repo
# - Building AppImage
# - Building Windows .exe
# - Final files in dist/
```

### 2.5 Commit and Push

```bash
git add .
git commit -m "Add modular build system with separate asset repo"
git push origin main
```

---

## Part 3: Verify Storage Savings

Check your GitHub repo sizes:

**Before:**
- EVE_Rebellion: 100+ MB (over limit)

**After:**
- EVE_Ships: ~50-100MB (all assets, can use Git LFS)
- EVE_Rebellion: <5MB (code only!)

Combined you're way under the limit, and EVE_Rebellion stays lean.

---

## Part 4: Daily Development Workflow

### When developing:

```bash
# Option 1: Quick build (reuses downloaded assets)
./quick_build.sh

# Option 2: Full build (fresh asset download)
./build_all.sh --all

# Option 3: Just run the game
python main.py  # (after assets downloaded once)
```

### When adding new ships:

1. Add SVG to EVE_Ships repo
2. Update `metadata/ship_manifest.json`
3. Commit and push EVE_Ships
4. Update `build_all.sh` in EVE_Rebellion if needed
5. Rebuild

---

## Part 5: Distribution

### For players:

Upload these to your GitHub Releases:
- `dist/EVE_Rebellion-v2.0-linux-x86_64.AppImage`
- `dist/EVE_Rebellion-v2.0-windows.exe`

File sizes should be ~15-30MB each (way smaller than before!)

### For CCP pitch:

You can now say:
- ✅ "Professional asset management system"
- ✅ "Scalable architecture supports 267+ ships"
- ✅ "Modular design for rapid iteration"
- ✅ "Multi-platform build pipeline"

---

## Troubleshooting

### "Git clone failed" during build
- Check your internet connection
- Verify EVE_Ships repo is public
- Ensure git is installed

### "Assets not found"
- Run `./build_all.sh --all` (without --skip-assets)
- Check that EVE_Ships repo has ships in `ships/` folder

### "Build failed"
- Check requirements: `pip install -r requirements.txt`
- Ensure PyInstaller is installed
- Check build output for specific errors

### "Repo still too large"
- Make sure you removed all SVGs from EVE_Rebellion
- Use Git LFS for EVE_Ships
- Consider BFG Repo-Cleaner to purge history

---

## Next Steps

Once this is set up:

1. ✅ GitHub storage problem solved
2. ✅ Professional architecture in place
3. ✅ Ready to add new features:
   - Wingman system
   - Drone waves
   - Background ships
   - Enhanced visuals

4. ✅ Ready for CCP pitch with:
   - Working demo (AppImage + .exe)
   - Professional codebase
   - Scalable asset pipeline

---

## Questions?

- Check README.md in each repo
- Run validation tools
- Review build script comments
- Open GitHub issue if stuck

Good luck! 🚀
