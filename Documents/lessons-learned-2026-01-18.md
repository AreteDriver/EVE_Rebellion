# Lessons Learned - GitHub Cleanup Session
**Date:** 2026-01-18

## CI/CD Fixes

### 1. Python Dependency Conflicts (Gorgon)
**Problem:** `starlette>=0.52.0` conflicted with `fastapi>=0.128.0` (requires starlette<0.51.0)

**Solution:** Remove explicit starlette version from requirements.txt - let FastAPI manage its own starlette dependency.

---

### 2. Firebase Initialization in CI (Chefwise)
**Problem:** `Firebase: Error (auth/invalid-api-key)` during Next.js build in CI where env vars aren't set.

**Solution:** Check for API key before initializing Firebase:
```javascript
const canInitialize = !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY;
export const app = canInitialize ? initializeApp(firebaseConfig) : null;
export const auth = app ? getAuth(app) : null;
// ... etc for other services
```

---

### 3. PyGObject Installation in CI (LikX)
**Problem:** System packages (`python3-gi`) not available to `actions/setup-python` Python.

**Solution:** Install via pip with build dependencies:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get install -y \
      libgirepository1.0-dev \
      libcairo2-dev \
      pkg-config \
      python3-dev \
      gir1.2-gtk-3.0

- name: Install test dependencies
  run: pip install "PyGObject<3.50" pycairo
```

**Note:** Pin `PyGObject<3.50` - version 3.50+ requires girepository-2.0 not available on Ubuntu 24.04.

---

### 4. Headless GUI Testing (LikX, Argus_Overview)
**Problem:** GTK/Qt tests fail without display in CI.

**Solution:** Use xvfb (X Virtual Framebuffer):
```yaml
- run: sudo apt-get install -y xvfb
- run: xvfb-run -a pytest tests/
```

For Qt apps, also set:
```yaml
env:
  QT_QPA_PLATFORM: offscreen
```

---

### 5. pynput X11 Connection Errors (Argus_Overview)
**Problem:** `Xlib.error.ConnectionClosedError` - pynput keyboard.Listener needs real X11 even with xvfb.

**Solution:** Mock the listener in tests:
```python
with patch("module.keyboard.Listener"):
    widget._start_recording()
    # test assertions
```

---

### 6. Temp Directory Fallback for Shared Paths (vdc-logistics, vdc-portfolio)
**Problem:** `PermissionError` when trying to create `/shared_data/` directory in CI.

**Solution:** Add fallback to temp directory:
```python
import tempfile

def _get_default_path() -> Path:
    env_path = os.environ.get("MY_PATH")
    if env_path:
        return Path(env_path)

    shared_path = Path("/shared_data/file.db")
    if shared_path.parent.exists():
        return shared_path

    # Fallback for CI/dev
    return Path(tempfile.gettempdir()) / "file.db"
```

---

### 7. Locale Differences in CI (LikX)
**Problem:** Tests expected 2-char language codes but CI returns `'C'` locale.

**Solution:** Update assertions to handle minimal locale:
```python
def test_returns_language_code(self):
    result = get_system_language()
    # Accept 'C' in minimal CI environments
    assert result.islower() or result == "C"
```

---

### 8. Ruff Formatting Issues (Gorgon, Argus_Overview, RedOPS)
**Problem:** CI fails on `ruff format --check` after new code is added.

**Solution:** Always run before committing:
```bash
ruff check . --fix
ruff format .
```

---

## Dependabot Management

### Rebasing Stale PRs
When merging multiple Dependabot PRs that touch the same files (e.g., package-lock.json), later PRs get conflicts.

**Solution:** Request rebases via comment:
```
@dependabot rebase
```

### Safe vs Risky Updates
- **Safe to auto-merge:** Minor/patch versions, CI action updates
- **Review first:** Major version bumps (check breaking changes, verify CI passes)

---

## GitHub CLI Commands Reference

```bash
# List failing CI
gh run list --repo OWNER/REPO --branch main --json conclusion

# View failure logs
gh run view RUN_ID --repo OWNER/REPO --log-failed

# Merge PR
gh pr merge NUM --repo OWNER/REPO --squash --delete-branch

# Request Dependabot rebase
gh pr comment NUM --repo OWNER/REPO --body "@dependabot rebase"

# Delete remote branch
gh api -X DELETE repos/OWNER/REPO/git/refs/heads/BRANCH_NAME

# Search open PRs
gh search prs --owner OWNER --state open --author "app/dependabot"
```

---

## Key Takeaways

1. **CI environments are minimal** - Don't assume system packages, displays, or writable paths exist
2. **Mock external dependencies** - pynput, Firebase, etc. should be mocked in CI tests
3. **Let frameworks manage sub-dependencies** - Don't pin starlette if using FastAPI
4. **Run formatters locally** - Catch ruff/prettier issues before pushing
5. **Batch Dependabot merges carefully** - Merge one at a time or request rebases after conflicts
