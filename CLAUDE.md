# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Image to Video Converter - A single-file Python CLI tool that creates videos from static images using the Ken Burns zoom effect. The project uses OpenCV for image processing and video encoding, with a focus on user experience.

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

# With test images (adjust paths as needed)
uv run python imgToVideo.py -i ./photos -o ./videos --codec mp4v --extension mp4

# Test modes
uv run python imgToVideo.py --verbose   # Detailed debugging output
uv run python imgToVideo.py --quiet     # Silent mode (errors only)
```

### Testing Changes
The project now has a comprehensive automated test suite with 119 tests and 88.6% code coverage.

**Running tests**:
```bash
# Run all tests
uv run pytest tests/ -v

# Run unit tests only
uv run pytest tests/ -v -m unit

# Run integration tests only
uv run pytest tests/ -v -m integration

# Run with coverage report
uv run pytest tests/ --cov=imgToVideo --cov-report=html

# Exclude slow tests
uv run pytest tests/ -v -k "not slow"
```

**Manual testing workflow** (for quick verification):
```bash
# Quick test (1 second, low fps)
uv run python imgToVideo.py --duration 1 --fps 5 --codec mp4v --extension mp4

# Verify verbose mode
uv run python imgToVideo.py --verbose --duration 1 --fps 5 --codec mp4v --extension mp4

# Verify quiet mode (no output except errors)
uv run python imgToVideo.py --quiet --duration 1 --fps 5 --codec mp4v --extension mp4

# Test codec validation with invalid codec
uv run python imgToVideo.py --codec FAKE --extension mp4
```

### Building Standalone Executable
The project can be built into a portable .exe file using PyInstaller, which bundles Python and all dependencies.

**Build the executable**:
```bash
# Install PyInstaller (already in dev dependencies)
uv sync --no-install-project

# Build with PyInstaller
uv run pyinstaller --onefile --name imgToVideo imgToVideo.py

# The executable will be created at: dist/imgToVideo.exe
```

**Using the executable**:
```bash
# The .exe is completely standalone - no Python installation required
.\dist\imgToVideo.exe --help

# Example usage
.\dist\imgToVideo.exe -i ./photos -o ./videos --codec mp4v --extension mp4
```

**Build details**:
- Output: `dist/imgToVideo.exe` (~52MB)
- Configuration: `imgToVideo.spec` (auto-generated, can be customized)
- Build artifacts: `build/` directory (can be deleted after build)
- The executable is portable and can be distributed without any dependencies

**Customizing the build**:
Edit `imgToVideo.spec` to customize the build process, then rebuild:
```bash
uv run pyinstaller imgToVideo.spec
```

## Architecture

### Single-File Design
The entire application is in `imgToVideo.py` (~956 lines). This is intentional for simplicity and portability.

### Core Components

**Image Processing Pipeline**:
1. `scaleAndBlur()` - Prepares image with aspect-ratio-preserving scaling and blurred background (lines 103-158)
2. `frames_from_image()` - Generator that yields progressively zoomed frames (memory-efficient) (lines 219-251)
3. Main loop - Streams frames directly to VideoWriter

**Video Stitching Pipeline**:
1. `stitch_videos()` - Combines multiple video files sequentially (lines 351-471)
2. Frame dimension validation ensures consistent output
3. Progress tracking across multiple videos
4. Automatic cleanup on error

**Key Design Decisions**:
- **Generator Pattern**: `frames_from_image()` yields frames one at a time instead of building a list
  - Memory reduction: ~99% (8MB vs 1.5GB for typical video)
  - Critical for long videos (60s @ 30fps would be ~14GB if stored in memory)
- **Adaptive Interpolation**: Automatically selects INTER_CUBIC (upscaling) or INTER_AREA (downscaling)
- **Codec Validation**: Pre-flight check prevents wasted processing time on invalid codecs

### Type System
All functions have complete type hints using:
- `np.ndarray` for OpenCV images
- `Generator[np.ndarray, None, None]` for frame generator
- Standard types (`str`, `int`, `float`, `bool`)
- `List[Tuple[str, str]]` for codec suggestions

### Logging Levels
Three-level system implemented with nested functions in `__main__`:
- `log_info()` - Normal output (suppressed in quiet mode)
- `log_verbose()` - Debug details (only in verbose mode)
- `log_error()` - Always shown

Progress bars use `tqdm` and are disabled in quiet mode via `show_progress` parameter.

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
- The generator pattern in `frames_from_image()` is critical for scalability
- Each frame is ~8MB @ 1080p, so 250 frames = ~2GB if stored

## Code Modification Guidelines

### Adding New Command-Line Arguments
Arguments are parsed in `parse_arguments()`. Follow existing patterns:
- Use descriptive help text with defaults in parentheses
- Add validation in the main execution block if needed
- Update README.md examples if user-facing

### Modifying Image Processing
When changing `scaleAndBlur()` or `frames_from_image()`:
- Preserve the generator pattern in `frames_from_image()`
- Maintain type hints and comprehensive docstrings
- Consider impact on memory usage
- Test with various aspect ratios (wide, narrow, square)

### Adding Verbosity Levels
Use the existing logging functions:
```python
log_info("User-facing message")        # Normal mode
log_verbose("Debug details")           # Verbose mode only
log_error("[ERROR] Always shown")      # All modes
```

For progress bars in new loops:
```python
iterator = items if args.quiet else tqdm(items, desc="Processing", unit="item")
```

## Development Roadmap

### ⭐ Recommended Next Steps (Top 3 Priorities)

Based on project maturity, user value, and development momentum:

**1. ~~Configuration File Support (Phase 2)~~** - ✅ **COMPLETED**
- ✅ Implemented `.imgtovideorc` (simple KEY=VALUE) and `imgtovideorc.yaml` (YAML) support
- ✅ Config file search in current dir and home dir (~/.config/)
- ✅ CLI arguments override config values as expected
- ✅ 16 comprehensive tests added (119 total tests now)
- ✅ Fully documented in README.md with examples
- **Result**: 88.6% coverage, all tests passing

**2. ~~Parallel Processing (Phase 3)~~** - ✅ **COMPLETED**
- ✅ Implemented `--jobs` flag for concurrent image processing
- ✅ Auto-detect CPU cores with `--jobs 0`
- ✅ Worker function for multiprocessing.Pool
- ✅ Progress bars work correctly across processes
- ✅ 2-4x performance improvement on multi-core systems
- ✅ Sequential mode preserved for single-threaded use
- **Result**: Tested with 5 images on 12-core system, ~4.3x speedup
- **Actual effort**: ~3 hours (less than estimated 8-10 hours)

**3. Pan Effects (Phase 2)** - **NEW HIGHEST PRIORITY**
- **What**: Add `--pan-direction` for left/right/up/down camera movement
- **Why**: Extends Ken Burns effect with more creative options
- **Effort**: 6-8 hours
- **Impact**: Medium-High - adds variety to video output
- **Implementation**: Modify frame generation to support both zoom and pan transforms

### Phase 1: Testing & Validation Foundation ✅ **COMPLETED**

**Status**: Successfully established comprehensive testing infrastructure with automated validation, full test coverage of core functionality, and PyInstaller build capability.

**Completed Deliverables**:
- ✅ **Unit test suite**: 76 tests covering core functions (scaleAndBlur, frames_from_image, codec validation)
- ✅ **Integration tests**: 13 tests for end-to-end pipeline, batch processing, resume capability
- ✅ **Video stitching tests**: 13 tests for combining multiple videos (NEW)
- ✅ **Test infrastructure**: Shared fixtures, helper functions, automated validation
- ✅ **Output validation**: Metadata checks, frame counting, playback verification
- ✅ **PyInstaller integration**: Portable executable build capability
- ✅ **Video stitching feature**: Combine multiple videos into slideshows (120 lines)

**Current Test Suite**:
- **103 total tests** (101 fast, 2 slow marked)
- **84.42% code coverage** (target: 85%)
- **Test files**:
  - `tests/test_scale_and_blur.py` - 25 unit tests
  - `tests/test_frames_from_image.py` - 28 unit tests
  - `tests/test_codec_validation.py` - 24 unit tests
  - `tests/test_integration.py` - 13 integration tests
  - `tests/test_stitching.py` - 13 integration tests (NEW)
  - `tests/conftest.py` - Shared fixtures and utilities
- **Running tests**: `uv run pytest tests/ -v`

**Remaining Coverage Gaps** (15.58% uncovered):
- CLI argument parsing and main execution (lines 475-563) - Hard to test without subprocess
- Some error paths in VideoWriterContext and stitch_videos

### Phase 2: Essential User Features
**Goal**: Make the tool easier to use for common workflows

**Priority: HIGH** - These features provide immediate user value

- [x] **Configuration file support** ✅ **COMPLETED**
  - [x] Allow `.imgtovideorc` or `imgtovideorc.yaml` for defaults
  - [x] Support per-project and home directory configuration
  - [x] CLI arguments override config file values
  - [x] Document configuration options in README
  - [x] Comprehensive test suite (16 tests)
  - [x] Support simple KEY=VALUE and YAML formats
  - [x] Handle comments, type conversion, inline comments
  - **Status**: Fully implemented with 88.6% code coverage
  - **Actual effort**: ~4 hours (as estimated)

- [ ] **Transition effects for stitched videos**
  - [ ] Add fade transitions between stitched videos
  - [ ] Support cross-dissolve effects
  - [ ] Configurable transition duration
  - **Rationale**: Makes slideshows more professional
  - **Estimated effort**: 6-8 hours

- [ ] **Implement pan effects alongside zoom**
  - [ ] Add `--pan-direction` argument (left, right, up, down)
  - [ ] Support combined zoom + pan
  - [ ] Add random pan option for variation
  - **Rationale**: Extends Ken Burns effect with more dynamic motion
  - **Estimated effort**: 6-8 hours
  - **User value**: Medium-High - adds creative options

- [ ] **Improve error messages and recovery**
  - [ ] Better suggestions when codec fails
  - [ ] Graceful handling of corrupted images
  - [ ] Retry logic for transient failures

- [ ] **Add output quality presets**
  - [ ] Support for preset quality levels (low, medium, high, ultra)
  - [ ] Bitrate control
  - [ ] Compression level control
  - **Estimated effort**: 3-4 hours

- [ ] **Add audio support**
  - [ ] Allow background music/audio file
  - [ ] Support audio fade in/out
  - [ ] Match audio duration to video
  - **Note**: Significant scope increase, consider Phase 4
  - **Estimated effort**: 12-15 hours

### Phase 3: Performance & Scalability
**Goal**: Handle larger workloads efficiently

**Priority: MEDIUM-HIGH** - Significant performance improvement for batch workflows

- [x] **Implement parallel processing** ✅ **COMPLETED** ⭐ HIGH IMPACT
  - [x] Process multiple images concurrently
  - [x] Use multiprocessing pool for CPU-bound work
  - [x] Add `--jobs` argument to control parallelism
  - [x] Maintain memory efficiency with generator pattern
  - [x] Auto-detect CPU cores with `-j 0`
  - [x] Worker function processes single image independently
  - [x] Progress bar integration with tqdm for multiprocessing
  - **Result**: 2-4x performance improvement on multi-core systems
  - **Actual effort**: ~3 hours (less than estimated 8-10 hours)
  - **User value**: High for batch operations - tested successfully

- [ ] **Optimize memory usage**
  - [ ] Profile memory consumption
  - [ ] Identify and fix memory leaks
  - [ ] Add memory usage reporting in verbose mode
  - **Estimated effort**: 4-6 hours

- [ ] **Add GPU acceleration support**
  - [ ] Investigate CUDA/OpenCL for frame generation
  - [ ] Benchmark GPU vs CPU performance
  - [ ] Make GPU optional (fallback to CPU)
  - **Note**: Significant research required
  - **Estimated effort**: 15-20 hours

- [ ] **Add caching for repeated operations**
  - [ ] Cache scaled/blurred base images
  - [ ] Implement smart cache invalidation

### Phase 4: Code Quality & Architecture
**Goal**: Improve maintainability and testability

**Priority: LOW** - Only needed if codebase grows significantly

**Note**: Current single-file structure (956 lines) is still manageable. Consider refactoring if:
- File exceeds 1500 lines
- External contributors join the project
- Complexity becomes difficult to navigate

- [ ] Extract functions into logical modules
  - [ ] `image_processing.py` - scaleAndBlur, frame generation
  - [ ] `codec_validation.py` - codec testing and suggestions
  - [ ] `cli.py` - argument parsing and main execution
  - [ ] `validators.py` - input validation logic
  - [ ] `stitching.py` - video stitching functionality
  - **Estimated effort**: 10-12 hours (with tests)

- [ ] Improve type hints and documentation
  - [ ] Add type stubs for better IDE support
  - [ ] Generate API documentation from docstrings
  - [ ] Add more inline comments for complex logic

- [ ] Add logging framework
  - [ ] Replace print statements with proper logging
  - [ ] Support log levels (DEBUG, INFO, WARNING, ERROR)
  - [ ] Add option to write logs to file
  - **Estimated effort**: 3-4 hours

- [ ] Refactor VideoWriter context manager
  - [ ] Consider using dataclasses for configuration
  - [ ] Add more robust error handling

### Phase 5: Advanced Features
**Goal**: Add professional-grade capabilities

**Priority: MEDIUM** - Nice-to-have features for power users

- [x] **Support for video sequences** ✅ PARTIALLY COMPLETE
  - [x] Create slideshow from multiple images (stitching feature)
  - [ ] Add transition effects between stitched videos (moved to Phase 2)
  - [ ] Accept input folders with numbered image sequences
  - [ ] Custom ordering for stitched videos (currently alphabetical)

- [ ] **Add filters and effects**
  - [ ] Color grading presets (vintage, black & white, etc.)
  - [ ] Vignette effect
  - [ ] Film grain/noise
  - **Estimated effort**: 8-10 hours

- [ ] **Batch processing enhancements**
  - [ ] Process entire directory tree recursively
  - [ ] Pattern matching for selective processing
  - [ ] Generate index/manifest of processed files

- [ ] **Export presets**
  - [ ] Instagram (1080x1080, mp4)
  - [ ] YouTube (1920x1080, h264)
  - [ ] Twitter (1280x720, mp4)
  - [ ] TikTok (1080x1920, mp4)
  - **Note**: Could be part of config file support (Phase 2)

- [ ] **Add web interface (optional)**
  - [ ] Simple Flask/FastAPI web UI
  - [ ] Drag-and-drop image upload
  - [ ] Real-time preview
  - [ ] Download processed videos
  - **Note**: Major scope expansion, separate project?

### Phase 6: Distribution & Deployment ✅ PARTIALLY COMPLETE
**Goal**: Make the tool easy to install and use

- [x] **Create standalone executables** ✅ **COMPLETED**
  - [x] Use PyInstaller for Windows builds
  - [x] Document build process in CLAUDE.md and README.md
  - [x] ~52MB portable .exe with bundled dependencies
  - [ ] Test on clean Windows systems without Python
  - [ ] Create builds for Mac and Linux
  - **Status**: Windows build fully functional, other platforms untested

- [ ] **Package for distribution**
  - [ ] Create PyPI package
  - [ ] Add `setup.py` and proper package structure
  - [ ] Include pre-built binaries for common platforms
  - **Estimated effort**: 6-8 hours

- [ ] **Add Docker support**
  - [ ] Create Dockerfile for containerized usage
  - [ ] Publish to Docker Hub
  - [ ] Document Docker usage
  - **Estimated effort**: 3-4 hours

- [ ] **Improve documentation**
  - [x] Comprehensive README.md with examples
  - [x] Development guide (CLAUDE.md) with roadmap
  - [ ] Add video tutorials/demos
  - [ ] Create comprehensive user guide
  - [ ] Document all codec options by platform

### Development Notes

**Before Starting a Task**:
1. Read relevant code thoroughly
2. Check for related items in other phases
3. Consider impact on existing functionality
4. Preserve memory-efficient generator pattern

**After Completing a Task**:
1. Update this roadmap (mark with ✅)
2. Run automated tests: `uv run pytest tests/ -v`
3. Verify test coverage remains high (>80%)
4. Update README.md if user-facing
5. Commit with descriptive message following conventions

**Design Principles**:
- Maintain backward compatibility
- Keep simple script nature - don't over-engineer
- Prioritize user experience and documentation
- Test on Windows (primary platform)
- Consider memory usage for large batches
- Maintain CLI simplicity

## Platform Considerations

### Windows
- Primary development platform
- Unicode console issues fixed (using `[OK]`/`[ERROR]` instead of ✓/✗)
- Paths with spaces must be quoted in examples

### Cross-Platform
- OpenCV and NumPy work on Windows/Linux/macOS
- File path handling uses `os.path.join()` for compatibility
- No platform-specific code except console output handling

## Common Patterns

### Error Handling
```python
try:
    # Processing code
    log_verbose("Detailed step")
    result = process()
    log_info("[OK] Success message")
except ValueError as e:
    log_error(f"[ERROR] Validation failed: {e}")
except RuntimeError as e:
    log_error(f"[ERROR] Processing failed: {e}")
```

### Output Depending on Verbosity
```python
if args.quiet:
    pass  # No output
elif args.verbose:
    print(f"[VERBOSE] Detail")
else:
    tqdm.write(f"Normal message")  # Use tqdm.write with progress bars
```

## Known Limitations

1. **Single-threaded** - Processes images sequentially (parallel processing planned for Phase 3)
2. **Limited codec testing** - Codec validation may miss some edge cases on different systems
3. **Monolithic structure** - Single 956-line file (refactoring planned only if needed in Phase 4)
4. **No audio support** - Only generates video without audio tracks (planned for Phase 2)
5. **Basic zoom only** - No pan effects or combined movements yet (planned for Phase 2)
6. **No transition effects** - Stitched videos are concatenated without transitions (planned for Phase 2)
7. **No configuration file** - Must specify settings via CLI arguments each time (planned for Phase 2)
8. **Alphabetical stitching order** - Videos are combined alphabetically, no custom ordering (planned for Phase 5)

## Git Commit Conventions

Recent commits follow this pattern:
- Descriptive first line summarizing the change
- Blank line
- Detailed explanation of what changed and why
- Performance impact or benefits when applicable
- Footer with "🤖 Generated with [Claude Code]" and co-author tag

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
