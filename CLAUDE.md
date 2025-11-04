# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Image to Video Converter** - A single-file Python CLI tool (1,291 lines) that creates videos from static images using the Ken Burns zoom effect. Built with OpenCV for image processing and video encoding.

**Key Stats**:
- 119 automated tests (8 test files) with 88.6% code coverage
- Parallel processing with multiprocessing (2-4x speedup)
- Configuration file support (.imgtovideorc, YAML)
- Video stitching to combine multiple outputs
- Portable executable builds via PyInstaller
- Automated releases with GitHub Actions

## Development Setup

```bash
# Install dependencies (uv recommended)
uv sync --no-install-project

# Run script
uv run python imgToVideo.py [options]

# Quick test
uv run python imgToVideo.py --duration 1 --fps 5 --codec mp4v --extension mp4

# Run tests
uv run pytest tests/ -v
uv run pytest tests/ --cov=imgToVideo --cov-report=html

# Build .exe locally (official releases use GitHub Actions)
uv run pyinstaller --onefile --name imgToVideo imgToVideo.py
```

## Architecture

### Single-File Design
Entire application in `imgToVideo.py` (1,291 lines) for simplicity and portability.

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

**OpenCV & NumPy**: Must use `opencv-python==4.6.0.66` with `numpy<2.0` (incompatibility enforced in dependencies)

**Blur Parameter**: Must be odd number (OpenCV GaussianBlur requirement) - validated with error messages

**Codec Validation**: Creates temporary VideoWriter with test frame because `isOpened()` returns true for some invalid codecs. Checks file size >100 bytes to confirm encoding worked.

**Memory Management**: Never build list of all frames - use generators/iterators. Each frame ~8MB @ 1080p (250 frames = ~2GB). Generator pattern in `frames_from_image()` is critical.

## Code Modification Guidelines

**New Arguments**: Add in `parse_arguments()` (lines 695-824) with `get_default('key', fallback)` for config support. Update README.md if user-facing.

**Image Processing**: Preserve generator pattern, maintain type hints/docstrings, test various aspect ratios, consider memory impact (~8MB per 1080p frame).

**Logging**:
```python
log_info("User-facing")      # Normal mode
log_verbose("Debug")          # Verbose only
log_error("[ERROR] Always")  # All modes
iterator = items if args.quiet else tqdm(items, desc="...", unit="item")
```

**Platform**: Windows uses `[OK]`/`[ERROR]` (no unicode). Quote paths with spaces. Use `os.path.join()` for cross-platform compatibility.

## Known Limitations

1. **Limited codec testing** - Codec validation may miss edge cases on different systems
2. **Monolithic structure** - Single 1,291-line file (intentional for simplicity)
3. **No audio support** - Only generates video without audio tracks
4. **Basic zoom only** - No pan effects or combined movements
5. **No transition effects** - Stitched videos are concatenated without transitions
6. **Alphabetical stitching order** - Videos combined alphabetically, no custom ordering

## Git Commit Conventions

### Commit Message Format

Pattern: Descriptive summary → blank line → detailed explanation → Claude Code attribution

```
Add comprehensive progress indicators with tqdm

Implement real-time progress tracking for both individual image
processing and batch operations.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Version Number Management

**IMPORTANT**: Always update the version number when making changes. The version increment depends on the type of change.

#### Semantic Versioning Rules

Format: `vMAJOR.MINOR.PATCH` (e.g., `v1.2.3`)

- **MAJOR** (`v2.0.0`): Breaking changes (remove flags, change config format)
- **MINOR** (`v1.1.0`): New features (add `--jobs`, config support, stitching)
- **PATCH** (`v1.0.1`): Bug fixes, docs, small optimizations (<50%)

#### Version Workflow

```bash
# 1. Make changes and commit (don't tag yet)
git add . && git commit -m "Add feature..." && git push

# 2. When ready to release, tag and push
git tag v1.1.0 && git push origin v1.1.0
```

**Decision**: Breaking? → MAJOR. New feature? → MINOR. Bug fix? → PATCH.

**Version Tracking**: Git tags (source of truth), README.md (manual), optional `__version__` in code.

## Testing

The project has 119 automated tests with 88.6% code coverage:

**Test Structure** (8 files, 119 tests):
- `test_scale_and_blur.py` - Image scaling and blurring (25 tests)
- `test_frames_from_image.py` - Frame generation (28 tests)
- `test_codec_validation.py` - Codec availability (24 tests)
- `test_config_loading.py` - Config file parsing (16 tests)
- `test_integration.py` - End-to-end workflows (13 tests)
- `test_stitching.py` - Video combining (13 tests)
- `conftest.py` - Shared fixtures and utilities
- `__init__.py` - Test package initialization

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

Automated via GitHub Actions (`.github/workflows/release.yml`). See `.github/RELEASE.md` for details.

**Quick Start**:
```bash
# 1. Test and commit changes
uv run pytest tests/ -v
git add . && git commit -m "Release changes" && git push

# 2. Tag and push
git tag v1.0.0 && git push origin v1.0.0
```

**Workflow** (auto-triggered on `v*` tags):
1. Test Job (Ubuntu) - Run pytest suite with coverage
2. Build Job (Windows) - Build .exe with PyInstaller, generate SHA256
3. Release Job (Ubuntu) - Create GitHub release with .exe and checksums

**Release Assets**:
- `imgToVideo-{version}-windows.exe` (~52MB portable executable)
- `SHA256SUMS.txt` (integrity verification)
