# Building and Distributing EVE Rebellion

This document explains how to build and distribute the EVE Rebellion game as a standalone Windows executable.

## For End Users

**Download the Executable:**

1. Go to the [Releases](https://github.com/AreteDriver/EVE_Rebellion/releases) page
2. Download the latest `EVE_Rebellion-Windows.zip` file
3. Extract the ZIP file
4. Double-click `EVE_Rebellion.exe` to play!

No Python installation required - the executable contains everything needed to run the game.

## For Developers

### Building the Executable Locally

**Requirements:**
- Windows 7 or later (for Windows builds)
- Python 3.8+
- Git (optional, for cloning the repository)

**Steps:**

1. Clone or download the repository:
   ```bash
   git clone https://github.com/AreteDriver/EVE_Rebellion.git
   cd EVE_Rebellion
   ```

2. Run the build script:
   
   **On Windows:**
   ```cmd
   build_exe.bat
   ```
   
   **On Linux/Mac:**
   ```bash
   chmod +x build_exe.sh
   ./build_exe.sh
   ```

3. The executable will be created in the `dist/` directory

4. Test the executable before distributing:
   ```
   dist\EVE_Rebellion.exe    (Windows)
   dist/EVE_Rebellion        (Linux/Mac)
   ```

### Manual Build Process

If you prefer to build manually:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run PyInstaller with the spec file:
   ```bash
   pyinstaller --clean EVE_Rebellion.spec
   ```

3. Find the executable in `dist/EVE_Rebellion.exe`

### Automated Builds (GitHub Actions)

The repository includes a GitHub Actions workflow that automatically builds the Windows executable when you create a release or push a version tag.

**To trigger an automated build:**

1. **Create a release:**
   - Go to the GitHub repository
   - Click "Releases" → "Create a new release"
   - Create a new tag (e.g., `v1.0.0`)
   - Add release notes
   - Click "Publish release"

2. **Or push a version tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Or manually trigger:**
   - Go to "Actions" tab
   - Select "Build Windows Executable" workflow
   - Click "Run workflow"

The workflow will:
- Build the Windows executable
- Create a ZIP archive
- Upload it as a release asset (if triggered by a release)
- Make it available for download as an artifact

### Customizing the Build

**Modify the spec file** (`EVE_Rebellion.spec`) to:
- Change the executable name
- Add/remove files to include
- Configure console visibility
- Add an icon (requires .ico file)
- Enable/disable UPX compression

**Example: Adding an icon:**

1. Create or obtain a `.ico` file
2. Modify the `exe = EXE(...)` section in `EVE_Rebellion.spec`:
   ```python
   exe = EXE(
       # ... other parameters ...
       icon='path/to/icon.ico',  # Add this line
   )
   ```

**Example: Enabling console for debugging:**

Change `console=False` to `console=True` in the spec file to see debug output.

## Distribution Guidelines

When distributing the executable:

1. **Include a README** - Users should know:
   - Game controls
   - System requirements
   - Where to report bugs
   
2. **Test on a clean Windows machine** - Ensure it runs without dependencies

3. **Consider virus scanning** - Some antivirus may flag PyInstaller executables as suspicious. This is a false positive, but you may want to:
   - Submit the executable to antivirus vendors for whitelisting
   - Include a note in the README about this possibility
   - Provide instructions for building from source as an alternative

4. **License considerations** - See `LICENSE` file for usage rights

5. **Attribution** - This game is inspired by EVE Online (CCP Games). Ensure proper attribution if distributing.

## Troubleshooting Build Issues

### PyInstaller not found

**Solution:** Install PyInstaller:
```bash
pip install pyinstaller
```

### Import errors during build

**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Missing data files in executable

**Solution:** Verify the spec file includes the data directory:
```python
datas = [
    ('data', 'data'),
]
```

### Executable won't run

**Solution:** Try building with console enabled for debugging:
```python
console=True  # in EVE_Rebellion.spec
```

### Large executable size

The executable is large (~30-40 MB) because it includes:
- Python runtime
- Pygame library
- NumPy library
- All game assets

To reduce size:
- Enable UPX compression (enabled by default on Windows)
- Remove unused imports from code
- Consider using PyInstaller's `--exclude-module` for unused libraries

## Support

For issues with:
- **Building the executable** - Open an issue on GitHub
- **Running the executable** - See README.md troubleshooting section
- **Contributing** - See CONTRIBUTING.md

---

*Happy shipping!*
