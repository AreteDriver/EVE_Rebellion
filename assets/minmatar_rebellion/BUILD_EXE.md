# Building Windows .exe

## Method 1: Using PyInstaller (Recommended)

### Step 1: Install PyInstaller
```batch
pip install pyinstaller
```

### Step 2: Build the .exe
Simply run the batch file:
```batch
build_exe.bat
```

Or manually:
```batch
pyinstaller --onefile --windowed --name "MinmatarRebellion" --add-data "svg;svg" --add-data "data;data" main.py
```

### Step 3: Find Your .exe
The executable will be in: `dist/MinmatarRebellion.exe`

You can distribute the entire `dist` folder - it's completely standalone!

## Method 2: Auto2exe (Alternative)

1. Install auto-py-to-exe:
```batch
pip install auto-py-to-exe
```

2. Run the GUI:
```batch
auto-py-to-exe
```

3. Configure:
   - Script Location: `main.py`
   - One File: Yes
   - Console Window: No (Window Based)
   - Additional Files: Add `svg` and `data` folders
   - Click "Convert .py to .exe"

## What Gets Included

The .exe will bundle:
- Python interpreter
- All game code (game.py, sprites.py, etc.)
- Pygame and NumPy libraries
- Ship SVGs
- JSON data files

**Size:** Approximately 40-50 MB

## Testing

After building:
```batch
cd dist
MinmatarRebellion.exe
```

The game should launch without needing Python installed!

## Troubleshooting

**"Missing module" errors:**
- Make sure pygame and numpy are installed: `pip install pygame numpy`

**Game doesn't start:**
- Build with console first (remove `--windowed`) to see errors
- Check that data and svg folders are included

**Large file size:**
- This is normal! It includes Python + all libraries
- Can't be reduced much without breaking functionality

## Distribution

To share your game:
1. Zip the entire `dist` folder
2. Upload to itch.io, Google Drive, or your website
3. Users just unzip and double-click the .exe!

No Python installation required for players! 🎮
