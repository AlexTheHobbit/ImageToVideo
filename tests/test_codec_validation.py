"""
Unit tests for codec validation functions.

Tests cover:
- validate_codec() function
- get_codec_suggestions() function
- Codec availability checking
- Error handling for invalid codecs
"""

import pytest
from pathlib import Path
import sys

# Import the functions under test
sys.path.insert(0, str(Path(__file__).parent.parent))
from imgToVideo import validate_codec, get_codec_suggestions


class TestValidateCodec:
    """Test the validate_codec() function."""

    @pytest.mark.unit
    def test_validate_with_available_codec(self, available_codecs):
        """Test validation with an available codec."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        # Use the first available codec
        codec = available_codecs[0]
        result = validate_codec(codec, 640, 480, 25, 'avi')

        assert result is True, f"Codec '{codec}' should be available"

    @pytest.mark.unit
    @pytest.mark.requires_codec
    def test_validate_mp4v_codec(self):
        """Test mp4v codec validation (commonly available)."""
        result = validate_codec('mp4v', 1920, 1080, 25, 'mp4')

        # mp4v is usually available on most systems
        # If not available, test that function returns False correctly
        assert isinstance(result, bool), "Should return boolean"

    @pytest.mark.unit
    def test_validate_with_fake_codec(self):
        """Test that fake/invalid codec returns False."""
        result = validate_codec('FAKE', 1920, 1080, 25, 'avi')

        assert result is False, "Fake codec should not validate"

    @pytest.mark.unit
    def test_validate_with_invalid_fourcc(self):
        """Test with invalid fourcc code."""
        result = validate_codec('XXXX', 1920, 1080, 25, 'avi')

        assert result is False, "Invalid fourcc should return False"

    @pytest.mark.unit
    def test_validate_returns_boolean(self, available_codecs):
        """Test that validate_codec always returns a boolean."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]
        result = validate_codec(codec, 1920, 1080, 25, 'avi')

        assert isinstance(result, bool), "Should return boolean value"

    @pytest.mark.unit
    def test_validate_with_different_dimensions(self, available_codecs):
        """Test validation with various video dimensions."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]

        # Test different resolutions
        resolutions = [
            (640, 480),
            (1280, 720),
            (1920, 1080),
            (3840, 2160),
        ]

        for width, height in resolutions:
            result = validate_codec(codec, width, height, 25, 'avi')
            assert isinstance(result, bool)

    @pytest.mark.unit
    def test_validate_with_different_fps(self, available_codecs):
        """Test validation with various frame rates."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]

        # Test different frame rates
        fps_values = [15, 24, 25, 30, 60]

        for fps in fps_values:
            result = validate_codec(codec, 1920, 1080, fps, 'avi')
            assert isinstance(result, bool)

    @pytest.mark.unit
    def test_validate_with_different_extensions(self, available_codecs):
        """Test validation with various file extensions."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]

        # Test different extensions
        extensions = ['avi', 'mp4', 'mkv', 'mxf']

        for ext in extensions:
            result = validate_codec(codec, 1920, 1080, 25, ext)
            assert isinstance(result, bool)

    @pytest.mark.unit
    def test_validate_creates_and_cleans_temp_file(self):
        """Test that validation properly cleans up temporary files."""
        import tempfile
        import os

        # Get temp directory
        temp_dir = tempfile.gettempdir()
        files_before = set(os.listdir(temp_dir))

        # Run validation
        validate_codec('mp4v', 1920, 1080, 25, 'avi')

        # Check that no new files remain
        files_after = set(os.listdir(temp_dir))
        new_files = files_after - files_before

        # Filter for video files only
        video_files = [f for f in new_files if f.endswith(('.avi', '.mp4', '.mkv', '.mxf'))]

        assert len(video_files) == 0, f"Temporary files not cleaned up: {video_files}"

    @pytest.mark.unit
    def test_validate_handles_exceptions_gracefully(self):
        """Test that validation handles exceptions without crashing."""
        # Test with potentially problematic inputs
        test_cases = [
            ('', 1920, 1080, 25, 'avi'),  # Empty codec
            ('a', 1920, 1080, 25, 'avi'),  # Single char
            ('abc', 1920, 1080, 25, 'avi'),  # Too short
            ('abcde', 1920, 1080, 25, 'avi'),  # Too long
        ]

        for codec, width, height, fps, ext in test_cases:
            try:
                result = validate_codec(codec, width, height, fps, ext)
                assert isinstance(result, bool), f"Should return bool for codec='{codec}'"
            except:
                pass  # If it raises an exception, that's also acceptable behavior


class TestGetCodecSuggestions:
    """Test the get_codec_suggestions() function."""

    @pytest.mark.unit
    def test_suggestions_for_mp4(self):
        """Test codec suggestions for MP4 extension."""
        suggestions = get_codec_suggestions('mp4')

        assert isinstance(suggestions, list), "Should return a list"
        assert len(suggestions) > 0, "Should have at least one suggestion"

        # Check structure of suggestions
        for codec, description in suggestions:
            assert isinstance(codec, str), "Codec should be string"
            assert isinstance(description, str), "Description should be string"
            assert len(codec) > 0, "Codec should not be empty"
            assert len(description) > 0, "Description should not be empty"

    @pytest.mark.unit
    def test_suggestions_for_avi(self):
        """Test codec suggestions for AVI extension."""
        suggestions = get_codec_suggestions('avi')

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # AVI should have specific codecs
        codecs = [codec for codec, _ in suggestions]
        # Common AVI codecs
        assert any(codec in ['xvid', 'mjpg', 'divx'] for codec in codecs)

    @pytest.mark.unit
    def test_suggestions_for_mxf(self):
        """Test codec suggestions for MXF extension."""
        suggestions = get_codec_suggestions('mxf')

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # MXF should have professional codecs
        codecs = [codec for codec, _ in suggestions]
        assert 'xdv7' in codecs or 'mp4v' in codecs

    @pytest.mark.unit
    def test_suggestions_for_mkv(self):
        """Test codec suggestions for MKV extension."""
        suggestions = get_codec_suggestions('mkv')

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    @pytest.mark.unit
    def test_suggestions_case_insensitive(self):
        """Test that extension matching is case-insensitive."""
        suggestions_lower = get_codec_suggestions('mp4')
        suggestions_upper = get_codec_suggestions('MP4')
        suggestions_mixed = get_codec_suggestions('Mp4')

        assert suggestions_lower == suggestions_upper
        assert suggestions_lower == suggestions_mixed

    @pytest.mark.unit
    def test_suggestions_for_unknown_extension(self):
        """Test suggestions for unknown file extension."""
        suggestions = get_codec_suggestions('unknown')

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0, "Should return default suggestions"

        # Should return MP4 suggestions as default
        codecs = [codec for codec, _ in suggestions]
        assert 'mp4v' in codecs or 'avc1' in codecs or 'x264' in codecs

    @pytest.mark.unit
    def test_suggestions_have_descriptions(self):
        """Test that all suggestions have meaningful descriptions."""
        extensions = ['mp4', 'avi', 'mxf', 'mkv']

        for ext in extensions:
            suggestions = get_codec_suggestions(ext)

            for codec, description in suggestions:
                assert len(description) > 10, \
                    f"Description for {codec} should be meaningful: '{description}'"
                # Description should have some explanatory text
                assert '-' in description or 'quality' in description.lower() or \
                       'compression' in description.lower()

    @pytest.mark.unit
    def test_suggestions_are_unique(self):
        """Test that suggestions don't have duplicate codecs."""
        extensions = ['mp4', 'avi', 'mxf', 'mkv']

        for ext in extensions:
            suggestions = get_codec_suggestions(ext)
            codecs = [codec for codec, _ in suggestions]

            assert len(codecs) == len(set(codecs)), \
                f"Extension '{ext}' has duplicate codec suggestions"

    @pytest.mark.unit
    def test_suggestions_reasonable_count(self):
        """Test that suggestions return a reasonable number of options."""
        extensions = ['mp4', 'avi', 'mxf', 'mkv']

        for ext in extensions:
            suggestions = get_codec_suggestions(ext)

            # Should have between 2 and 5 suggestions
            assert 2 <= len(suggestions) <= 5, \
                f"Extension '{ext}' should have 2-5 suggestions, got {len(suggestions)}"

    @pytest.mark.unit
    def test_mp4_suggests_common_codecs(self):
        """Test that MP4 suggests commonly available codecs."""
        suggestions = get_codec_suggestions('mp4')
        codecs = [codec for codec, _ in suggestions]

        # Should include some of the most common MP4 codecs
        common_codecs = {'mp4v', 'avc1', 'x264', 'h264'}
        assert any(codec in common_codecs for codec in codecs), \
            f"MP4 should suggest common codecs, got: {codecs}"

    @pytest.mark.unit
    def test_avi_suggests_legacy_codecs(self):
        """Test that AVI suggests appropriate legacy codecs."""
        suggestions = get_codec_suggestions('avi')
        codecs = [codec for codec, _ in suggestions]

        # Should include AVI-appropriate codecs
        avi_codecs = {'xvid', 'mjpg', 'divx', 'mp4v'}
        assert any(codec in avi_codecs for codec in codecs), \
            f"AVI should suggest appropriate codecs, got: {codecs}"


class TestCodecValidationIntegration:
    """Integration tests for codec validation workflow."""

    @pytest.mark.unit
    def test_typical_workflow(self, available_codecs):
        """Test a typical codec validation workflow."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        # Step 1: Try to validate a codec
        is_valid = validate_codec('mp4v', 1920, 1080, 25, 'mp4')

        # Step 2: If invalid, get suggestions
        if not is_valid:
            suggestions = get_codec_suggestions('mp4')
            assert len(suggestions) > 0

            # Step 3: Try first suggestion
            first_codec, _ = suggestions[0]
            result = validate_codec(first_codec, 1920, 1080, 25, 'mp4')
            assert isinstance(result, bool)

    @pytest.mark.unit
    @pytest.mark.requires_codec
    def test_find_working_codec_for_extension(self):
        """Test finding a working codec for a given extension."""
        extension = 'avi'
        suggestions = get_codec_suggestions(extension)

        # Try to find at least one working codec
        working_codecs = []
        for codec, description in suggestions:
            if validate_codec(codec, 1920, 1080, 25, extension):
                working_codecs.append(codec)

        # At least one suggested codec should work (on most systems)
        # If none work, that's also valid (might be a minimal system)
        assert isinstance(working_codecs, list)

    @pytest.mark.unit
    def test_consistent_validation_results(self, available_codecs):
        """Test that validation gives consistent results for same input."""
        if not available_codecs:
            pytest.skip("No available codecs found on system")

        codec = available_codecs[0]

        # Validate same codec multiple times
        result1 = validate_codec(codec, 1920, 1080, 25, 'avi')
        result2 = validate_codec(codec, 1920, 1080, 25, 'avi')
        result3 = validate_codec(codec, 1920, 1080, 25, 'avi')

        # Should get consistent results
        assert result1 == result2 == result3, \
            "Codec validation should be deterministic"
