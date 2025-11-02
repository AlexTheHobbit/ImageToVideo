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
There is currently no automated test suite. Manual testing workflow:
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

## Architecture

### Single-File Design
The entire application is in `imgToVideo.py` (~585 lines). This is intentional for simplicity and portability.

### Core Components

**Image Processing Pipeline**:
1. `scaleAndBlur()` - Prepares image with aspect-ratio-preserving scaling and blurred background
2. `frames_from_image()` - Generator that yields progressively zoomed frames (memory-efficient)
3. Main loop - Streams frames directly to VideoWriter

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

### Phase 1: Testing & Validation Foundation
**Goal**: Establish a robust testing infrastructure

- [ ] Create unit tests for core functions
  - [ ] `scaleAndBlur()` - test aspect ratio handling, blur validation
  - [ ] `frames_from_image()` - test generator pattern, zoom calculations
  - [ ] `validate_codec()` - test various codec scenarios
  - [ ] `get_codec_suggestions()` - test suggestion accuracy
- [ ] Add integration tests for full processing pipeline
  - [ ] Test processing single image end-to-end
  - [ ] Test batch processing with multiple images
  - [ ] Test resume capability (skip existing files)
- [ ] Implement output video validation
  - [ ] Verify output file exists and has content
  - [ ] Check video metadata (duration, fps, resolution)
  - [ ] Validate frame count matches expected
- [ ] Add test fixtures and sample images
  - [ ] Wide (landscape) test image
  - [ ] Narrow (portrait) test image
  - [ ] Square test image
  - [ ] Edge cases (very small, very large)

### Phase 2: User Experience & Features
**Goal**: Make the tool more user-friendly and capable

- [ ] Add configuration file support
  - [ ] Allow `.imgtovideorc` or `config.yaml` for defaults
  - [ ] Support per-project configuration
  - [ ] Document configuration options
- [ ] Implement pan effects alongside zoom
  - [ ] Add `--pan-direction` argument (left, right, up, down)
  - [ ] Support combined zoom + pan
  - [ ] Add random pan option for variation
- [ ] Add audio support
  - [ ] Allow background music/audio file
  - [ ] Support audio fade in/out
  - [ ] Match audio duration to video
- [ ] Improve error messages and recovery
  - [ ] Better suggestions when codec fails
  - [ ] Graceful handling of corrupted images
  - [ ] Retry logic for transient failures
- [ ] Add more output options
  - [ ] Support for preset quality levels (low, medium, high, ultra)
  - [ ] Bitrate control
  - [ ] Compression level control

### Phase 3: Code Quality & Architecture
**Goal**: Improve maintainability and testability

- [ ] Extract functions into logical modules
  - [ ] `image_processing.py` - scaleAndBlur, frame generation
  - [ ] `codec_validation.py` - codec testing and suggestions
  - [ ] `cli.py` - argument parsing and main execution
  - [ ] `validators.py` - input validation logic
- [ ] Improve type hints and documentation
  - [ ] Add type stubs for better IDE support
  - [ ] Generate API documentation from docstrings
  - [ ] Add more inline comments for complex logic
- [ ] Refactor VideoWriter context manager
  - [ ] Consider using dataclasses for configuration
  - [ ] Add more robust error handling
- [ ] Add logging framework
  - [ ] Replace print statements with proper logging
  - [ ] Support log levels (DEBUG, INFO, WARNING, ERROR)
  - [ ] Add option to write logs to file

### Phase 4: Performance & Scalability
**Goal**: Handle larger workloads efficiently

- [ ] Implement parallel processing
  - [ ] Process multiple images concurrently
  - [ ] Use multiprocessing pool for CPU-bound work
  - [ ] Add `--jobs` argument to control parallelism
  - [ ] Maintain memory efficiency with generator pattern
- [ ] Add GPU acceleration support
  - [ ] Investigate CUDA/OpenCL for frame generation
  - [ ] Benchmark GPU vs CPU performance
  - [ ] Make GPU optional (fallback to CPU)
- [ ] Optimize memory usage
  - [ ] Profile memory consumption
  - [ ] Identify and fix memory leaks
  - [ ] Add memory usage reporting in verbose mode
- [ ] Add caching for repeated operations
  - [ ] Cache scaled/blurred base images
  - [ ] Implement smart cache invalidation

### Phase 5: Advanced Features
**Goal**: Add professional-grade capabilities

- [ ] Support for video sequences
  - [ ] Accept input folders with numbered image sequences
  - [ ] Create slideshow from multiple images
  - [ ] Add transition effects between images
- [ ] Add filters and effects
  - [ ] Color grading presets (vintage, black & white, etc.)
  - [ ] Vignette effect
  - [ ] Film grain/noise
- [ ] Batch processing enhancements
  - [ ] Process entire directory tree recursively
  - [ ] Pattern matching for selective processing
  - [ ] Generate index/manifest of processed files
- [ ] Export presets
  - [ ] Instagram (1080x1080, mp4)
  - [ ] YouTube (1920x1080, h264)
  - [ ] Twitter (1280x720, mp4)
  - [ ] TikTok (1080x1920, mp4)
- [ ] Add web interface (optional)
  - [ ] Simple Flask/FastAPI web UI
  - [ ] Drag-and-drop image upload
  - [ ] Real-time preview
  - [ ] Download processed videos

### Phase 6: Distribution & Deployment
**Goal**: Make the tool easy to install and use

- [ ] Package for distribution
  - [ ] Create PyPI package
  - [ ] Add `setup.py` and proper package structure
  - [ ] Include pre-built binaries for common platforms
- [ ] Create standalone executables
  - [ ] Use PyInstaller for Windows/Mac/Linux
  - [ ] Test on clean systems without Python
- [ ] Add Docker support
  - [ ] Create Dockerfile for containerized usage
  - [ ] Publish to Docker Hub
  - [ ] Document Docker usage
- [ ] Improve documentation
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
2. Test manually (no automated tests yet)
3. Update README.md if user-facing
4. Commit with descriptive message following conventions

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

1. **No test suite** - Manual testing required for all changes
2. **Single-threaded** - Processes images sequentially (parallel processing planned for Phase 4)
3. **No validation of output video** - Assumes successful write if no exceptions
4. **Limited codec testing** - Codec validation may miss some edge cases on different systems
5. **Monolithic structure** - Single file makes it harder to unit test (refactoring planned for Phase 3)

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
