# Changelog

All notable changes to Minmatar Rebellion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-08

### Added
- `requirements.txt` for easy dependency management
- `setup.py` for package installation support
- `MANIFEST.in` for proper package data inclusion
- `progression.py` module for save game functionality
- `run.sh` and `run.bat` convenience scripts for launching the game
- `CHANGELOG.md` to track project changes
- Multiple installation methods in README

### Changed
- Updated `core/loader.py` to use Python 3.8 compatible type hints (Dict instead of dict)
- Enhanced README with comprehensive installation instructions
- Improved `main.py` to include a proper `main()` entry point function
- Updated `.gitignore` to exclude distribution archives (*.zip, *.tar.gz)

### Fixed
- Python 3.8 compatibility issues with type annotations
- Missing progression module dependency for upgrade_screen.py

### Removed
- Removed `minmatar_rebellion_v2_updated.zip` from git tracking (kept locally, excluded via .gitignore)

## [1.0.0] - Initial Release

### Added
- Initial game release with procedural graphics and sound
- 5 difficulty levels (Easy, Normal, Hard, Nightmare)
- 5 ammo types with tactical mechanics
- Upgrade system using rescued refugees
- 5 game stages with boss battles
- Advanced enemy AI with multiple movement patterns
- Screen shake effects
- Procedural sound generation
- Ambient space music
