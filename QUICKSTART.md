# Quick Start Guide

Get up and running with EVE Rebellion in under 2 minutes!

## Prerequisites Check

```bash
# Check if you have Python 3.8+
python3 --version

# Should output something like: Python 3.8.x or higher
```

If you don't have Python 3.8+, download it from [python.org](https://www.python.org/downloads/).

## Installation (3 Steps)

### Step 1: Get the Code

```bash
git clone https://github.com/AreteDriver/EVE_Rebellion.git
cd EVE_Rebellion
```

Or download the ZIP and extract it.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Pygame (game engine)
- NumPy (audio synthesis)

### Step 3: Run the Game!

```bash
python main.py
```

That's it! The game should launch.

## First Launch

You'll see:
1. **Main Menu** - Press ENTER to start
2. **Difficulty Selection** - Choose Normal for your first playthrough
3. **Game Start** - You're the Rifter (triangular ship with glowing engines)

## Basic Controls

| Action | Key |
|--------|-----|
| Move | WASD or Arrow Keys |
| Shoot | SPACE or Left Mouse |
| Rockets | SHIFT or Right Mouse |
| Pause | ESC |

## Your First Mission

**Objective**: Survive Stage 1 and collect refugees

1. **Destroy enemies** - Shoot the golden Amarr ships
2. **Collect refugees** - Pick up the white escape pods that drop
3. **Avoid red lasers** - Enemy fire will damage you
4. **Pick up green powerups** - They repair your hull

**Tip**: Keep moving! Don't stay in one place.

## After Stage 1

You'll reach the **Rebel Station** (upgrade screen):
- Spend rescued refugees on upgrades
- Recommended first purchase: **Gyrostabilizer** (faster shooting)
- Then buy **EMP Ammo** to deal with shielded enemies

## Troubleshooting

### "ModuleNotFoundError: No module named 'pygame'"
```bash
pip install pygame numpy
```

### Game is slow/laggy
Edit `constants.py`:
```python
FPS = 30  # Lower from 60
```

### No sound
That's okay! The game works fine without audio. Sound auto-disables if no audio device is found.

### Black screen
Try software rendering:
```bash
SDL_VIDEODRIVER=software python main.py
```

## Next Steps

Once you're comfortable:
- Try different **ammo types** (press 1-5)
- Increase **difficulty** for a challenge
- Read the **full README** for advanced strategies
- Check out the **technical docs** to see how it works

## Tips for Success

1. **Rescue refugees** - They're your currency for upgrades
2. **Dodge lasers** - Weave between enemy fire
3. **Upgrade early** - Better weapons = easier combat
4. **Use rockets sparingly** - They're powerful but limited
5. **Stay on screen** - Don't fly off the edges

## Getting Help

- **Full documentation**: See [README.md](README.md)
- **Controls reference**: Press P to see in-game help (if implemented)
- **Build issues**: See [build-notes/BUILD.md](build-notes/BUILD.md)

---

## Advanced: Configuration

Want to customize the game?

Edit `constants.py`:

```python
# Make yourself invincible for testing
PLAYER_HEALTH = 999999

# Start at a specific stage
START_STAGE = 3

# Adjust difficulty
DIFFICULTY_MULTIPLIERS = {
    'easy': 0.5,  # Make even easier
    # ...
}
```

---

**Enjoy the game! Remember: "We were slaves once. Never again."**

*Having issues? Check the detailed [BUILD.md](build-notes/BUILD.md) or open an issue on GitHub.*
