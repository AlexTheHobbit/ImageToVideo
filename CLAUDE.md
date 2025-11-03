# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**ImageToVideo** - A single-file Python CLI tool that creates videos from static images using the Ken Burns zoom effect. Built with OpenCV for image processing and video encoding. Distributed as a

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

### Building Standalone Executable
```bash
# Build portable .exe (~52MB)
uv run pyinstaller --onefile --name imgToVideo imgToVideo.py

# Output: dist/imgToVideo.exe
# Usage: .\dist\imgToVideo.exe -i ./photos -o ./videos
```

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
