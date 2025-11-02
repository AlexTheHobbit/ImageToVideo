# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Image to Video Converter - A single-file Python CLI tool that creates videos from static images using the Ken Burns zoom effect. The project uses OpenCV for image processing and video encoding, with a focus on memory efficiency and user experience.

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

### Phase 1: Quick Wins & Critical Fixes ✅ COMPLETE
All Phase 1 items have been implemented:

**Critical Fixes**:
- ✅ Memory management - Converted to generator pattern (99% memory reduction)
- ✅ Codec validation - Pre-flight checks with helpful suggestions

**Documentation**:
- ✅ README.md - Comprehensive user documentation
- ✅ Comprehensive docstrings - All functions documented with examples
- ✅ Type hints - Complete type annotations throughout

**User Experience**:
- ✅ Progress indicators - tqdm progress bars for batch and frame generation
- ✅ Improved error messages - Clear prefixes and helpful solutions
- ✅ Verbose/quiet modes - Three-level logging system

### Phase 2: UX Improvements (Next Priority)

**Workflow Enhancements**:
- [ ] **Dry-run mode** - Preview processing without execution
  - `--dry-run` flag to show files, settings, estimated output size

- [ ] **Preview mode** - Generate sample output
  - `--preview` creates first/middle/last frame thumbnails or 3-second sample

- [ ] **Resume capability** - Skip already-processed files
  - Check for existing output files
  - `--force` to reprocess, `--skip-existing` as default

**Configuration**:
- [ ] **Config file support** - YAML/JSON configuration files
  - `--config config.yaml` to load settings
  - CLI args override config values
  - Presets for common scenarios (web, broadcast, social media)

- [ ] **Logging framework** - Structured logging with Python's logging module
  - Log levels: DEBUG, INFO, WARNING, ERROR
  - `--log-file output.log` for persistent logs

**Validation & Safety**:
- [ ] **Disk space validation** - Check before processing
- [ ] **Output validation** - Verify created videos are valid
- [ ] **Better CLI validation** - Validate blur at parse time, check paths early

### Phase 3: Code Quality

**Testing**:
- [ ] Create test structure (tests/, pytest.ini, conftest.py, fixtures/)
- [ ] Unit tests for `scaleAndBlur()` and `frames_from_image()`
- [ ] Integration tests for end-to-end workflows

**Code Cleanup**:
- [ ] Extract magic numbers to named constants
- [ ] Improve iteration patterns (already using direct iteration)
- [ ] Resource cleanup with context managers for VideoWriter
- [ ] Separate validation logic to validators module

### Phase 4: Feature Expansion

**Output Options**:
- [ ] Quality presets (--quality low/medium/high/best)
- [ ] List available codecs command
- [ ] Metadata support (title, description, EXIF preservation)

**Batch Processing**:
- [ ] Pattern matching (--pattern "*.jpg")
- [ ] Parallel processing (--parallel N)
- [ ] Recursive directory processing (--recursive)

**Effects**:
- [ ] Zoom direction (in vs out)
- [ ] Pan direction (left/right/up/down)

**Refactoring**:
- [ ] Modularize into src/ structure while maintaining backward compatibility

### Future Considerations

**Advanced Features**:
- GPU acceleration (CUDA backend)
- Slideshow mode with transitions
- Audio support
- Smart cropping (face detection)
- Advanced motion curves

**Distribution**:
- PyPI package distribution
- Entry point CLI command
- Cross-platform CI/CD testing

**Infrastructure**:
- GitHub Actions CI/CD
- Dependency security scanning
- Code quality gates

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
