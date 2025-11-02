# Image to Video Converter - Improvement Roadmap

This document tracks planned improvements for the Image to Video Converter project, organized by priority and implementation phase.

---

## Phase 1: Quick Wins & Critical Fixes
**Focus**: Immediate improvements with high impact and low effort

### Critical Fixes
- [x] **Fix memory management issue** - Stream frames directly to VideoWriter instead of storing entire frame list in memory
  - ~~Current issue~~ FIXED: High memory usage for long videos (e.g., 60s @ 30fps @ 1080p = ~14GB RAM)
  - Location: `frames_from_image()` lines 87-100, main loop line 253
  - Solution: Converted to generator pattern that yields frames one at a time
  - Bonus fix: Replaced Unicode symbols (✓/✗) with ASCII [OK]/[ERROR] for Windows compatibility

- [ ] **Add codec validation** - Pre-validate codec availability before processing
  - Current issue: Invalid codecs cause cryptic errors after processing
  - Location: Line 247 in VideoWriter initialization
  - Solution: Check codec availability, provide fallback suggestions

### Documentation
- [x] **Create README.md** - Comprehensive user documentation
  - Installation instructions (uv, pip, PyInstaller)
  - Usage examples and command reference
  - Troubleshooting guide
  - Sample outputs

- [ ] **Add comprehensive docstrings** - Document all functions
  - `scaleAndBlur()` - Explain Ken Burns effect implementation
  - `frames_from_image()` - Document zoom algorithm and parameters
  - Include parameter types, return values, and exceptions

- [ ] **Add type hints** - Improve code clarity and enable static analysis
  - Add type hints to all function signatures
  - Use `numpy.ndarray`, `int`, `float`, `str` types appropriately
  - Consider using `typing.Optional` where needed

### User Experience
- [ ] **Add progress indicators** - Show processing progress to users
  - Use `tqdm` library for progress bars
  - Track: frame generation, video writing, batch processing
  - Example: "Processing image 3/10: Generating frames [████████░░] 80%"

- [ ] **Improve error messages** - User-friendly errors with solutions
  - Replace technical OpenCV errors with helpful guidance
  - Example: "Codec 'xdv7' not available. Try: --codec mp4v or --codec avc1"
  - Add suggestions for common issues (disk space, permissions, formats)

- [ ] **Add verbose/quiet modes** - Control output verbosity
  - `-v, --verbose` flag for detailed output and debugging
  - `-q, --quiet` flag for minimal output (errors only)
  - Default: normal informational output

---

## Phase 2: UX Improvements
**Focus**: Enhance user experience and workflow efficiency

### Workflow Enhancements
- [ ] **Add dry-run mode** - Preview what will be processed without executing
  - `--dry-run` flag shows: files to process, settings, estimated output size
  - Helps users verify configuration before committing

- [ ] **Add preview mode** - Generate sample output before full processing
  - `--preview` flag creates: first/middle/last frame thumbnails
  - Optional: 3-second sample video
  - Saves time when testing settings

- [ ] **Resume capability** - Skip already-processed files
  - Check if output file exists before processing
  - `--force` flag to reprocess existing files
  - `--skip-existing` flag (default behavior)
  - Prevents wasted time on interrupted batches

### Configuration
- [ ] **Configuration file support** - Save and reuse settings
  - Support YAML or JSON config files
  - `--config config.yaml` to load settings
  - Example config with common presets (web, broadcast, social media)
  - CLI args override config file values

- [ ] **Add logging framework** - Structured logging for debugging
  - Use Python's `logging` module
  - Log levels: DEBUG, INFO, WARNING, ERROR
  - Optional log file output: `--log-file output.log`
  - Timestamp all operations for troubleshooting

### Validation & Safety
- [ ] **Disk space validation** - Check available space before processing
  - Estimate output file size based on settings
  - Warn if insufficient disk space
  - Fail early rather than mid-processing

- [ ] **Output validation** - Verify video after creation
  - Check that output file exists and is not empty
  - Report file size and duration
  - Optional: Verify video is playable (read first frame)

- [ ] **Better CLI validation** - Catch errors before processing
  - Validate blur value at argument parsing (must be odd)
  - Check input/output paths exist and are accessible
  - Warn if input and output directories are the same

---

## Phase 3: Code Quality
**Focus**: Maintainability, testability, and code health

### Testing
- [ ] **Create test structure** - Foundation for test coverage
  - Create `tests/` directory with `__init__.py`
  - Add `pytest.ini` configuration
  - Create `conftest.py` with shared fixtures
  - Add `tests/fixtures/` with sample test images

- [ ] **Write unit tests** - Test individual functions
  - `tests/test_image_processor.py` - Test `scaleAndBlur()`
    - Normal cases (various aspect ratios)
    - Edge cases (square images, extreme ratios)
    - Error cases (invalid dimensions, missing files)
  - `tests/test_frame_generator.py` - Test `frames_from_image()`
    - Frame count validation
    - Zoom calculations
    - Memory efficiency

- [ ] **Write integration tests** - Test end-to-end workflows
  - Process sample images with various settings
  - Test batch processing
  - Test error recovery

### Code Cleanup
- [ ] **Extract magic numbers** - Named constants with documentation
  - Line 79: Document zoom rate limits (0 to 0.1)
  - Lines 91-92: Explain offset calculations
  - Create `CONSTANTS` section at top of file

- [ ] **Improve iteration patterns** - More Pythonic code
  - Line 256: Use `for frame in imgSequence` instead of `range(len())`
  - Consider enumerate() where indices are needed

- [ ] **Resource cleanup** - Proper resource management
  - Use context managers for VideoWriter
  - Ensure cleanup on exceptions
  - Delete partial output files on failure

- [ ] **Separate validation logic** - Extract to validators module
  - Create `validators.py` with validation functions
  - Centralize dimension, blur, file path validation
  - Reuse across CLI and function-level validation

---

## Phase 4: Modest Feature Expansion
**Focus**: Valuable features with reasonable implementation effort

### Output Options
- [ ] **Quality presets** - Easy quality selection
  - `--quality low` - Faster processing, smaller files
  - `--quality medium` - Current defaults (balanced)
  - `--quality high` - Higher bitrate, better quality
  - `--quality best` - Lossless or near-lossless
  - Presets adjust resolution, bitrate, encoding settings

- [ ] **List available codecs** - Help users choose codecs
  - `--list-codecs` command to show available codecs on system
  - Include descriptions and recommended use cases
  - Example: "mp4v - MPEG-4 codec, widely supported"

- [ ] **Metadata support** - Add video metadata
  - Write title, description, creation date
  - Option to preserve EXIF data from source images
  - `--title "My Video"`, `--description "Created from photos"`

### Batch Processing
- [ ] **Pattern matching** - Filter files by pattern
  - `--pattern "vacation_*.jpg"` to process specific files
  - Support glob patterns (*, ?, [])
  - Combine with existing format filtering

- [ ] **Parallel processing** - Speed up batch operations
  - `--parallel N` to process N images concurrently
  - Use multiprocessing for CPU-bound operations
  - Default: auto-detect CPU cores, use cores - 1
  - Progress tracking across parallel operations

- [ ] **Recursive directory processing** - Process subdirectories
  - `--recursive` flag to search subdirectories
  - Maintain directory structure in output
  - Useful for organized photo libraries

### Effects
- [ ] **Zoom direction** - Choose zoom in or out
  - `--zoom-direction in` (current behavior, zoom in)
  - `--zoom-direction out` (start zoomed, zoom out)
  - Affects starting scale and direction in `frames_from_image()`

- [ ] **Pan direction** - Add panning motion
  - `--pan left`, `--pan right`, `--pan up`, `--pan down`
  - Combine with zoom for diagonal motion
  - Modify offset calculations in frame generation

### Refactoring (Foundation for future work)
- [ ] **Modularize codebase** - Separate concerns
  - Create `src/` directory structure:
    - `core/image_processor.py` - Image scaling and blurring
    - `core/frame_generator.py` - Frame generation with effects
    - `core/video_writer.py` - Video output handling
    - `cli/args.py` - Argument parsing
    - `cli/runner.py` - Main execution logic
    - `utils/validators.py` - Validation functions
    - `utils/constants.py` - Constants and presets
  - Maintain backward compatibility with current script

---

## Future Considerations (Lower Priority)

### Advanced Features
- [ ] GPU acceleration (OpenCV CUDA backend)
- [ ] Slideshow mode (combine multiple images with transitions)
- [ ] Audio support (background music)
- [ ] Smart cropping (face detection, saliency-based framing)
- [ ] Advanced motion curves (ease-in/ease-out, custom paths)
- [ ] Watermarking support
- [ ] More output formats and presets

### Distribution
- [ ] Package for PyPI distribution (`pip install img2video`)
- [ ] Entry point CLI command (`img2video` instead of `python imgToVideo.py`)
- [ ] Improved PyInstaller spec and build scripts
- [ ] Cross-platform testing (GitHub Actions for Linux/Mac/Windows)

### Infrastructure
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated testing on PRs
- [ ] Dependency security scanning
- [ ] Code quality gates (linting, type checking, coverage)
- [ ] Documentation website

---

## Development Guidelines

### Before Starting a Task:
1. Read the relevant code section thoroughly
2. Check for related TODOs in other phases
3. Consider impact on existing functionality
4. Write tests first (TDD) when applicable

### After Completing a Task:
1. Mark the checkbox with [x]
2. Run tests to ensure nothing broke
3. Update README.md if user-facing changes
4. Consider if new tests are needed
5. Commit with descriptive message

### Priority Labels:
- **Critical**: Must fix, affects functionality or user experience significantly
- **High**: Important improvements, should do soon
- **Medium**: Nice to have, improves quality of life
- **Low**: Future enhancements, not urgent

---

## Notes

- Focus on backward compatibility when refactoring
- Keep the simple script nature - don't over-engineer
- Prioritize user experience and documentation
- Test on Windows (primary platform based on git history)
- Consider memory usage for large batches
- Maintain CLI simplicity even as features grow

---

**Last Updated**: 2025-11-03
**Version**: 1.0.0
