"""
Unit tests for the scaleAndBlur() function.

Tests cover:
- Normal operation with various aspect ratios
- Input validation and error handling
- Edge cases (small/large images)
- Blur parameter validation
- Output dimensions and format
"""

import os
import pytest
import numpy as np
import cv2
from pathlib import Path

# Import the function under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from imgToVideo import scaleAndBlur


class TestScaleAndBlurNormalOperation:
    """Test normal operation with valid inputs."""

    @pytest.mark.unit
    def test_wide_image_scaling(self, sample_image_wide):
        """Test scaling a wide (landscape) image."""
        result = scaleAndBlur(str(sample_image_wide), 1920, 1080, 195)

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (1080, 1920, 3), f"Expected (1080, 1920, 3), got {result.shape}"
        assert result.dtype == np.uint8

    @pytest.mark.unit
    def test_narrow_image_scaling(self, sample_image_narrow):
        """Test scaling a narrow (portrait) image."""
        result = scaleAndBlur(str(sample_image_narrow), 1920, 1080, 195)

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (1080, 1920, 3)
        assert result.dtype == np.uint8

    @pytest.mark.unit
    def test_square_image_scaling(self, sample_image_square):
        """Test scaling a square image."""
        result = scaleAndBlur(str(sample_image_square), 1920, 1080, 195)

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (1080, 1920, 3)
        assert result.dtype == np.uint8

    @pytest.mark.unit
    def test_small_image_upscaling(self, sample_image_small):
        """Test upscaling a small image (tests INTER_CUBIC interpolation)."""
        result = scaleAndBlur(str(sample_image_small), 1920, 1080, 195)

        assert result is not None
        assert result.shape == (1080, 1920, 3)
        # Image should be upscaled without artifacts
        assert np.any(result > 0), "Result should contain non-zero values"

    @pytest.mark.unit
    @pytest.mark.slow
    def test_large_image_downscaling(self, sample_image_large):
        """Test downscaling a large image (tests INTER_AREA interpolation)."""
        result = scaleAndBlur(str(sample_image_large), 1920, 1080, 195)

        assert result is not None
        assert result.shape == (1080, 1920, 3)
        assert np.any(result > 0), "Result should contain non-zero values"

    @pytest.mark.unit
    def test_custom_dimensions(self, sample_image_wide):
        """Test with non-standard output dimensions."""
        result = scaleAndBlur(str(sample_image_wide), 1280, 720, 99)

        assert result is not None
        assert result.shape == (720, 1280, 3)

    @pytest.mark.unit
    def test_custom_blur_values(self, sample_image_wide):
        """Test with various valid blur values."""
        # Test different odd blur values
        blur_values = [1, 51, 99, 195, 255]

        for blur in blur_values:
            result = scaleAndBlur(str(sample_image_wide), 1920, 1080, blur)
            assert result is not None
            assert result.shape == (1080, 1920, 3), f"Failed for blur={blur}"

    @pytest.mark.unit
    def test_minimal_blur(self, sample_image_wide):
        """Test with minimal blur value (1)."""
        result = scaleAndBlur(str(sample_image_wide), 1920, 1080, 1)

        assert result is not None
        assert result.shape == (1080, 1920, 3)


class TestScaleAndBlurValidation:
    """Test input validation and error handling."""

    @pytest.mark.unit
    def test_invalid_width_zero(self, sample_image_wide):
        """Test that zero width raises ValueError."""
        with pytest.raises(ValueError, match="Target dimensions must be positive"):
            scaleAndBlur(str(sample_image_wide), 0, 1080, 195)

    @pytest.mark.unit
    def test_invalid_width_negative(self, sample_image_wide):
        """Test that negative width raises ValueError."""
        with pytest.raises(ValueError, match="Target dimensions must be positive"):
            scaleAndBlur(str(sample_image_wide), -1920, 1080, 195)

    @pytest.mark.unit
    def test_invalid_height_zero(self, sample_image_wide):
        """Test that zero height raises ValueError."""
        with pytest.raises(ValueError, match="Target dimensions must be positive"):
            scaleAndBlur(str(sample_image_wide), 1920, 0, 195)

    @pytest.mark.unit
    def test_invalid_height_negative(self, sample_image_wide):
        """Test that negative height raises ValueError."""
        with pytest.raises(ValueError, match="Target dimensions must be positive"):
            scaleAndBlur(str(sample_image_wide), 1920, -1080, 195)

    @pytest.mark.unit
    def test_invalid_blur_zero(self, sample_image_wide):
        """Test that zero blur raises ValueError."""
        with pytest.raises(ValueError, match="Target blur must be positive"):
            scaleAndBlur(str(sample_image_wide), 1920, 1080, 0)

    @pytest.mark.unit
    def test_invalid_blur_negative(self, sample_image_wide):
        """Test that negative blur raises ValueError."""
        with pytest.raises(ValueError, match="Target blur must be positive"):
            scaleAndBlur(str(sample_image_wide), 1920, 1080, -195)

    @pytest.mark.unit
    def test_invalid_blur_even(self, sample_image_wide):
        """Test that even blur value raises ValueError."""
        with pytest.raises(ValueError, match="Target blur must be odd for GaussianBlur"):
            scaleAndBlur(str(sample_image_wide), 1920, 1080, 196)

    @pytest.mark.unit
    def test_nonexistent_file(self):
        """Test that nonexistent file raises ValueError."""
        with pytest.raises(ValueError, match="Failed to load image"):
            scaleAndBlur("nonexistent_file.jpg", 1920, 1080, 195)

    @pytest.mark.unit
    def test_invalid_image_file(self, temp_dir):
        """Test that invalid image file raises ValueError."""
        # Create a text file pretending to be an image
        invalid_file = temp_dir / "invalid.jpg"
        invalid_file.write_text("This is not an image")

        with pytest.raises(ValueError, match="Failed to load image"):
            scaleAndBlur(str(invalid_file), 1920, 1080, 195)


class TestScaleAndBlurOutputQuality:
    """Test output quality and characteristics."""

    @pytest.mark.unit
    def test_output_has_blur_effect(self, sample_image_wide):
        """Test that the output actually has blurred background areas."""
        result = scaleAndBlur(str(sample_image_wide), 1920, 1080, 195)

        # The image should have varying pixel values (not all the same)
        assert np.std(result) > 1, "Output should have variation from blur effect"

    @pytest.mark.unit
    def test_output_is_bgr_format(self, sample_image_wide):
        """Test that output is in BGR format (OpenCV standard)."""
        result = scaleAndBlur(str(sample_image_wide), 1920, 1080, 195)

        # Should have 3 color channels
        assert result.ndim == 3
        assert result.shape[2] == 3

    @pytest.mark.unit
    def test_different_blur_produces_different_results(self, sample_image_narrow):
        """Test that different blur values produce different results in letterbox areas."""
        # Use narrow image to ensure letterbox areas exist where blur is visible
        result_small_blur = scaleAndBlur(str(sample_image_narrow), 1920, 1080, 51)
        result_large_blur = scaleAndBlur(str(sample_image_narrow), 1920, 1080, 195)

        # Results should be different in the letterbox (blurred background) areas
        # Check the edges where letterbox appears
        left_edge_small = result_small_blur[:, :100, :]
        left_edge_large = result_large_blur[:, :100, :]

        assert not np.array_equal(left_edge_small, left_edge_large), \
            "Different blur values should produce different results in background areas"


class TestScaleAndBlurEdgeCases:
    """Test edge cases and unusual inputs."""

    @pytest.mark.unit
    def test_very_small_output_dimensions(self, sample_image_wide):
        """Test with very small output dimensions."""
        result = scaleAndBlur(str(sample_image_wide), 64, 64, 15)

        assert result is not None
        assert result.shape == (64, 64, 3)

    @pytest.mark.unit
    def test_extreme_aspect_ratio_output(self, sample_image_wide):
        """Test with extreme aspect ratio output."""
        # Very wide output
        result = scaleAndBlur(str(sample_image_wide), 3840, 480, 99)

        assert result is not None
        assert result.shape == (480, 3840, 3)

    @pytest.mark.unit
    def test_minimal_blur_value(self, sample_image_wide):
        """Test with minimal valid blur value (1)."""
        result = scaleAndBlur(str(sample_image_wide), 1920, 1080, 1)

        assert result is not None
        assert result.shape == (1080, 1920, 3)

    @pytest.mark.unit
    def test_large_blur_value(self, sample_image_wide):
        """Test with very large blur value."""
        result = scaleAndBlur(str(sample_image_wide), 1920, 1080, 255)

        assert result is not None
        assert result.shape == (1080, 1920, 3)

    @pytest.mark.unit
    def test_same_dimensions_as_input(self, temp_dir):
        """Test when output dimensions match input dimensions."""
        # Create a 1920x1080 image
        img = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        img_path = temp_dir / "exact_size.jpg"
        cv2.imwrite(str(img_path), img)

        result = scaleAndBlur(str(img_path), 1920, 1080, 195)

        assert result is not None
        assert result.shape == (1080, 1920, 3)
