# Image to Video Converter

Convert still images into videos with a cinematic Ken Burns zoom effect. Perfect for creating engaging video content from photos, presentation slides, or artwork.

## Features

- **Ken Burns Effect**: Smooth zoom animation that brings static images to life
- **Flexible Output**: Support for multiple video codecs and formats (MXF, MP4, AVI, etc.)
- **Customizable Settings**: Control resolution, frame rate, duration, zoom speed, and blur
- **Batch Processing**: Process multiple images in one command
- **Smart Scaling**: Automatically handles various aspect ratios with intelligent cropping
- **Blurred Background**: Fills letterbox areas with an artistic blurred version of the image
- **Fast Performance**: Powered by OpenCV with optimized image processing
- **Command-Line Interface**: Easy to use with sensible defaults

## Installation

### Using uv (Recommended)

```bash
# Clone or download the project
cd "Image to Video Converter"

# Install dependencies with uv
uv sync --no-install-project

# Run the script
uv run python imgToVideo.py [options]
```

### Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Run the script
python imgToVideo.py [options]
```

### Requirements

- Python 3.8 or higher
- opencv-python 4.6.0.66
- numpy < 2.0 (for compatibility)

## Quick Start

### Basic Usage

Process all images in the current directory with default settings (1920x1080, 25fps, 10 seconds):

```bash
uv run python imgToVideo.py
```

### Specify Input and Output Directories

```bash
uv run python imgToVideo.py -i ./photos -o ./videos
```

### Custom Resolution and Settings

Create 4K videos with 30fps and 15-second duration:

```bash
uv run python imgToVideo.py --width 3840 --height 2160 --fps 30 --duration 15
```

### Adjust Zoom and Blur

```bash
uv run python imgToVideo.py --zoom 0.0006 --blur 201
```

## Command-Line Options

### Input/Output

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | `.` (current dir) | Input directory containing images |
| `--output` | `-o` | `.` (current dir) | Output directory for videos |

### Video Settings

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--width` | `-w` | `1920` | Target video width in pixels |
| `--height` | | `1080` | Target video height in pixels |
| `--fps` | | `25` | Frame rate (frames per second) |
| `--duration` | `-d` | `10` | Video duration in seconds |

### Effect Settings

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--zoom` | `-z` | `0.0004` | Zoom rate (0.0001-0.01) - higher = faster zoom |
| `--blur` | `-b` | `195` | Blur strength for background (must be odd number) |

### Output Format

| Option | Default | Description |
|--------|---------|-------------|
| `--codec` | `xdv7` | Video codec fourcc code |
| `--extension` | `mxf` | Output video file extension |

### Common Codec Options

| Codec | Extension | Description |
|-------|-----------|-------------|
| `mp4v` | `mp4` | MPEG-4, widely compatible |
| `avc1` | `mp4` | H.264, high quality, widely supported |
| `xvid` | `avi` | Xvid codec, good compression |
| `xdv7` | `mxf` | Professional MXF format (default) |

## Supported Image Formats

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- JFIF (`.jfif`)
- WebP (`.webp`)

## How It Works

### The Ken Burns Effect

The Ken Burns effect creates the illusion of motion in still images through a slow zoom and pan. This implementation:

1. **Scales the image** to fit the target resolution while preserving aspect ratio
2. **Creates a blurred background** to fill letterbox areas artistically
3. **Generates frames** with progressive zoom over time
4. **Writes to video** using your chosen codec and format

### Adaptive Interpolation

The script automatically chooses the best interpolation method based on whether the image is being upscaled or downscaled:

- **Upscaling**: Uses `INTER_CUBIC` for smooth results
- **Downscaling**: Uses `INTER_AREA` for better quality when shrinking

## Examples

### Social Media - 1080p Square

```bash
uv run python imgToVideo.py --width 1080 --height 1080 --fps 30 --duration 5 --codec avc1 --extension mp4
```

### YouTube - 4K

```bash
uv run python imgToVideo.py --width 3840 --height 2160 --fps 60 --duration 10 --codec avc1 --extension mp4
```

### Instagram Story - 9:16

```bash
uv run python imgToVideo.py --width 1080 --height 1920 --fps 30 --duration 5 --codec avc1 --extension mp4
```

### Presentation Slides

```bash
uv run python imgToVideo.py -i ./slides -o ./presentation --fps 25 --duration 8 --codec mp4v --extension mp4
```

### Slow Dramatic Zoom

```bash
uv run python imgToVideo.py --zoom 0.0002 --duration 20 --blur 255
```

### Fast Dynamic Zoom

```bash
uv run python imgToVideo.py --zoom 0.0008 --duration 5 --blur 151
```

## Output

For each input image, the script creates a video file with `_video` appended to the name:

```
Input:  vacation_photo.jpg
Output: vacation_photo_video.mxf
```

The script provides progress updates:

```
Found 5 image(s) to process
Settings: 1920x1080, 25fps, 10s, zoom=0.0004, blur=195

Processing: photo1.jpg
✓ Successfully created: ./output/photo1_video.mxf
Processing: photo2.jpg
✓ Successfully created: ./output/photo2_video.mxf
...

==================================================
Processing complete: 5 succeeded, 0 failed
==================================================
```

## Troubleshooting

### Video Codec Not Available

**Error**: `Failed to initialize video writer`

**Solution**: The specified codec may not be available on your system. Try a different codec:

```bash
# Try MP4V (widely supported)
uv run python imgToVideo.py --codec mp4v --extension mp4

# Or H.264
uv run python imgToVideo.py --codec avc1 --extension mp4
```

### Blur Value Error

**Error**: `Target blur must be odd for GaussianBlur`

**Solution**: The blur parameter must be an odd number (e.g., 151, 195, 201, 255):

```bash
uv run python imgToVideo.py --blur 201  # ✓ Correct
uv run python imgToVideo.py --blur 200  # ✗ Error - even number
```

### Image File Not Found

**Error**: `Failed to load image: file.jpg`

**Solution**:
- Check that the file exists in the input directory
- Verify the file is a valid image format
- Ensure the file is not corrupted
- Check file permissions

### Memory Issues

**Symptom**: Program slows down or crashes with long videos

**Cause**: High framerate × long duration = many frames in memory

**Solution**: Reduce settings to lower memory usage:

```bash
# Reduce frame rate
uv run python imgToVideo.py --fps 25  # instead of 60

# Reduce duration
uv run python imgToVideo.py --duration 10  # instead of 60

# Or both for very large images
uv run python imgToVideo.py --fps 24 --duration 10
```

### Path Contains Spaces

**Windows**: Use quotes around paths with spaces:

```bash
uv run python imgToVideo.py -i "C:\My Photos" -o "C:\My Videos"
```

## Tips and Best Practices

### Choosing Settings

**Resolution**:
- Match your target platform (YouTube, Instagram, etc.)
- Higher resolution = larger file size and slower processing
- Common: 1920x1080 (Full HD), 3840x2160 (4K), 1080x1080 (Square)

**Frame Rate**:
- 24-30 fps: Standard for most video content
- 60 fps: Smoother motion, larger files
- 25 fps: Good balance (default)

**Duration**:
- 5-10 seconds: Social media, attention-grabbing
- 10-20 seconds: Presentations, storytelling
- Longer: Artistic or ambient content

**Zoom Rate**:
- 0.0002-0.0004: Subtle, slow zoom
- 0.0004-0.0006: Moderate zoom (default range)
- 0.0006-0.001: Fast, dynamic zoom
- Higher than 0.001: Very aggressive (may look unnatural)

**Blur**:
- 151-195: Moderate blur (good for most images)
- 195-255: Strong blur (more artistic)
- Must be odd number
- Higher values = more processing time

### Image Preparation

For best results:
- Use high-resolution images (at least 2-3x your target video resolution)
- Ensure images are well-lit and in focus
- Remove or crop out distracting elements
- Consider the aspect ratio of your target video format

### Batch Processing

- Organize images by project in separate directories
- Use consistent naming for easier management
- Process similar images together with the same settings
- Check output directory has sufficient free space

## Project Structure

```
Image to Video Converter/
├── imgToVideo.py          # Main script
├── pyproject.toml         # Project dependencies (uv)
├── uv.lock                # Locked dependencies
├── requirements.txt       # Pip dependencies (legacy)
├── README.md              # This file
├── CLAUDE.md              # Development guide and roadmap
├── .gitignore             # Git ignore rules
└── .venv/                 # Virtual environment (uv)
```

## Development

See [CLAUDE.md](CLAUDE.md) for development guide and planned improvements roadmap.

### Current Version: 1.0.0

**Recent Updates**:
- ✓ Comprehensive command-line argument support
- ✓ Adaptive interpolation for better quality
- ✓ Robust error handling and validation
- ✓ Migrated to uv for package management

## Technical Details

### Algorithm Overview

1. **Image Loading**: Load source image with OpenCV
2. **Scaling Analysis**: Calculate scale factors based on aspect ratios
3. **Dual Scaling**: Create both fit-to-frame and blurred background versions
4. **Background Blur**: Apply Gaussian blur to background layer
5. **Compositing**: Overlay scaled image on blurred background
6. **Frame Generation**: Create sequence of progressively zoomed frames
7. **Video Writing**: Encode frames to video with specified codec

### Performance Characteristics

**Memory Usage**:
- Approximately: `frame_count × width × height × 3 bytes`
- Example: 250 frames × 1920 × 1080 × 3 = ~1.5 GB RAM

**Processing Time** (approximate, varies by hardware):
- 1920x1080, 10s, 25fps: 5-15 seconds per image
- 3840x2160, 10s, 30fps: 30-60 seconds per image

**File Sizes** (approximate):
- 1080p, 10s, MP4V: 5-20 MB
- 4K, 10s, H.264: 20-80 MB
- Varies significantly based on codec and content

## License

This project is open source. See repository for license details.

## Contributing

Contributions are welcome! Areas for improvement:

- Additional zoom and pan effects
- Configuration file support
- Preview mode before full processing
- Parallel batch processing
- More output format presets
- Quality presets

See [CLAUDE.md](CLAUDE.md) for the complete development roadmap with planned phases.

## Acknowledgments

Built with:
- [OpenCV](https://opencv.org/) - Computer vision and image processing
- [NumPy](https://numpy.org/) - Numerical computing
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer

---

**Created with**: Python 3.10+ and OpenCV 4.6
**Platform**: Cross-platform (Windows, Linux, macOS)
**Status**: Active Development
