# GitHub Actions CI/CD Workflows

This repository uses GitHub Actions for automated testing and deployment.

## Workflows

### 1. Test Workflow (`test.yml`)

The test workflow runs automatically on every push and pull request to the `main` branch.

**Triggered by:**
- Push to `main` branch
- Pull requests targeting `main` branch

**What it does:**
1. Sets up Python environments (3.8, 3.9, 3.10, 3.11)
2. Installs dependencies from `requirements.txt`
3. Runs linting with `flake8`:
   - Critical errors (syntax errors, undefined names) will fail the build
   - Style warnings are reported but don't fail the build
4. Runs unit tests with `pytest`

**Matrix Strategy:**
The workflow runs tests across multiple Python versions to ensure compatibility.

### 2. Deployment Workflow (`deploy.yml`)

The deployment workflow builds standalone executables and creates GitHub Releases.

**Triggered by:**
- Pushing a tag starting with `v` (e.g., `v1.0.0`, `v2.1.3`)

**What it does:**
1. Builds the game for three platforms:
   - **Linux**: Creates a `.tar.gz` archive
   - **Windows**: Creates a `.zip` archive with `.exe`
   - **macOS**: Creates a `.zip` archive
2. Uses PyInstaller to create standalone executables
3. Creates a GitHub Release with all three platform builds attached
4. Automatically generates release notes

**How to trigger a release:**

```bash
# Tag a commit with a version number
git tag v1.0.0
git push origin v1.0.0
```

## Running Tests Locally

Install dependencies:
```bash
pip install -r requirements.txt
```

Run tests:
```bash
pytest -v
```

Run linting:
```bash
# Check for critical errors
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Full lint check
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## Building Locally

To build a standalone executable locally:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name MinmatarRebellion main.py
```

The executable will be in the `dist/` directory.

## Dependencies

All project dependencies are defined in `requirements.txt`:

- **Game dependencies:**
  - `pygame>=2.0.0` - Game engine
  - `numpy>=1.20.0` - Sound generation

- **Development dependencies:**
  - `flake8>=6.0.0` - Code linting
  - `pytest>=7.0.0` - Testing framework
  - `pyinstaller>=5.0.0` - Executable packaging

## Test Structure

Tests are located in the `tests/` directory:

- `tests/test_basic.py` - Basic smoke tests for core functionality
  - Pygame initialization
  - Module imports
  - Constants validation
  - Class structure verification

To add new tests, create Python files in the `tests/` directory with names starting with `test_`.

## Workflow Configuration

### Customizing the Test Workflow

Edit `.github/workflows/test.yml` to:
- Add/remove Python versions from the matrix
- Modify linting rules
- Add additional testing steps

### Customizing the Deployment Workflow

Edit `.github/workflows/deploy.yml` to:
- Change PyInstaller build options
- Modify platform targets
- Adjust release naming conventions
- Add additional build artifacts

## Badges

You can add workflow status badges to your README:

```markdown
![Test](https://github.com/AreteDriver/EVE_Rebellion/actions/workflows/test.yml/badge.svg)
![Deploy](https://github.com/AreteDriver/EVE_Rebellion/actions/workflows/deploy.yml/badge.svg)
```

## Troubleshooting

### Tests fail locally but pass in CI (or vice versa)

- Ensure you have the same Python version
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Tests may behave differently on different operating systems

### Deployment fails

- Verify PyInstaller can build locally first
- Check that all required files are included in the repository
- Review the workflow logs in the Actions tab on GitHub

### Release not created

- Ensure you pushed a tag starting with `v`
- Check that the deployment workflow completed successfully
- Verify you have the necessary permissions in the repository
