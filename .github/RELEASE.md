# Creating Releases

This document explains how to create a new release with the GitHub Actions workflow.

## Automatic Releases

The workflow automatically builds and releases executables when you push a version tag.

### Steps to Create a Release

1. **Ensure all tests pass locally**:
   ```bash
   uv run pytest tests/ -v
   ```

2. **Update version number** (if you have one in your code)

3. **Commit all changes**:
   ```bash
   git add .
   git commit -m "Prepare release v1.0.0"
   git push
   ```

4. **Create and push a version tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

5. **The workflow will automatically**:
   - Run all tests
   - Build Windows .exe
   - Create GitHub release
   - Upload executable and checksums

## Manual Releases

You can also trigger the workflow manually:

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select "Build and Release" workflow
4. Click "Run workflow"
5. Choose the branch
6. Click "Run workflow" button

## Workflow Jobs

### 1. Test Job (Ubuntu)
- Runs on Ubuntu latest
- Installs dependencies with uv
- Runs full pytest suite with coverage
- Must pass before building

### 2. Build Job (Windows)
- Runs on Windows latest
- Builds portable .exe with PyInstaller
- Generates SHA256 checksums
- Uploads artifacts

### 3. Release Job (Ubuntu)
- Only runs for tag pushes
- Creates GitHub release
- Uploads .exe and checksums
- Generates release notes

## Version Naming

Use semantic versioning for tags:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

## Release Assets

Each release includes:
- `imgToVideo-{version}-windows.exe` - Portable Windows executable
- `SHA256SUMS.txt` - Checksums for verification

## Troubleshooting

### Workflow fails on test job
- Check test results in Actions log
- Fix failing tests locally
- Push fixes and re-tag

### Build fails on Windows
- Check PyInstaller logs in Actions
- Test build locally on Windows: `uv run pyinstaller --onefile --name imgToVideo imgToVideo.py`
- Verify all dependencies are in pyproject.toml

### Release not created
- Ensure you pushed a tag (not just committed)
- Check that tag follows `v*` pattern
- Verify GITHUB_TOKEN permissions in repository settings

## Example Release Workflow

```bash
# 1. Make changes and test
git checkout -b feature/new-zoom-effect
# ... make changes ...
uv run pytest tests/ -v
git add .
git commit -m "Add new zoom effect feature"

# 2. Merge to main
git checkout main
git merge feature/new-zoom-effect
git push

# 3. Create release
git tag v1.1.0
git push origin v1.1.0

# 4. Wait for workflow to complete (check Actions tab)
# 5. Release appears at: github.com/yourusername/repo/releases
```

## Notes

- The workflow requires `write` permissions for releases (automatically granted in public repos)
- Artifacts are stored for 7 days even if release fails
- You can download artifacts from the Actions tab to debug issues
