# 🚀 EVE Rebellion - Automated GitHub Migration

## What This Does

**ONE COMMAND** sets up your entire multi-repo architecture and solves your GitHub storage problem!

### The Problem
- Your EVE_Rebellion repo is at 475% storage capacity ❌
- 267 ship SVG files eating up space
- Can't push new code without errors

### The Solution
- Split into 2 repos: EVE_Ships (assets) + EVE_Rebellion (code) ✅
- Main game repo drops to <5MB
- Build script auto-pulls needed assets
- Creates AppImage (Linux) + .exe (Windows)

---

## 🎯 Quick Start (2 Steps!)

### Step 1: Run the Migration Script

```bash
chmod +x RUN_THIS.sh
./RUN_THIS.sh
```

**That's it!** The script will:
1. Ask for your GitHub token (optional - for auto-push)
2. Create both repository structures
3. Generate all build scripts
4. Commit everything locally
5. Push to GitHub (if you provided token)

### Step 2: Add Your Files

After the script finishes, you'll have two new repos:

**EVE_Ships** - Add your 267 SVG files:
```bash
cd ~/eve_migration_*/EVE_Ships
# Copy your ship SVGs into ships/ folders
git add ships/
git commit -m "Add ship assets"
git push
```

**EVE_Rebellion** - Add your game code:
```bash
cd ~/eve_migration_*/EVE_Rebellion
# Copy your Python game files (main.py, etc.)
git add .
git commit -m "Add game code"
git push
```

---

## 📋 What Gets Created

### EVE_Ships Repository
```
EVE_Ships/
├── ships/
│   ├── minmatar/     ← Put your Minmatar ships here
│   ├── amarr/        ← Put your Amarr ships here
│   ├── caldari/
│   └── gallente/
├── metadata/
│   └── ship_manifest.json
└── tools/
    └── validate_ships.py
```

### EVE_Rebellion Repository
```
EVE_Rebellion/
├── main.py           ← Your game code
├── build_all.sh      ← Builds AppImage + .exe
├── quick_build.sh    ← Fast dev builds
├── requirements.txt
└── assets/
    └── ships/        ← Auto-filled during build
```

---

## 🔑 GitHub Token (Optional)

If you want auto-push, create a token:

1. Go to: https://github.com/settings/tokens/new
2. Give it a name: "EVE Migration"
3. Select scope: ☑️ **repo** (full control)
4. Click "Generate token"
5. Copy the token
6. Paste when the script asks

**Or skip it** and push manually later!

---

## 🏗️ Build Your Game

Once your code is in place:

```bash
cd ~/eve_migration_*/EVE_Rebellion

# First build (downloads assets from EVE_Ships repo)
./build_all.sh --all

# Outputs:
# - dist/EVE_Rebellion-v2.0-linux.AppImage (~15-25MB)
# - dist/EVE_Rebellion-v2.0-windows.exe (~20-30MB)

# For development (reuses downloaded assets)
./quick_build.sh

# Just run the game
python main.py
```

---

## ✅ What You Get

After running this script:

✅ **EVE_Ships repo** at https://github.com/AreteDriver/EVE_Ships
- Professional asset organization
- 267 ships preserved
- Reusable for future games

✅ **EVE_Rebellion repo** at https://github.com/AreteDriver/EVE_Rebellion  
- Clean <5MB codebase
- Automated build pipeline
- AppImage + Windows distributions

✅ **GitHub storage problem SOLVED**
- No more 475% overrun
- Room to grow
- Professional architecture

---

## 🆘 Troubleshooting

### "Command not found: git"
Install git: `sudo apt install git` (Linux) or download from git-scm.com

### "Permission denied"
Make scripts executable: `chmod +x *.sh`

### "Authentication failed"  
- Check your GitHub token
- Or skip auto-push and push manually later

### "Repository already exists"
The script will clone it and update instead of creating new

### Need help?
Open an issue at: https://github.com/AreteDriver/EVE_Rebellion/issues

---

## 📚 More Info

- **QUICK_REFERENCE.md** - Command cheatsheet
- **SETUP_GUIDE.md** - Detailed manual instructions
- **EVE_Ships/** - Asset repo template
- **EVE_Rebellion/** - Game repo template

---

## 🎮 Ready to Build!

Once setup is complete, you can:

1. ✅ Build for Linux (AppImage)
2. ✅ Build for Windows (.exe)
3. ✅ Upload to GitHub Releases
4. ✅ Distribute to players
5. ✅ Pitch to CCP Games

Your GitHub storage problem is **SOLVED** and you have a professional build pipeline! 🚀

---

**Questions?** Check SETUP_GUIDE.md or the inline script comments.

**Ready?** Run `./RUN_THIS.sh` and let's go! 🎯
