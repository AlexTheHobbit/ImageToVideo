# Development Roadmap

This document outlines potential enhancements and improvements for the ImageToVideo project.

## Current Status

- **Version**: Latest stable release
- **Test Coverage**: 88.6% (119 tests across 8 test files)
- **Core Features**: Ken Burns effect, parallel processing, video stitching, config file support
- **Lines of Code**: 1,291 (single-file design)

---

## Phase 1: Core Enhancements

### 1.1 Enhanced Motion Effects
- [ ] **Pan Effect**: Add horizontal/vertical panning motion
  - New parameters: `--pan-direction` (left, right, up, down)
  - Combined pan + zoom effects
  - Lines affected: `frames_from_image()` (160-251)

- [ ] **Configurable Zoom Direction**: Support zoom-out in addition to zoom-in
  - New parameter: `--zoom-direction` (in, out)
  - Reverse the zoom calculation logic
  - Maintain backward compatibility

- [ ] **Motion Presets**: Predefined motion patterns
  - `--motion-preset` (zoom-in, zoom-out, pan-left, pan-right, diagonal)
  - Simplify common use cases
  - Store presets in config file

**Estimated Effort**: 2-3 days
**Test Coverage Target**: Add 15-20 new tests
**Priority**: High

### 1.2 Video Transitions
- [ ] **Stitching with Transitions**: Add fade/crossfade between videos
  - New parameter: `--transition` (none, fade, crossfade, wipe)
  - New parameter: `--transition-duration` (default: 1 second)
  - Modify `stitch_videos()` (351-471)
  - Blend frames during transition periods

**Estimated Effort**: 2-3 days
**Test Coverage Target**: Add 10-12 new tests
**Priority**: Medium

### 1.3 Audio Support
- [ ] **Background Music**: Add audio track to generated videos
  - New parameter: `--audio-file` (path to audio file)
  - Use `moviepy` or `ffmpeg-python` for audio mixing
  - Consider adding as optional dependency
  - Auto-loop or trim audio to match video duration

- [ ] **Audio Stitching**: Preserve/combine audio when stitching videos
  - Extract audio from source videos (if present)
  - Concatenate audio tracks alongside video

**Estimated Effort**: 3-4 days
**Test Coverage Target**: Add 8-10 new tests
**Priority**: Medium
**Note**: May increase executable size significantly

---

## Phase 2: Usability Improvements

### 2.1 Custom Stitching Order
- [ ] **Manual Ordering**: Specify video order for stitching
  - New parameter: `--stitch-order` (path to text file with ordered filenames)
  - Alternative: `--sort-by` (name, date, custom)
  - Replace alphabetical sorting with user-defined order

**Estimated Effort**: 1 day
**Test Coverage Target**: Add 5-6 new tests
**Priority**: High

### 2.2 Progress & Resume Features
- [ ] **Resume from Failure**: Better handling of interrupted processing
  - Store processing state in temporary file
  - Auto-detect incomplete videos (corrupted/truncated files)
  - `--resume` flag to continue from last successful file

- [ ] **Estimated Time Remaining**: Show ETA in progress bars
  - Calculate based on current processing speed
  - Update dynamically during execution

**Estimated Effort**: 1-2 days
**Test Coverage Target**: Add 6-8 new tests
**Priority**: Medium

### 2.3 Output Formats & Quality
- [ ] **Quality Presets**: Simplify codec/bitrate selection
  - New parameter: `--quality` (low, medium, high, ultra)
  - Map to appropriate codec + bitrate combinations
  - Document expected file sizes

- [ ] **Codec Auto-Detection**: Intelligently suggest best available codec
  - Test multiple codecs and rank by quality/compatibility
  - Fall back to most compatible option
  - Cache codec availability results

**Estimated Effort**: 1-2 days
**Test Coverage Target**: Add 8-10 new tests
**Priority**: Low

---

## Phase 3: Advanced Features

### 3.1 Smart Image Analysis
- [ ] **Auto-Crop**: Detect and remove black bars from images
  - Analyze image borders for solid colors
  - Crop to content before processing

- [ ] **Face Detection**: Center zoom on detected faces
  - Use OpenCV Haar cascades or DNN face detection
  - Adjust zoom center point to face location
  - Graceful fallback if no face detected

**Estimated Effort**: 3-4 days
**Test Coverage Target**: Add 12-15 new tests
**Priority**: Low

### 3.2 Batch Configuration
- [ ] **Per-Image Settings**: Custom settings for each image
  - YAML/JSON file mapping images to settings
  - Example: `image1.jpg: {duration: 5, zoom: 0.001}`
  - Override global defaults per-image

- [ ] **Folder-Based Configs**: Different settings per folder
  - Search for `.imgtovideorc` in each subdirectory
  - Recursive processing with folder-specific configs

**Estimated Effort**: 2-3 days
**Test Coverage Target**: Add 10-12 new tests
**Priority**: Low

### 3.3 Performance Optimizations
- [ ] **GPU Acceleration**: Use GPU for image processing
  - OpenCV CUDA support (cv2.cuda module)
  - Significant speedup for 4K+ videos
  - Optional feature with CPU fallback

- [ ] **Caching**: Cache scaled/blurred images
  - Store intermediate results on disk
  - Reuse if processing same image with different settings
  - Configurable cache size limit

**Estimated Effort**: 4-5 days
**Test Coverage Target**: Add 8-10 new tests
**Priority**: Low
**Note**: GPU support may complicate distribution

---

## Phase 4: Documentation & Tooling

### 4.1 Documentation
- [ ] **Video Tutorial**: Create demo video showing features
- [ ] **Cookbook**: Common recipes and examples
  - "Creating a photo slideshow with music"
  - "Batch processing vacation photos"
  - "Professional settings for 4K output"
- [ ] **API Documentation**: Document functions for programmatic use
  - Enable `import imgToVideo` as library
  - Example scripts using the API

**Estimated Effort**: 2-3 days
**Priority**: Medium

### 4.2 Developer Tools
- [ ] **Benchmark Suite**: Performance testing framework
  - Measure processing speed across hardware
  - Track performance regression
  - Compare codec encoding speeds

- [ ] **Profiling Tools**: Identify bottlenecks
  - Memory profiling integration
  - CPU profiling for optimization opportunities

**Estimated Effort**: 1-2 days
**Priority**: Low

### 4.3 Distribution
- [ ] **Linux Binary**: Build executable for Linux
  - Modify GitHub Actions workflow
  - Test on Ubuntu/Debian/Fedora

- [ ] **macOS Binary**: Build executable for macOS
  - Apple Silicon (ARM64) and Intel support
  - Code signing considerations

- [ ] **Package Managers**: Distribute via pip, brew, chocolatey
  - Publish to PyPI as installable package
  - Create homebrew formula
  - Create chocolatey package

**Estimated Effort**: 3-4 days
**Priority**: Medium

---

## Phase 5: Experimental Ideas

### 5.1 Advanced Effects
- [ ] **Parallax Effect**: Create depth with multi-layer images
- [ ] **Rotation**: Gentle rotation during zoom
- [ ] **Color Grading**: Apply filters (sepia, B&W, cinematic)
- [ ] **Stabilization**: Smooth out motion for handheld photos

### 5.2 Integration
- [ ] **GUI Wrapper**: Optional graphical interface
  - Electron or Qt-based desktop app
  - Drag-and-drop interface
  - Real-time preview

- [ ] **Web Service**: Cloud-based processing
  - Upload images, download video
  - Queue-based processing
  - Shareable video links

### 5.3 Intelligence
- [ ] **Scene Detection**: Auto-adjust duration per image
  - Longer duration for complex scenes
  - Shorter for simple images

- [ ] **Smart Cropping**: AI-powered composition
  - Identify subject importance
  - Optimize framing automatically

**Note**: These are exploratory ideas requiring significant R&D

---

## Maintenance & Quality

### Ongoing Tasks
- [ ] **Test Coverage**: Maintain ≥85% coverage with all new features
- [ ] **Performance**: No regression in processing speed
- [ ] **Compatibility**: Test on Windows 10/11, Ubuntu 20.04+, macOS 12+
- [ ] **Dependencies**: Keep OpenCV/NumPy versions updated (within compatibility constraints)
- [ ] **Documentation**: Update README.md and CLAUDE.md with each feature

### Code Quality Goals
- [ ] Maintain single-file design for core functionality
- [ ] Keep type hints on all functions
- [ ] Comprehensive docstrings with examples
- [ ] No breaking changes without major version bump

---

## How to Contribute

When implementing items from this roadmap:

1. **Create Issue**: Discuss approach before starting
2. **Write Tests First**: TDD approach preferred
3. **Update Documentation**: CLAUDE.md, README.md, docstrings
4. **Check Coverage**: Must maintain ≥85%
5. **Version Bump**: Follow semantic versioning rules
6. **Create PR**: Reference issue number

## Feedback

This roadmap is a living document. Suggestions and priorities can change based on:
- User feedback and feature requests
- Performance bottlenecks discovered in real-world use
- Emerging technologies (new codecs, AI models, etc.)
- Community contributions

Last Updated: 2025-11-04
