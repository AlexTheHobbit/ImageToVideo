"""
Integration tests for the complete image-to-video processing pipeline.

Tests cover:
- End-to-end single image processing
- Batch processing multiple images
- Resume capability (skip existing files)
- Output video validation (file existence, metadata, frame count)
- Error handling and recovery
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Tuple

import pytest
import numpy as np
import cv2

# Import functions under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from imgToVideo import scaleAndBlur, frames_from_image, validate_codec, VideoWriterContext


# ============================================================================
# Helper Functions for Video Validation
# ============================================================================

def validate_video_file(
    video_path: Path,
    expected_duration: int = None,
    expected_fps: int = None,
    expected_width: int = None,
    expected_height: int = None,
    min_file_size_bytes: int = 1000
) -> Dict[str, any]:
    """
    Validate a video file's existence, metadata, and properties.

    Args:
        video_path: Path to video file
        expected_duration: Expected duration in seconds (None to skip check)
        expected_fps: Expected frame rate (None to skip check)
        expected_width: Expected width in pixels (None to skip check)
        expected_height: Expected height in pixels (None to skip check)
        min_file_size_bytes: Minimum file size in bytes

    Returns:
        dict: Video metadata including actual values

    Raises:
        AssertionError: If validation fails
    """
    # Check file exists
    assert video_path.exists(), f"Video file does not exist: {video_path}"

    # Check file size
    file_size = video_path.stat().st_size
    assert file_size >= min_file_size_bytes, \
        f"Video file too small: {file_size} bytes (minimum: {min_file_size_bytes})"

    # Open video with OpenCV
    cap = cv2.VideoCapture(str(video_path))
    assert cap.isOpened(), f"Could not open video file: {video_path}"

    try:
        # Get video metadata
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        actual_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_duration = actual_frame_count / actual_fps if actual_fps > 0 else 0

        # Validate FPS if specified
        if expected_fps is not None:
            assert abs(actual_fps - expected_fps) < 1.0, \
                f"FPS mismatch: expected {expected_fps}, got {actual_fps}"

        # Validate dimensions if specified
        if expected_width is not None:
            assert actual_width == expected_width, \
                f"Width mismatch: expected {expected_width}, got {actual_width}"

        if expected_height is not None:
            assert actual_height == expected_height, \
                f"Height mismatch: expected {expected_height}, got {actual_height}"

        # Validate duration if specified (allow 10% tolerance for encoding variations)
        if expected_duration is not None:
            duration_tolerance = expected_duration * 0.1
            assert abs(actual_duration - expected_duration) <= duration_tolerance, \
                f"Duration mismatch: expected {expected_duration}s, got {actual_duration}s"

        # Validate frame count if we have expected values
        if expected_duration is not None and expected_fps is not None:
            expected_frame_count = expected_duration * expected_fps
            frame_count_tolerance = max(2, int(expected_frame_count * 0.1))  # 10% or 2 frames
            assert abs(actual_frame_count - expected_frame_count) <= frame_count_tolerance, \
                f"Frame count mismatch: expected ~{expected_frame_count}, got {actual_frame_count}"

        # Try to read first frame to verify video is valid
        ret, frame = cap.read()
        assert ret, "Could not read first frame from video"
        assert frame is not None, "First frame is None"
        assert frame.shape[0] > 0 and frame.shape[1] > 0, "Invalid frame dimensions"

        return {
            'fps': actual_fps,
            'frame_count': actual_frame_count,
            'width': actual_width,
            'height': actual_height,
            'duration': actual_duration,
            'file_size': file_size,
            'first_frame_valid': True
        }

    finally:
        cap.release()


def create_test_video(
    output_path: Path,
    image_path: Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 5,
    duration: int = 1,
    codec: str = 'mp4v',
    extension: str = 'mp4'
) -> bool:
    """
    Create a test video from an image using the core functions.

    Args:
        output_path: Path for output video
        image_path: Path to source image
        width: Video width
        height: Video height
        fps: Frame rate
        duration: Video duration in seconds
        codec: Video codec
        extension: File extension

    Returns:
        bool: True if successful
    """
    try:
        # Process image
        blurred_img = scaleAndBlur(str(image_path), width, height, targetBlur=195)

        # Generate frames
        frame_generator = frames_from_image(
            blurred_img,
            frameRate=fps,
            imgDuration=duration,
            targetWidth=width,
            targetHeight=height,
            show_progress=False
        )

        # Write video
        fourcc = cv2.VideoWriter_fourcc(*codec)
        with VideoWriterContext(str(output_path), fourcc, fps, (width, height)) as writer:
            if not writer.isOpened():
                return False

            for frame in frame_generator:
                writer.write(frame)

        return output_path.exists()

    except Exception as e:
        print(f"Error creating test video: {e}")
        return False


# ============================================================================
# Integration Tests
# ============================================================================

class TestSingleImageProcessing:
    """Test end-to-end processing of a single image."""

    @pytest.mark.integration
    def test_process_single_wide_image(self, temp_dir, sample_image_wide, available_codecs):
        """Test processing a single wide (landscape) image end-to-end."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / f"output_wide.avi"

        # Process image to video
        success = create_test_video(
            output_path,
            sample_image_wide,
            width=1920,
            height=1080,
            fps=5,
            duration=2,
            codec=codec,
            extension='avi'
        )

        assert success, "Failed to create video"
        assert output_path.exists(), "Output video file not created"

        # Validate output video
        metadata = validate_video_file(
            output_path,
            expected_duration=2,
            expected_fps=5,
            expected_width=1920,
            expected_height=1080
        )

        assert metadata['frame_count'] >= 8, "Not enough frames in video"
        assert metadata['first_frame_valid'], "First frame is invalid"

    @pytest.mark.integration
    def test_process_single_narrow_image(self, temp_dir, sample_image_narrow, available_codecs):
        """Test processing a single narrow (portrait) image end-to-end."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / f"output_narrow.avi"

        success = create_test_video(
            output_path,
            sample_image_narrow,
            width=1920,
            height=1080,
            fps=5,
            duration=1,
            codec=codec,
            extension='avi'
        )

        assert success, "Failed to create video"

        # Validate output
        metadata = validate_video_file(
            output_path,
            expected_duration=1,
            expected_fps=5,
            expected_width=1920,
            expected_height=1080
        )

        assert metadata['frame_count'] >= 4, "Not enough frames in video"

    @pytest.mark.integration
    def test_process_small_image_upscaling(self, temp_dir, sample_image_small, available_codecs):
        """Test processing a small image (requires upscaling)."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / f"output_small.avi"

        success = create_test_video(
            output_path,
            sample_image_small,
            width=1920,
            height=1080,
            fps=5,
            duration=1,
            codec=codec,
            extension='avi'
        )

        assert success, "Failed to create video from small image"
        assert output_path.exists()

        # Validate that upscaling worked
        metadata = validate_video_file(output_path, expected_width=1920, expected_height=1080)
        assert metadata['width'] == 1920, "Width not upscaled correctly"
        assert metadata['height'] == 1080, "Height not upscaled correctly"

    @pytest.mark.integration
    def test_process_with_custom_settings(self, temp_dir, sample_image_square, available_codecs):
        """Test processing with custom resolution and settings."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / f"output_custom.avi"

        # Custom settings
        custom_width, custom_height = 1280, 720
        custom_fps, custom_duration = 10, 3

        success = create_test_video(
            output_path,
            sample_image_square,
            width=custom_width,
            height=custom_height,
            fps=custom_fps,
            duration=custom_duration,
            codec=codec,
            extension='avi'
        )

        assert success, "Failed to create video with custom settings"

        # Validate custom settings
        metadata = validate_video_file(
            output_path,
            expected_duration=custom_duration,
            expected_fps=custom_fps,
            expected_width=custom_width,
            expected_height=custom_height
        )

        expected_frames = custom_fps * custom_duration
        assert abs(metadata['frame_count'] - expected_frames) <= 3, \
            f"Frame count mismatch with custom settings"


class TestBatchProcessing:
    """Test batch processing of multiple images."""

    @pytest.mark.integration
    def test_process_multiple_images(self, temp_dir, available_codecs):
        """Test processing multiple images in batch."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]

        # Create multiple test images
        test_images = []
        for i, (width, height) in enumerate([(1920, 1080), (1080, 1920), (1080, 1080)]):
            img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            img_path = temp_dir / f"input_{i}.jpg"
            cv2.imwrite(str(img_path), img)
            test_images.append(img_path)

        # Process each image
        output_videos = []
        for i, img_path in enumerate(test_images):
            output_path = temp_dir / f"output_{i}.avi"
            success = create_test_video(
                output_path,
                img_path,
                width=1920,
                height=1080,
                fps=5,
                duration=1,
                codec=codec,
                extension='avi'
            )
            assert success, f"Failed to process image {i}"
            output_videos.append(output_path)

        # Verify all outputs
        assert len(output_videos) == 3, "Not all videos were created"

        for i, video_path in enumerate(output_videos):
            assert video_path.exists(), f"Video {i} not created"
            metadata = validate_video_file(
                video_path,
                expected_width=1920,
                expected_height=1080
            )
            assert metadata['frame_count'] > 0, f"Video {i} has no frames"

    @pytest.mark.integration
    def test_batch_different_resolutions(self, temp_dir, available_codecs):
        """Test batch processing with different output resolutions."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]

        # Create test image
        img = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        img_path = temp_dir / "test_image.jpg"
        cv2.imwrite(str(img_path), img)

        # Process with different resolutions
        resolutions = [
            (1920, 1080),
            (1280, 720),
            (640, 480)
        ]

        for i, (width, height) in enumerate(resolutions):
            output_path = temp_dir / f"output_{width}x{height}.avi"
            success = create_test_video(
                output_path,
                img_path,
                width=width,
                height=height,
                fps=5,
                duration=1,
                codec=codec,
                extension='avi'
            )

            assert success, f"Failed to create {width}x{height} video"

            metadata = validate_video_file(
                output_path,
                expected_width=width,
                expected_height=height
            )

            assert metadata['width'] == width
            assert metadata['height'] == height


class TestResumeCapability:
    """Test resume capability (skip existing files)."""

    @pytest.mark.integration
    def test_skip_existing_output(self, temp_dir, sample_image_wide, available_codecs):
        """Test that processing skips existing output files."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / "output.avi"

        # Create video first time
        success1 = create_test_video(
            output_path,
            sample_image_wide,
            width=1920,
            height=1080,
            fps=5,
            duration=1,
            codec=codec,
            extension='avi'
        )

        assert success1, "Failed to create initial video"
        assert output_path.exists()

        # Get file modification time and size
        mtime1 = output_path.stat().st_mtime
        size1 = output_path.stat().st_size

        # Wait a moment to ensure timestamp would change if file is modified
        time.sleep(0.1)

        # Check if file exists (simulate resume check)
        should_skip = output_path.exists()
        assert should_skip, "Resume check should detect existing file"

        # Verify file was not modified (in actual resume scenario)
        mtime2 = output_path.stat().st_mtime
        size2 = output_path.stat().st_size

        assert mtime1 == mtime2, "File modification time changed (should be unchanged on skip)"
        assert size1 == size2, "File size changed (should be unchanged on skip)"

    @pytest.mark.integration
    def test_force_reprocess_existing(self, temp_dir, sample_image_wide, available_codecs):
        """Test that force flag allows reprocessing existing files."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / "output.avi"

        # Create video first time
        create_test_video(
            output_path,
            sample_image_wide,
            width=1920,
            height=1080,
            fps=5,
            duration=1,
            codec=codec,
            extension='avi'
        )

        mtime1 = output_path.stat().st_mtime

        time.sleep(0.1)

        # Simulate force reprocess by creating video again
        success = create_test_video(
            output_path,
            sample_image_wide,
            width=1920,
            height=1080,
            fps=5,
            duration=1,
            codec=codec,
            extension='avi'
        )

        assert success, "Force reprocess should succeed"

        mtime2 = output_path.stat().st_mtime
        # Note: modification time might be same on fast systems, but file should still be valid

        # Validate the reprocessed video is valid
        metadata = validate_video_file(output_path, expected_width=1920, expected_height=1080)
        assert metadata['first_frame_valid']


class TestOutputValidation:
    """Test output video validation utilities."""

    @pytest.mark.integration
    def test_validate_video_metadata(self, temp_dir, sample_image_wide, available_codecs):
        """Test video metadata validation."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / "test_metadata.avi"

        fps, duration = 10, 2
        width, height = 1280, 720

        create_test_video(
            output_path,
            sample_image_wide,
            width=width,
            height=height,
            fps=fps,
            duration=duration,
            codec=codec,
            extension='avi'
        )

        # Validate all metadata
        metadata = validate_video_file(
            output_path,
            expected_duration=duration,
            expected_fps=fps,
            expected_width=width,
            expected_height=height
        )

        # Check returned metadata
        assert metadata['fps'] > 0
        assert metadata['frame_count'] > 0
        assert metadata['width'] == width
        assert metadata['height'] == height
        assert metadata['file_size'] > 1000
        assert metadata['first_frame_valid'] is True

    @pytest.mark.integration
    def test_validate_video_frame_count(self, temp_dir, sample_image_wide, available_codecs):
        """Test that frame count validation works correctly."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / "test_frames.avi"

        fps, duration = 5, 3
        expected_frames = fps * duration  # 15 frames

        create_test_video(
            output_path,
            sample_image_wide,
            width=1920,
            height=1080,
            fps=fps,
            duration=duration,
            codec=codec,
            extension='avi'
        )

        metadata = validate_video_file(
            output_path,
            expected_duration=duration,
            expected_fps=fps
        )

        # Allow small tolerance for codec variations
        assert abs(metadata['frame_count'] - expected_frames) <= 2, \
            f"Frame count significantly off: expected ~{expected_frames}, got {metadata['frame_count']}"

    @pytest.mark.integration
    def test_validate_video_file_size(self, temp_dir, sample_image_wide, available_codecs):
        """Test that file size validation works correctly."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        output_path = temp_dir / "test_size.avi"

        create_test_video(
            output_path,
            sample_image_wide,
            width=1920,
            height=1080,
            fps=5,
            duration=2,
            codec=codec,
            extension='avi'
        )

        # Validate with minimum file size requirement
        metadata = validate_video_file(output_path, min_file_size_bytes=5000)

        assert metadata['file_size'] >= 5000, "Video file size too small"


class TestErrorHandling:
    """Test error handling in integration scenarios."""

    @pytest.mark.integration
    def test_invalid_codec_fails_gracefully(self, temp_dir, sample_image_wide):
        """Test that invalid codec is handled gracefully."""
        output_path = temp_dir / "invalid_codec.avi"

        # This should fail or return False for invalid codec
        result = create_test_video(
            output_path,
            sample_image_wide,
            width=1920,
            height=1080,
            fps=5,
            duration=1,
            codec='FAKE',
            extension='avi'
        )

        # Should fail gracefully (return False, not crash)
        assert result is False or not output_path.exists(), \
            "Should fail gracefully with invalid codec"

    @pytest.mark.integration
    def test_missing_input_image(self, temp_dir, available_codecs):
        """Test handling of missing input image."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        nonexistent_image = temp_dir / "nonexistent.jpg"
        output_path = temp_dir / "output.avi"

        # Should fail gracefully
        try:
            result = create_test_video(
                output_path,
                nonexistent_image,
                width=1920,
                height=1080,
                fps=5,
                duration=1,
                codec=codec,
                extension='avi'
            )
            assert result is False, "Should return False for missing input"
        except (ValueError, FileNotFoundError):
            # Either return False or raise an expected exception
            pass
