"""
Unit tests for the frames_from_image() generator function.

Tests cover:
- Generator behavior and memory efficiency
- Frame generation with Ken Burns zoom effect
- Input validation and error handling
- Frame count, dimensions, and format
- Zoom progression over time
- Progress bar functionality
"""

import pytest
import numpy as np
from typing import Generator
from pathlib import Path
import sys

# Import the function under test
sys.path.insert(0, str(Path(__file__).parent.parent))
from imgToVideo import frames_from_image


class TestFramesFromImageGeneratorBehavior:
    """Test that the function behaves as a proper generator."""

    @pytest.mark.unit
    def test_returns_generator(self, sample_processed_image):
        """Test that function returns a generator, not a list."""
        result = frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=1,
            show_progress=False
        )

        # Should be a generator
        assert isinstance(result, Generator), "Should return a generator"

    @pytest.mark.unit
    def test_generator_is_memory_efficient(self, sample_processed_image):
        """Test that generator doesn't build entire frame list in memory."""
        # Create generator
        generator = frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=2,  # 50 frames
            show_progress=False
        )

        # Generator object should be small
        import sys
        gen_size = sys.getsizeof(generator)
        assert gen_size < 1000, f"Generator should be small, but is {gen_size} bytes"

        # Consume one frame
        first_frame = next(generator)
        assert first_frame is not None

    @pytest.mark.unit
    def test_generator_can_be_iterated(self, sample_processed_image):
        """Test that generator can be iterated with for loop."""
        frame_count = 0

        for frame in frames_from_image(
            sample_processed_image,
            frameRate=5,
            imgDuration=2,
            show_progress=False
        ):
            frame_count += 1
            assert isinstance(frame, np.ndarray)

        assert frame_count == 10, f"Expected 10 frames, got {frame_count}"


class TestFramesFromImageNormalOperation:
    """Test normal frame generation operation."""

    @pytest.mark.unit
    def test_correct_frame_count(self, sample_processed_image):
        """Test that correct number of frames is generated."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=2,
            show_progress=False
        ))

        expected_count = 25 * 2  # 50 frames
        assert len(frames) == expected_count, f"Expected {expected_count} frames, got {len(frames)}"

    @pytest.mark.unit
    def test_frame_dimensions(self, sample_processed_image):
        """Test that all frames have correct dimensions."""
        target_width, target_height = 1920, 1080

        for frame in frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=1,
            targetWidth=target_width,
            targetHeight=target_height,
            show_progress=False
        ):
            assert frame.shape == (target_height, target_width, 3), \
                f"Expected shape ({target_height}, {target_width}, 3), got {frame.shape}"

    @pytest.mark.unit
    def test_frame_dtype(self, sample_processed_image):
        """Test that frames are uint8 type."""
        generator = frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=1,
            show_progress=False
        )

        first_frame = next(generator)
        assert first_frame.dtype == np.uint8, f"Expected uint8, got {first_frame.dtype}"

    @pytest.mark.unit
    def test_custom_frame_rate(self, sample_processed_image):
        """Test with custom frame rate."""
        fps = 30
        duration = 2

        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=fps,
            imgDuration=duration,
            show_progress=False
        ))

        expected_count = fps * duration
        assert len(frames) == expected_count

    @pytest.mark.unit
    def test_custom_dimensions(self, sample_processed_image):
        """Test with custom output dimensions."""
        width, height = 1280, 720

        for frame in frames_from_image(
            sample_processed_image,
            frameRate=5,
            imgDuration=1,
            targetWidth=width,
            targetHeight=height,
            show_progress=False
        ):
            assert frame.shape == (height, width, 3)

    @pytest.mark.unit
    def test_with_progress_bar_enabled(self, sample_processed_image):
        """Test that show_progress=True doesn't break functionality."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=5,
            imgDuration=1,
            show_progress=True  # Should show tqdm progress
        ))

        assert len(frames) == 5

    @pytest.mark.unit
    def test_with_progress_bar_disabled(self, sample_processed_image):
        """Test that show_progress=False works correctly."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=5,
            imgDuration=1,
            show_progress=False
        ))

        assert len(frames) == 5


class TestFramesFromImageZoomEffect:
    """Test the Ken Burns zoom effect."""

    @pytest.mark.unit
    def test_zoom_progression(self, sample_processed_image):
        """Test that frames progressively zoom in."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=1,
            zoomRate=0.001,  # More noticeable zoom
            show_progress=False
        ))

        # First and last frames should be different (zoom effect)
        first_frame = frames[0]
        last_frame = frames[-1]

        assert not np.array_equal(first_frame, last_frame), \
            "First and last frames should differ due to zoom"

    @pytest.mark.unit
    def test_different_zoom_rates(self, sample_processed_image):
        """Test that different zoom rates produce different results."""
        slow_zoom_frames = list(frames_from_image(
            sample_processed_image,
            frameRate=10,
            imgDuration=1,
            zoomRate=0.0002,
            show_progress=False
        ))

        fast_zoom_frames = list(frames_from_image(
            sample_processed_image,
            frameRate=10,
            imgDuration=1,
            zoomRate=0.002,
            show_progress=False
        ))

        # Last frames should be significantly different
        assert not np.array_equal(slow_zoom_frames[-1], fast_zoom_frames[-1]), \
            "Different zoom rates should produce different results"

    @pytest.mark.unit
    def test_zero_zoom_rate(self, sample_processed_image):
        """Test with zero zoom rate (static frames)."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=5,
            imgDuration=1,
            zoomRate=0.0,  # No zoom
            show_progress=False
        ))

        # All frames should be nearly identical (allowing for interpolation differences)
        first_frame = frames[0]
        for frame in frames[1:]:
            # Frames might have tiny differences due to resize operations
            diff = np.abs(frame.astype(float) - first_frame.astype(float)).mean()
            assert diff < 1.0, f"With zero zoom, frames should be nearly identical (diff={diff})"


class TestFramesFromImageValidation:
    """Test input validation and error handling."""

    @pytest.mark.unit
    def test_invalid_frame_rate_zero(self, sample_processed_image):
        """Test that zero frame rate raises ValueError."""
        with pytest.raises(ValueError, match="Frame rate must be positive"):
            list(frames_from_image(
                sample_processed_image,
                frameRate=0,
                imgDuration=10,
                show_progress=False
            ))

    @pytest.mark.unit
    def test_invalid_frame_rate_negative(self, sample_processed_image):
        """Test that negative frame rate raises ValueError."""
        with pytest.raises(ValueError, match="Frame rate must be positive"):
            list(frames_from_image(
                sample_processed_image,
                frameRate=-25,
                imgDuration=10,
                show_progress=False
            ))

    @pytest.mark.unit
    def test_invalid_duration_zero(self, sample_processed_image):
        """Test that zero duration raises ValueError."""
        with pytest.raises(ValueError, match="Image duration must be positive"):
            list(frames_from_image(
                sample_processed_image,
                frameRate=25,
                imgDuration=0,
                show_progress=False
            ))

    @pytest.mark.unit
    def test_invalid_duration_negative(self, sample_processed_image):
        """Test that negative duration raises ValueError."""
        with pytest.raises(ValueError, match="Image duration must be positive"):
            list(frames_from_image(
                sample_processed_image,
                frameRate=25,
                imgDuration=-10,
                show_progress=False
            ))

    @pytest.mark.unit
    def test_invalid_zoom_rate_negative(self, sample_processed_image):
        """Test that negative zoom rate raises ValueError."""
        with pytest.raises(ValueError, match="Zoom rate must be between 0 and 0.1"):
            list(frames_from_image(
                sample_processed_image,
                frameRate=25,
                imgDuration=10,
                zoomRate=-0.001,
                show_progress=False
            ))

    @pytest.mark.unit
    def test_invalid_zoom_rate_too_large(self, sample_processed_image):
        """Test that zoom rate > 0.1 raises ValueError."""
        with pytest.raises(ValueError, match="Zoom rate must be between 0 and 0.1"):
            list(frames_from_image(
                sample_processed_image,
                frameRate=25,
                imgDuration=10,
                zoomRate=0.15,
                show_progress=False
            ))

    @pytest.mark.unit
    def test_invalid_target_width_zero(self, sample_processed_image):
        """Test that zero target width raises ValueError."""
        with pytest.raises(ValueError, match="Target dimensions must be positive"):
            list(frames_from_image(
                sample_processed_image,
                frameRate=25,
                imgDuration=10,
                targetWidth=0,
                targetHeight=1080,
                show_progress=False
            ))

    @pytest.mark.unit
    def test_invalid_target_height_negative(self, sample_processed_image):
        """Test that negative target height raises ValueError."""
        with pytest.raises(ValueError, match="Target dimensions must be positive"):
            list(frames_from_image(
                sample_processed_image,
                frameRate=25,
                imgDuration=10,
                targetWidth=1920,
                targetHeight=-1080,
                show_progress=False
            ))


class TestFramesFromImageEdgeCases:
    """Test edge cases and unusual inputs."""

    @pytest.mark.unit
    def test_very_short_duration(self, sample_processed_image):
        """Test with very short duration (1 frame)."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=1,
            imgDuration=1,
            show_progress=False
        ))

        assert len(frames) == 1

    @pytest.mark.unit
    @pytest.mark.slow
    def test_long_duration(self, sample_processed_image):
        """Test with long duration."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=60,  # 1 minute = 1500 frames
            show_progress=False
        ))

        assert len(frames) == 1500

    @pytest.mark.unit
    def test_high_frame_rate(self, sample_processed_image):
        """Test with high frame rate."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=60,
            imgDuration=1,
            show_progress=False
        ))

        assert len(frames) == 60

    @pytest.mark.unit
    def test_small_output_dimensions(self, sample_processed_image):
        """Test with very small output dimensions."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=5,
            imgDuration=1,
            targetWidth=320,
            targetHeight=240,
            show_progress=False
        ))

        assert len(frames) == 5
        for frame in frames:
            assert frame.shape == (240, 320, 3)

    @pytest.mark.unit
    def test_maximum_zoom_rate(self, sample_processed_image):
        """Test with maximum allowed zoom rate."""
        frames = list(frames_from_image(
            sample_processed_image,
            frameRate=5,
            imgDuration=1,
            zoomRate=0.1,  # Maximum allowed
            show_progress=False
        ))

        assert len(frames) == 5
        # Should still produce valid frames
        for frame in frames:
            assert frame.shape == (1080, 1920, 3)


class TestFramesFromImagePerformance:
    """Test performance characteristics."""

    @pytest.mark.unit
    def test_lazy_evaluation(self, sample_processed_image):
        """Test that frames are generated lazily, not all at once."""
        generator = frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=10,  # 250 frames
            show_progress=False
        )

        # Generator should be created instantly
        import time
        start = time.time()
        _ = frames_from_image(
            sample_processed_image,
            frameRate=25,
            imgDuration=10,
            show_progress=False
        )
        creation_time = time.time() - start

        # Creation should be very fast (< 0.1 second)
        assert creation_time < 0.1, \
            f"Generator creation took {creation_time}s, should be instant"

    @pytest.mark.unit
    def test_frames_consumed_one_at_a_time(self, sample_processed_image):
        """Test that frames are generated one at a time."""
        generator = frames_from_image(
            sample_processed_image,
            frameRate=5,
            imgDuration=2,
            zoomRate=0.01,  # Use higher zoom rate to ensure visible differences
            show_progress=False
        )

        # Get frames one by one
        frame1 = next(generator)
        assert frame1 is not None

        # Skip a few frames to get more noticeable difference
        frame2 = next(generator)
        frame3 = next(generator)
        frame4 = next(generator)

        assert frame4 is not None
        # First and fourth frames should be noticeably different with zoom
        diff = np.abs(frame1.astype(float) - frame4.astype(float)).mean()
        assert diff > 0.1, f"Frames should differ due to zoom (diff={diff})"
