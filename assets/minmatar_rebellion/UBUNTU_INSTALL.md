# UBUNTU INSTALLATION GUIDE

Complete guide for installing and running Minmatar Rebellion on Ubuntu/Linux.

## System Requirements

- Ubuntu 20.04 or newer (also works on Debian, Mint, Pop!_OS, etc.)
- Python 3.8+
- ~100MB free space
- Graphics drivers with OpenGL support

## Quick Install

```bash
# 1. Install Python and pip (if not already installed)
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 2. Install system dependencies for cairosvg (for EVE ship graphics)
sudo apt install libcairo2-dev libffi-dev pkg-config

# 3. Navigate to the game directory
cd minmatar_rebellion

# 4. Install game dependencies
pip3 install pygame numpy cairosvg

# 5. Run the game!
python3 main.py
```

## Virtual Environment (Recommended)

Using a virtual environment keeps the game dependencies isolated:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install pygame numpy cairosvg

# Run game
python main.py

# When done playing, deactivate
deactivate
```

## Troubleshooting

### "No module named pygame"

```bash
pip3 install pygame numpy cairosvg --user
```

### "ImportError: libcairo.so.2"

Install Cairo library:
```bash
sudo apt install libcairo2 libcairo2-dev
```

### "Permission denied" when installing

Use `--user` flag:
```bash
pip3 install pygame numpy cairosvg --user
```

### Low FPS or laggy graphics

Try disabling vsync:
```bash
# Edit constants.py and set:
VSYNC = False
```

Or run in windowed mode with lower resolution.

### No sound

Sound requires SDL2 mixer:
```bash
sudo apt install libsdl2-mixer-2.0-0
```

You can also disable sound in-game with the 'S' key in the menu.

### SVG ships not loading

Check if cairosvg is installed:
```bash
python3 -c "import cairosvg; print('✓ cairosvg works')"
```

If it fails:
```bash
sudo apt install libcairo2-dev libffi-dev pkg-config python3-dev
pip3 install --upgrade --force-reinstall cairosvg
```

## Alternative: System-wide Install

If you prefer not using virtual environments:

```bash
sudo apt install python3-pygame python3-numpy
pip3 install cairosvg --user
```

## Arch Linux / Manjaro

```bash
sudo pacman -S python python-pygame python-numpy cairo pkgconf
pip install cairosvg --user
python main.py
```

## Fedora / RHEL

```bash
sudo dnf install python3-pygame python3-numpy cairo-devel python3-devel
pip3 install cairosvg --user
python3 main.py
```

## Running from Terminal

```bash
# Make the game executable
chmod +x main.py

# Run directly
./main.py

# Or with python
python3 main.py
```

## Creating a Desktop Shortcut

Create `~/.local/share/applications/minmatar-rebellion.desktop`:

```ini
[Desktop Entry]
Name=Minmatar Rebellion
Comment=EVE Online space shooter
Exec=/full/path/to/minmatar_rebellion/main.py
Icon=/full/path/to/minmatar_rebellion/icon.png
Terminal=false
Type=Application
Categories=Game;
```

## Performance Tips

1. **Fullscreen mode**: Better FPS, run with `--fullscreen` flag
2. **Lower resolution**: Edit `SCREEN_WIDTH` and `SCREEN_HEIGHT` in `constants.py`
3. **Disable effects**: Set `EFFECTS_ENABLED = False` in constants.py
4. **Use dedicated GPU**: For laptops with Nvidia/AMD graphics:
   ```bash
   DRI_PRIME=1 python3 main.py  # AMD
   __NV_PRIME_RENDER_OFFLOAD=1 python3 main.py  # Nvidia
   ```

## Uninstall

```bash
# Remove dependencies (if you want)
pip3 uninstall pygame numpy cairosvg

# Remove save file
rm ~/.minmatar_rebellion_save.json

# Remove the game folder
rm -rf minmatar_rebellion/
```

## Wayland vs X11

The game works on both! If you have issues:

```bash
# Force X11 mode (on Wayland)
export SDL_VIDEODRIVER=x11
python3 main.py

# Or force Wayland
export SDL_VIDEODRIVER=wayland
python3 main.py
```

## Steam Deck / Gaming Handheld

Works great! Install using the Desktop mode:

1. Switch to Desktop Mode
2. Open Konsole (terminal)
3. Follow the "Quick Install" steps above
4. Add as Non-Steam Game

## Building from Source

Already done - this is Python! Just run it directly.

## Need Help?

Check the main README.md or TROUBLESHOOTING.md files.

---

**Tested on:**
- Ubuntu 22.04 LTS ✓
- Ubuntu 24.04 LTS ✓
- Pop!_OS 22.04 ✓
- Linux Mint 21 ✓
- Arch Linux ✓
- Fedora 39 ✓
- Steam Deck (SteamOS) ✓

**Fly safe, capsuleer!** o7
