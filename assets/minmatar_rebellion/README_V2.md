# 🚀 MINMATAR REBELLION v2.0 - JAGUAR EDITION

## EVE Online-Inspired Space Shooter with T2 Ship Progression

**A top-down space shooter featuring actual EVE ship silhouettes, persistent skill point progression, and T2 assault frigates!**

---

## 🎮 QUICK START

### Windows:
1. Extract ZIP
2. Run `INSTALL.bat` (first time only)
3. Run `PLAY_GAME.bat`

### Ubuntu/Linux:
1. Extract ZIP
2. `pip3 install pygame numpy cairosvg`
3. `python3 main.py`

See `UBUNTU_INSTALL.md` for full Linux instructions.

---

## ✨ NEW IN V2.0

### 🛸 THREE PLAYABLE SHIPS

**Rifter** (Base - Always Unlocked)
- Balanced stats
- Good for learning
- Rust-brown hull

**Wolf** (500 SP to unlock) 🔥
- +25% damage
- +20% speed
- +50 armor, +25 hull
- 3-shot spread
- Orange engine glow
- **Playstyle:** Aggressive DPS

**Jaguar** (500 SP to unlock) 🛡️
- +10% damage
- +30% speed (FASTEST!)
- +50 shields, +15 hull
- Blue engine glow
- **Playstyle:** Tank & speed

### 📈 SKILL POINT SYSTEM

**Earn permanent SP from kills:**
- Frigates: 5-8 SP
- Destroyers: 10-15 SP
- Cruisers: 20-25 SP
- Battlecruisers: 50-60 SP
- Battleships: 100-200 SP

**SP multiplied by difficulty:**
- Easy: 0.8x
- Normal: 1.0x
- Hard: 1.3x
- Nightmare: 1.5x

**Unlock Requirements:**
- Each T2 ship: 500 SP
- Progress saved between sessions!
- Saved to: `~/.minmatar_rebellion_save.json`

### 🎯 SHIP SELECTION SCREEN

New pre-mission screen shows:
- All 3 ships with preview sprites
- Lock/unlock status
- Ship stats and bonuses
- Strategy recommendations
- **[U]** to unlock with SP
- **[ENTER]** to launch

### 🌊 PROGRESSIVE WAVE SYSTEM

**Dynamic difficulty scaling:**
- Base enemies: 3
- +1 per wave
- +2 per stage completed
- Health/score scaled by wave and stage

**Stage Progression:**
1. Belt Escape (5 waves) - 1.0x difficulty
2. Patrol Interdiction (7 waves) - 1.2x difficulty
3. Colony Liberation (8 waves) - 1.4x difficulty
4. Gate Assault (10 waves) - 1.6x difficulty
5. Final Push (12 waves) - 2.0x difficulty

### 🎲 RANDOMIZED BOSS BATTLES

**Every playthrough is different!**

**Boss Tiers:**
- **Tier 1:** Coercer, Dragoon, Heretic (Destroyers)
- **Tier 2:** Omen, Maller, Arbitrator, Augoror (Cruisers)
- **Tier 3:** Harbinger, Prophecy, Oracle (Battlecruisers)
- **Tier 4:** Apocalypse, Abaddon, Armageddon (Battleships)

**13 Unique Boss Abilities:**
- Rapid Fire, Beam Sweep, Armor Repair
- Drone Swarm, Interdiction, Neut Pulse
- Energy Transfer, Focused Beam, Combat Drones
- Alpha Strike, Mega Pulse, Omega Strike, Neut Wave

**Boss Features:**
- Enrage mode at <25% health
- Special ability cooldowns
- Tier-based movement patterns
- Enhanced AI

### 📦 13 NEW SHIPS

**Destroyers:**
- Coercer, Dragoon, Heretic

**Cruisers:**
- Omen, Maller, Arbitrator, Augoror

**Battlecruisers:**
- Harbinger, Prophecy, Oracle

**Battleships:**
- Apocalypse, Abaddon, Armageddon

All with actual EVE ship silhouettes!

---

## 🎮 CONTROLS

**Movement:**
- WASD or Arrow Keys

**Combat:**
- Space or Left Click - Fire autocannon
- Shift or Right Click - Fire rocket
- Q or Tab - Cycle ammo types
- 1-5 - Select specific ammo

**UI:**
- ESC - Pause menu
- S - Toggle sound (in menu)

---

## 💣 AMMO TYPES

1. **Titanium Sabot** - Balanced
2. **EMP** - Shield bonus
3. **Phased Plasma** - Armor bonus
4. **Fusion** - High damage
5. **Barrage** - Armor penetration

---

## 🛒 SHOP (Between Stages)

Use rescued refugees as currency:

1. **[1] Gyrostabilizer** - 30 refugees - +50% fire rate
2. **[2] Tracking Computer** - 40 refugees - +30% accuracy
3. **[3] EMP Ammo** - 10 refugees
4. **[4] Phased Plasma** - 10 refugees
5. **[5] Fusion Ammo** - 15 refugees
6. **[6] Barrage Ammo** - 15 refugees
7. **[7] Rocket Capacity** - 20 refugees - +5 rockets
8. **[8] Wolf Upgrade** - 200 refugees - T2 assault frigate
9. **[9] Jaguar Upgrade** - 200 refugees - T2 assault frigate

**Note:** Wolf and Jaguar are mutually exclusive per run!

---

## 📊 GAME FEATURES

### Core Gameplay:
- Top-down space combat
- 5 campaign stages
- Progressive wave system
- Random boss battles
- Shield/Armor/Hull damage system
- 5 tactical ammo types
- Refugee rescue mechanic
- Between-stage shop

### Progression:
- Persistent SP system
- Permanent T2 unlocks
- Difficulty-based SP multipliers
- Progress saved automatically

### Visuals:
- 267 authentic EVE ship silhouettes
- Procedural explosions
- Screen shake effects
- Parallax star field
- Boss health bars

### Audio:
- Procedural sound generation
- Autocannon fire
- Rocket launches
- Laser weapons
- Explosions and pickups
- Toggle with 'S' key

---

## 📁 FILE STRUCTURE

```
minmatar_rebellion/
├── main.py              # Entry point
├── game.py              # Main game loop
├── sprites.py           # All game sprites (✅ T2 ships)
├── constants.py         # Config (✅ all new stats)
├── progression.py       # ✅ SP persistence system
├── ship_loader.py       # SVG loading
├── sounds.py            # Procedural audio
├── requirements.txt     # Dependencies
├── CHANGELOG_V2.md      # ✅ Complete feature list
├── UBUNTU_INSTALL.md    # ✅ Linux guide
├── EVE_SHIPS_README.md  # Ship graphics guide
├── svg/top/            # 267 ship silhouettes
└── [other files]
```

---

## 🔧 SYSTEM REQUIREMENTS

### Minimum:
- Windows 7+ / Ubuntu 20.04+ / macOS 10.14+
- Python 3.8+
- 100MB free space
- Basic graphics with OpenGL

### Recommended:
- Windows 10+ / Ubuntu 22.04+
- Python 3.10+
- Dedicated GPU
- 200MB free space

---

## 🐧 UBUNTU/LINUX SUPPORT

**Fully tested on:**
- Ubuntu 22.04 & 24.04 ✓
- Pop!_OS 22.04 ✓
- Linux Mint 21 ✓
- Arch Linux ✓
- Fedora 39 ✓
- Steam Deck ✓

**Quick Install:**
```bash
sudo apt install python3 python3-pip libcairo2-dev
pip3 install pygame numpy cairosvg
python3 main.py
```

See `UBUNTU_INSTALL.md` for full instructions!

---

## 🎯 STRATEGY TIPS

### Rifter (Base Ship):
- Learn the patterns
- Use all ammo types
- Focus on dodging
- Save refugees for upgrades

### Wolf (Offense):
- Maximize damage output
- Use 3-shot spread
- Play aggressively
- Target bosses quickly

### Jaguar (Defense):
- Tank with shields
- Use speed to reposition
- Hit-and-run tactics
- Survive longer waves

### General Tips:
- **Match ammo to enemy:**
  - EMP for shield ships
  - Plasma for armor ships
  - Fusion for high damage
- **Rescue refugees** - currency for shop
- **Play on harder difficulties** - 1.5x SP!
- **Bosses worth tons of SP** - 100-200 each!

---

## 📈 PROGRESSION PATH

1. **Start:** Play with Rifter
2. **Learn:** Master controls and ammo switching
3. **Earn:** Get 500 SP (a few runs)
4. **Unlock:** Choose Wolf or Jaguar
5. **Master:** Try both playstyles
6. **Dominate:** Tackle Nightmare difficulty!

---

## 🛠️ TROUBLESHOOTING

### "No module named pygame"
```bash
pip install pygame numpy cairosvg
```

### "ImportError: libcairo"
```bash
# Ubuntu:
sudo apt install libcairo2-dev

# Windows: Should work automatically
```

### SVG ships not loading:
- Check cairosvg is installed
- Game falls back to procedural graphics
- Run: `python ship_loader.py` to test

### Low FPS:
- Edit `constants.py`
- Lower `SCREEN_WIDTH` and `SCREEN_HEIGHT`
- Set `VSYNC = False`

### No sound:
- Press 'S' in menu to toggle
- Game works fine without audio

See `WINDOWS_GUIDE.txt` or `UBUNTU_INSTALL.md` for more!

---

## 📜 SAVE FILE LOCATION

**Your progress is saved to:**
- Windows: `C:\Users\YourName\.minmatar_rebellion_save.json`
- Linux: `~/.minmatar_rebellion_save.json`
- Mac: `~/.minmatar_rebellion_save.json`

**Contains:**
- Total SP earned
- Unlocked ships
- Total kills
- Highest stage reached

---

## 🎨 CREDITS

**Game Design & Code:** Your team
**Ship Silhouettes:** EVE Online / CCP Games
**Inspired by:** EVE Online universe

**All ship silhouettes are property of CCP Games.**
This is a fan project created to demonstrate game development concepts.

---

## 📝 VERSION INFO

**Version:** 2.0 - Jaguar Edition
**Release Date:** December 2024
**File Size:** 874 KB (with all 267 ship SVGs!)
**Lines of Code:** ~3,500+

---

## 🚀 NEXT STEPS AFTER INSTALL

1. **Extract the ZIP**
2. **Run installation** (see Quick Start above)
3. **Read CHANGELOG_V2.md** - Full feature list
4. **Start playing!**
5. **Earn 500 SP** to unlock your first T2 ship
6. **Master all three ships** and tackle Nightmare mode!

---

## 📞 NEED HELP?

- Check `WINDOWS_GUIDE.txt` for Windows issues
- Check `UBUNTU_INSTALL.md` for Linux issues
- Check `CHANGELOG_V2.md` for feature details
- Check `EVE_SHIPS_README.md` for ship graphics info

---

**Fly safe, capsuleer!** o7

*For the Minmatar Republic! Freedom through firepower!* 🔥
