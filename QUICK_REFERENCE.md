# Quick Reference - EVE Rebellion Multi-Repo Setup

## 🎯 What This Does

**Solves your GitHub storage problem** by splitting assets from code:
- Before: 1 repo with 267 SVGs = 475% over storage limit ❌
- After: 2 repos, main game repo <5MB ✅

## 📁 Repository Structure

### EVE_Ships (Asset Library)
```
aretecaresolutions/EVE_Ships
├── ships/
│   ├── minmatar/     ← Your 267 SVG files organized here
│   ├── amarr/
│   ├── caldari/
│   └── gallente/
├── metadata/
│   └── ship_manifest.json  ← Lists which ships to use
└── tools/
    └── validate_ships.py   ← Checks everything
```

### EVE_Rebellion (Game Code)
```
aretecaresolutions/EVE_Rebellion
├── main.py              ← Your game code
├── build_all.sh         ← NEW: Builds AppImage + .exe
├── quick_build.sh       ← NEW: Fast dev builds
└── assets/
    └── ships/           ← Empty! Filled during build
```

## 🚀 Build Process

```bash
# The build script automatically:
1. git clone EVE_Ships (sparse checkout - only needed ships)
2. Copy 16 ships to assets/ships/
3. Build AppImage (Linux)
4. Build .exe (Windows)
5. Clean up temporary files
```

**Result:** 
- AppImage: ~15-25MB
- Windows .exe: ~20-30MB
- Source repo: <5MB

## ⚡ Quick Commands

```bash
# First time setup
./build_all.sh --all

# Daily development
./quick_build.sh

# Build specific platform
./build_all.sh --appimage  # Linux only
./build_all.sh --windows   # Windows only

# Just run the game (after first build)
python main.py
```

## 📦 Ships Included in Build

**Player (3):**
- Rifter, Wolf, Jaguar

**Enemies (11):**
- Frigates: Punisher, Tormentor, Crucifier
- Destroyer: Coercer
- Cruisers: Arbitrator, Maller, Omen
- Battleships: Apocalypse, Armageddon, Abaddon

**Drones (2):**
- Acolyte, Infiltrator

**Background (1):**
- Slasher

= **16 total ships** instead of 267!

## 🔧 Setup Steps

1. **EVE_Ships repo:**
   - Upload the EVE_Ships folder
   - Run `./setup_structure.sh`
   - Copy your 267 SVGs into ships/ folders
   - Commit and push

2. **EVE_Rebellion repo:**
   - Remove all ship SVGs from current repo
   - Upload the new build scripts
   - Update ASSET_REPO URL in build_all.sh
   - Commit and push

3. **Build:**
   - Run `./build_all.sh --all`
   - Distribute the files in dist/

## 🎮 What You Get

✅ GitHub storage problem solved
✅ Professional architecture
✅ AppImage for Linux (Steam Deck ready!)
✅ Windows .exe
✅ <30MB distributions
✅ Can add all 267 ships later without bloat

## 📋 Next Features to Add

From your list:
- [ ] Better weapon/damage visuals
- [ ] Wingman powerup (33% before bosses)
- [ ] Drone waves from Amarr carriers
- [ ] Background ships with parallax
- [ ] Controller support polish
- [ ] Better powerup visuals

All ready to implement with the new structure!

---

**See SETUP_GUIDE.md for detailed instructions**
