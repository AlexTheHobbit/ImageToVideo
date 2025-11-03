# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Image to Video Converter** - A single-file Python CLI tool (~1,290 lines) that creates videos from static images using the Ken Burns zoom effect. Built with OpenCV for image processing and video encoding.

**Key Stats**:
- 119 automated tests with 88.6% code coverage
- Supports parallel processing with multiprocessing
- Configuration file support (.imgtovideorc, YAML)
- Video stitching to combine multiple outputs
- Portable executable builds via PyInstaller
- Automated releases with GitHub Actions

## Development Setup

### Environment Setup
```bash
# Install dependencies with uv (recommended)
uv sync --no-install-project

# Or with pip
pip install -r requirements.txt
```

### Running the Script
```bash
# Basic usage
uv run python imgToVideo.py [options]

# Quick test (1 second, low fps)
uv run python imgToVideo.py --duration 1 --fps 5 --codec mp4v --extension mp4

# Test modes
uv run python imgToVideo.py --verbose   # Detailed debugging
uv run python imgToVideo.py --quiet     # Errors only
```

### Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=imgToVideo --cov-report=html

# Exclude slow tests
uv run pytest tests/ -v -k "not slow"
```

### Building Locally (Optional)
Releases are built automatically via GitHub Actions, but you can build locally for testing:

```bash
# Build portable .exe (~52MB)
uv run pyinstaller --onefile --name imgToVideo imgToVideo.py

# Output: dist/imgToVideo.exe
# Usage: .\dist\imgToVideo.exe -i ./photos -o ./videos
```

**Note**: Use GitHub Actions for official releases (see Release Process section below).

## Architecture

### Single-File Design
Entire application in `imgToVideo.py` (~1,290 lines) for simplicity and portability.

### Core Components

**Image Processing Pipeline**:
1. `scaleAndBlur()` - Scales image with aspect-ratio preservation and blurred background (lines 65-158)
2. `frames_from_image()` - Generator yielding progressively zoomed frames (lines 160-251)
3. `VideoWriterContext` - Context manager for safe video writing (lines 24-62)

**Video Stitching**: `stitch_videos()` - Combines videos sequentially with validation (lines 351-471)

**Parallel Processing**: `process_single_image()` - Worker function for multiprocessing.Pool (lines 607-693)

**Configuration**: `load_config_file()` - Loads .imgtovideorc or YAML configs (lines 473-604)

**Key Design Decisions**:
- **Generator Pattern**: Yields frames one-by-one (~99% memory reduction: 8MB vs 1.5GB)
- **Adaptive Interpolation**: Auto-selects INTER_CUBIC (upscale) or INTER_AREA (downscale)
- **Codec Validation**: Pre-flight check prevents wasted processing on invalid codecs
- **Type Hints**: Complete typing with `np.ndarray`, `Generator`, etc.

**Logging Levels**:
- `log_info()` - Normal output (suppressed in quiet mode)
- `log_verbose()` - Debug details (verbose mode only)
- `log_error()` - Always shown

## Important Constraints

### OpenCV & NumPy Compatibility
- **Must use `opencv-python==4.6.0.66` with `numpy<2.0`**
- OpenCV 4.6.0.66 is not compatible with NumPy 2.x
- This is enforced in both `pyproject.toml` and `requirements.txt`

### Blur Parameter
- Must be an odd number (OpenCV GaussianBlur requirement)
- Validated at function level with helpful error messages

### Codec Validation
The `validate_codec()` function creates a temporary VideoWriter and writes a test frame because:
- OpenCV's `isOpened()` returns true even for some invalid codecs
- Some codecs accept initialization but fail during encoding
- The function checks file size (>100 bytes) to confirm actual encoding occurred

### Memory Management
When modifying frame generation:
- **Never** build a list of all frames - use generators/iterators
- Each frame is ~8MB @ 1080p, so 250 frames = ~2GB if stored
- The generator pattern in `frames_from_image()` is critical for scalability

## Code Modification Guidelines

### Adding New Command-Line Arguments
1. Add argument in `parse_arguments()` (lines 695-824)
2. Use descriptive help text with defaults
3. Get default from config: `get_default('key', fallback)`
4. Add validation in main execution if needed
5. Update README.md if user-facing

### Modifying Image Processing
When changing `scaleAndBlur()` or `frames_from_image()`:
- Preserve the generator pattern - never store all frames in memory
- Maintain type hints and comprehensive docstrings
- Test with various aspect ratios (wide, narrow, square)
- Consider memory impact (each frame ~8MB @ 1080p)

### Adding Verbosity Levels
Use existing logging functions:
```python
log_info("User-facing message")        # Normal mode
log_verbose("Debug details")           # Verbose only
log_error("[ERROR] Always shown")      # All modes
```

For progress bars:
```python
iterator = items if args.quiet else tqdm(items, desc="Processing", unit="item")
```

## Platform Considerations

**Windows** (primary platform):
- Unicode console: Uses `[OK]`/`[ERROR]` instead of ✓/✗
- Paths with spaces must be quoted

**Cross-Platform**:
- OpenCV and NumPy work on Windows/Linux/macOS
- Path handling uses `os.path.join()` for compatibility

## Common Patterns

### Error Handling
```python
try:
    log_verbose("Detailed step")
    result = process()
    log_info("[OK] Success message")
except ValueError as e:
    log_error(f"[ERROR] Validation failed: {e}")
except RuntimeError as e:
    log_error(f"[ERROR] Processing failed: {e}")
```

### Verbosity-Aware Output
```python
if args.quiet:
    pass  # No output
elif args.verbose:
    print(f"[VERBOSE] Detail")
else:
    tqdm.write(f"Normal message")  # Use tqdm.write with progress bars
```

## Known Limitations

1. **Limited codec testing** - Codec validation may miss edge cases on different systems
2. **Monolithic structure** - Single ~1,290-line file (intentional for simplicity)
3. **No audio support** - Only generates video without audio tracks
4. **Basic zoom only** - No pan effects or combined movements yet
5. **No transition effects** - Stitched videos are concatenated without transitions
6. **Alphabetical stitching order** - Videos combined alphabetically, no custom ordering

## Git Commit Conventions

### Commit Message Format

Follow this pattern:
- Descriptive first line summarizing the change
- Blank line
- Detailed explanation of what changed and why
- Performance impact or benefits when applicable
- Footer with Claude Code attribution

Example:
```
Add comprehensive progress indicators with tqdm

Implement real-time progress tracking for both individual image
processing and batch operations.

Features:
- Overall batch progress
- Per-image frame generation
- Performance metrics

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Version Number Management

**IMPORTANT**: Always update the version number when making changes. The version increment depends on the type of change.

#### Semantic Versioning Rules

Format: `vMAJOR.MINOR.PATCH` (e.g., `v1.2.3`)

**MAJOR version** (`v2.0.0`) - Breaking changes:
- Changes that break backward compatibility
- Removal of features or command-line arguments
- Changes to output format or file structure
- API changes that require user code updates
- **Examples**: Removing `--codec` flag, changing config file format incompatibly

**MINOR version** (`v1.1.0`) - New features:
- New features that don't break existing functionality
- New command-line arguments or options
- Performance improvements (2x or more)
- New major capabilities (parallel processing, video stitching, etc.)
- **Examples**: Adding `--jobs` flag, implementing config file support, adding pan effects

**PATCH version** (`v1.0.1`) - Bug fixes:
- Bug fixes and minor improvements
- Documentation updates
- Refactoring without behavior changes
- Small performance optimizations (<50%)
- Error message improvements
- **Examples**: Fixing codec validation bug, correcting typos, improving error messages

#### Version Update Workflow

**Every commit should include a version consideration**:

```bash
# 1. Make your changes
# ... edit files ...

# 2. Determine version increment
# - Breaking change? → MAJOR
# - New feature? → MINOR
# - Bug fix or minor improvement? → PATCH

# 3. Commit changes (don't tag yet)
git add .
git commit -m "Add pan effects feature

Implement horizontal and vertical pan directions alongside zoom.

Features:
- --pan-direction flag (left, right, up, down)
- Combined zoom + pan support
- Random pan option

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
"

# 4. Push to main/branch
git push

# 5. When ready to release, create and push tag
git tag v1.1.0  # Minor version bump for new feature
git push origin v1.1.0
```

#### Quick Version Decision Guide

Ask yourself:
1. **Did I break anything?** → MAJOR (v2.0.0)
2. **Did I add something new?** → MINOR (v1.1.0)
3. **Did I fix or improve existing functionality?** → PATCH (v1.0.1)

#### Special Cases

- **Multiple changes in one commit**: Use the highest applicable version increment
  - Bug fix + new feature → MINOR
  - New feature + breaking change → MAJOR

- **Work-in-progress**: Don't tag until ready for release
  - Make commits normally without tags
  - Create version tag only when ready to publish

- **Hotfixes**:
  - Branch from last release tag
  - Fix bug
  - Increment PATCH version
  - Example: `v1.2.3` → `v1.2.4`

#### Version Tracking

Current version can be tracked in:
- Git tags (source of truth)
- README.md (update manually in commit)
- Optionally: Add `__version__ = "1.0.0"` to imgToVideo.py

**Template for version-aware commits**:
```bash
# Bug fix example
git commit -m "Fix codec validation for edge cases

Resolves issue where some codecs passed validation but failed encoding.

Changes:
- Increase minimum file size check to 100 bytes
- Add stderr capture for OpenCV warnings

Fixes #123

Version: 1.0.1 (patch - bug fix)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
"
```

## Testing

The project has 119 automated tests with 88.6% code coverage:

**Test Structure**:
- `tests/test_scale_and_blur.py` - Image scaling and blurring (25 tests)
- `tests/test_frames_from_image.py` - Frame generation (28 tests)
- `tests/test_codec_validation.py` - Codec availability (24 tests)
- `tests/test_config_loading.py` - Config file parsing (16 tests)
- `tests/test_integration.py` - End-to-end workflows (13 tests)
- `tests/test_stitching.py` - Video combining (13 tests)
- `tests/conftest.py` - Shared fixtures and utilities

**Test Markers**:
- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Full workflow tests
- `@pytest.mark.slow` - Long-running tests (skippable)
- `@pytest.mark.requires_codec` - Tests needing specific codecs

**Before committing**:
1. Run full test suite: `uv run pytest tests/ -v`
2. Check coverage: `uv run pytest tests/ --cov=imgToVideo --cov-report=html`
3. Verify coverage ≥85%
4. Update README.md if user-facing changes

## Release Process

Releases are fully automated via GitHub Actions (`.github/workflows/release.yml`).

### Creating a New Release

```bash
# 1. Ensure all tests pass locally
uv run pytest tests/ -v

# 2. Commit all changes
git add .
git commit -m "Prepare release v1.0.0"
git push

# 3. Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### What Happens Automatically

When you push a version tag (format: `v*`), GitHub Actions will:

1. **Test Job** (Ubuntu)
   - Run full pytest suite with coverage
   - Must pass before building

2. **Build Job** (Windows)
   - Build `imgToVideo-v1.0.0-windows.exe` with PyInstaller
   - Generate SHA256 checksums for verification
   - Upload artifacts (retained 7 days)

3. **Release Job** (Ubuntu, tags only)
   - Create GitHub release with auto-generated notes
   - Upload .exe and checksums
   - Include documentation links

### Manual Workflow Trigger

You can also trigger builds manually without creating a release:
- Go to Actions tab on GitHub
- Select "Build and Release" workflow
- Click "Run workflow"

### Version Naming

Use semantic versioning:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

### Release Assets

Each release includes:
- `imgToVideo-{version}-windows.exe` - Portable Windows executable (~52MB)
- `SHA256SUMS.txt` - Checksums for integrity verification
- Auto-generated release notes with features and links

See `.github/RELEASE.md` for detailed release documentation.
