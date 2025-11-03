"""
Integration tests for video stitching functionality.

Tests cover:
- Successful stitching of multiple videos
- Edge cases (empty list, single video, no videos)
- Dimension mismatch handling
- Progress bar behavior (show_progress flag)
- Error handling and cleanup
- Frame count accuracy
- Output video validation
"""

import os
from pathlib import Path
from typing import List

import pytest
import numpy as np
import cv2

# Import functions under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from imgToVideo import stitch_videos, VideoWriterContext, validate_codec


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_video(
    output_path: Path,
    width: int,
    height: int,
    fps: int,
    num_frames: int,
    codec: str = 'mp4v',
    color: tuple = (128, 128, 128)
) -> Path:
    """
    Create a simple test video with solid color frames.

    Args:
        output_path: Path for output video
        width: Video width
        height: Video height
        fps: Frame rate
        num_frames: Number of frames to generate
        codec: Video codec
        color: RGB color for frames

    Returns:
        Path: Path to created video
    """
    fourcc = cv2.VideoWriter_fourcc(*codec)

    with VideoWriterContext(str(output_path), fourcc, fps, (width, height)) as out:
        for i in range(num_frames):
            # Create frame with color (add frame number for variation)
            frame = np.full((height, width, 3), color, dtype=np.uint8)
            # Add a number indicator in corner
            cv2.putText(frame, str(i), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            out.write(frame)

    return output_path


def get_video_frame_count(video_path: Path) -> int:
    """Get the number of frames in a video file."""
    cap = cv2.VideoCapture(str(video_path))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frame_count


def get_video_dimensions(video_path: Path) -> tuple:
    """Get the dimensions (width, height) of a video file."""
    cap = cv2.VideoCapture(str(video_path))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return (width, height)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_videos_same_size(temp_dir, available_codecs):
    """Create 3 test videos with the same dimensions."""
    if not available_codecs:
        pytest.skip("No available codecs found on system")

    codec = available_codecs[0]
    videos = []
    for i in range(3):
        video_path = temp_dir / f"test_video_{i}.mp4"
        create_test_video(
            video_path,
            width=640,
            height=480,
            fps=10,
            num_frames=10,
            codec=codec,
            color=(i * 80, 128, 255 - i * 80)  # Different colors
        )
        videos.append(str(video_path))
    return videos, codec


@pytest.fixture
def test_videos_different_sizes(temp_dir, available_codecs):
    """Create 2 test videos with different dimensions."""
    if not available_codecs:
        pytest.skip("No available codecs found on system")

    codec = available_codecs[0]
    videos = []

    # Video 1: 640x480
    video1 = temp_dir / "video_640x480.mp4"
    create_test_video(video1, 640, 480, 10, 10, codec)
    videos.append(str(video1))

    # Video 2: 320x240 (different size)
    video2 = temp_dir / "video_320x240.mp4"
    create_test_video(video2, 320, 240, 10, 10, codec)
    videos.append(str(video2))

    return videos, codec


# ============================================================================
# Tests: Successful Stitching
# ============================================================================

@pytest.mark.integration
def test_stitch_multiple_videos_success(test_videos_same_size, temp_dir):
    """Test successful stitching of multiple videos."""
    videos, codec = test_videos_same_size
    output_path = str(temp_dir / "stitched_output.mp4")

    result = stitch_videos(
        video_files=videos,
        output_path=output_path,
        codec=codec,
        fps=10,
        width=640,
        height=480,
        show_progress=False
    )

    assert result is True
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 1000  # Not empty

    # Verify frame count (3 videos * 10 frames each = 30 frames)
    frame_count = get_video_frame_count(Path(output_path))
    assert frame_count == 30, f"Expected 30 frames, got {frame_count}"


@pytest.mark.integration
def test_stitch_maintains_video_order(test_videos_same_size, temp_dir):
    """Test that videos are stitched in the order provided."""
    videos, codec = test_videos_same_size
    output_path = str(temp_dir / "stitched_ordered.mp4")

    # Stitch in specific order
    result = stitch_videos(
        video_files=videos,
        output_path=output_path,
        codec=codec,
        fps=10,
        width=640,
        height=480,
        show_progress=False
    )

    assert result is True

    # Read first few frames from output and verify they match first input video
    cap_output = cv2.VideoCapture(output_path)
    cap_first_input = cv2.VideoCapture(videos[0])

    # Compare first frame
    ret_out, frame_out = cap_output.read()
    ret_in, frame_in = cap_first_input.read()

    assert ret_out and ret_in
    # Frames should be very similar (allowing for encoding differences)
    diff = cv2.absdiff(frame_out, frame_in)
    mean_diff = np.mean(diff)
    assert mean_diff < 5.0, f"First frame differs too much: {mean_diff}"

    cap_output.release()
    cap_first_input.release()


@pytest.mark.integration
def test_stitch_with_progress_disabled(test_videos_same_size, temp_dir):
    """Test stitching with progress bar disabled."""
    videos, codec = test_videos_same_size
    output_path = str(temp_dir / "stitched_no_progress.mp4")

    result = stitch_videos(
        video_files=videos,
        output_path=output_path,
        codec=codec,
        fps=10,
        width=640,
        height=480,
        show_progress=False
    )

    assert result is True
    assert os.path.exists(output_path)


@pytest.mark.integration
def test_stitch_with_progress_enabled(test_videos_same_size, temp_dir, capsys):
    """Test stitching with progress bar enabled."""
    videos, codec = test_videos_same_size
    output_path = str(temp_dir / "stitched_with_progress.mp4")

    result = stitch_videos(
        video_files=videos,
        output_path=output_path,
        codec=codec,
        fps=10,
        width=640,
        height=480,
        show_progress=True
    )

    assert result is True
    assert os.path.exists(output_path)


@pytest.mark.integration
def test_stitch_two_videos(temp_dir, available_codecs):
    """Test stitching exactly two videos."""
    if not available_codecs:
        pytest.skip("No available codecs found on system")

    codec = available_codecs[0]

    # Create 2 videos
    video1 = temp_dir / "video1.mp4"
    video2 = temp_dir / "video2.mp4"
    create_test_video(video1, 320, 240, 5, 5, codec, (255, 0, 0))
    create_test_video(video2, 320, 240, 5, 5, codec, (0, 255, 0))

    output_path = str(temp_dir / "two_videos_stitched.mp4")

    result = stitch_videos(
        video_files=[str(video1), str(video2)],
        output_path=output_path,
        codec=codec,
        fps=5,
        width=320,
        height=240,
        show_progress=False
    )

    assert result is True
    frame_count = get_video_frame_count(Path(output_path))
    assert frame_count == 10, f"Expected 10 frames, got {frame_count}"


@pytest.mark.integration
def test_stitch_creates_correct_dimensions(test_videos_same_size, temp_dir):
    """Test that output video has correct dimensions."""
    videos, codec = test_videos_same_size
    output_path = str(temp_dir / "stitched_dims.mp4")

    result = stitch_videos(
        video_files=videos,
        output_path=output_path,
        codec=codec,
        fps=10,
        width=640,
        height=480,
        show_progress=False
    )

    assert result is True
    dims = get_video_dimensions(Path(output_path))
    assert dims == (640, 480), f"Expected (640, 480), got {dims}"


# ============================================================================
# Tests: Edge Cases
# ============================================================================

@pytest.mark.unit
def test_stitch_empty_video_list_raises_error(temp_dir, available_codecs):
    """Test that empty video list raises ValueError."""
    if not available_codecs:
        pytest.skip("No available codecs found on system")

    codec = available_codecs[0]
    output_path = str(temp_dir / "output.mp4")

    with pytest.raises(ValueError, match="No video files provided"):
        stitch_videos(
            video_files=[],
            output_path=output_path,
            codec=codec,
            fps=10,
            width=640,
            height=480
        )


@pytest.mark.unit
def test_stitch_empty_output_path_raises_error(available_codecs):
    """Test that empty output path raises ValueError."""
    if not available_codecs:
        pytest.skip("No available codecs found on system")

    codec = available_codecs[0]

    with pytest.raises(ValueError, match="Output path cannot be empty"):
        stitch_videos(
            video_files=["video1.mp4"],
            output_path="",
            codec=codec,
            fps=10,
            width=640,
            height=480
        )


@pytest.mark.integration
def test_stitch_dimension_mismatch_raises_error(test_videos_different_sizes, temp_dir):
    """Test that videos with different dimensions raise RuntimeError."""
    videos, codec = test_videos_different_sizes
    output_path = str(temp_dir / "mismatched_output.mp4")

    with pytest.raises(RuntimeError, match="different dimensions"):
        stitch_videos(
            video_files=videos,
            output_path=output_path,
            codec=codec,
            fps=10,
            width=640,  # First video size
            height=480,
            show_progress=False
        )


@pytest.mark.integration
def test_stitch_nonexistent_video_raises_error(temp_dir, available_codecs):
    """Test that nonexistent video file raises RuntimeError."""
    if not available_codecs:
        pytest.skip("No available codecs found on system")

    codec = available_codecs[0]
    output_path = str(temp_dir / "output.mp4")
    fake_video = str(temp_dir / "nonexistent.mp4")

    with pytest.raises(RuntimeError, match="Failed to open video file"):
        stitch_videos(
            video_files=[fake_video],
            output_path=output_path,
            codec=codec,
            fps=10,
            width=640,
            height=480,
            show_progress=False
        )


# ============================================================================
# Tests: Error Handling and Cleanup
# ============================================================================

@pytest.mark.integration
def test_stitch_cleans_up_on_error(temp_dir, available_codecs):
    """Test that partial output file is cleaned up on error."""
    if not available_codecs:
        pytest.skip("No available codecs found on system")

    codec = available_codecs[0]
    output_path = str(temp_dir / "cleanup_test.mp4")
    fake_video = str(temp_dir / "nonexistent.mp4")

    # Verify output doesn't exist before
    assert not os.path.exists(output_path)

    # Try to stitch (will fail)
    with pytest.raises(RuntimeError):
        stitch_videos(
            video_files=[fake_video],
            output_path=output_path,
            codec=codec,
            fps=10,
            width=640,
            height=480,
            show_progress=False
        )

    # Verify cleanup occurred (file should not exist or be empty)
    # Note: File might not exist at all, which is fine
    if os.path.exists(output_path):
        assert os.path.getsize(output_path) == 0


@pytest.mark.integration
def test_stitch_single_video_works(temp_dir, available_codecs):
    """Test stitching a single video (edge case but should work)."""
    if not available_codecs:
        pytest.skip("No available codecs found on system")

    codec = available_codecs[0]

    # Create single video
    video1 = temp_dir / "single.mp4"
    create_test_video(video1, 320, 240, 5, 15, codec)

    output_path = str(temp_dir / "single_stitched.mp4")

    result = stitch_videos(
        video_files=[str(video1)],
        output_path=output_path,
        codec=codec,
        fps=5,
        width=320,
        height=240,
        show_progress=False
    )

    assert result is True
    # Should have same frame count as input
    frame_count = get_video_frame_count(Path(output_path))
    assert frame_count == 15


# ============================================================================
# Tests: Video Validation
# ============================================================================

@pytest.mark.integration
def test_stitched_video_is_playable(test_videos_same_size, temp_dir):
    """Test that stitched video can be opened and read."""
    videos, codec = test_videos_same_size
    output_path = str(temp_dir / "playable.mp4")

    stitch_videos(
        video_files=videos,
        output_path=output_path,
        codec=codec,
        fps=10,
        width=640,
        height=480,
        show_progress=False
    )

    # Try to read all frames
    cap = cv2.VideoCapture(output_path)
    assert cap.isOpened()

    frames_read = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        assert frame is not None
        assert frame.shape == (480, 640, 3)
        frames_read += 1

    cap.release()
    assert frames_read == 30  # 3 videos * 10 frames each
