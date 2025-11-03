"""
Unit tests for configuration file loading functionality.

Tests cover:
- Simple KEY=VALUE format parsing
- YAML format parsing (if PyYAML available)
- Config file priority (current dir > home dir)
- Type conversion (int, float, bool, string)
- Comment and empty line handling
- CLI arguments overriding config values
- Error handling for malformed config files
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

# Import functions under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from imgToVideo import load_config_file


# ============================================================================
# Helper Functions
# ============================================================================

def create_config_file(path: Path, content: str):
    """Create a config file with given content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)


# ============================================================================
# Tests: Simple Format Parsing
# ============================================================================

@pytest.mark.unit
def test_load_simple_format_basic(temp_dir, monkeypatch):
    """Test loading a simple KEY=VALUE config file."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
width=1920
height=1080
fps=30
    """)

    # Change to temp directory so config is found
    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config['width'] == 1920
    assert config['height'] == 1080
    assert config['fps'] == 30


@pytest.mark.unit
def test_load_simple_format_with_comments(temp_dir, monkeypatch):
    """Test that comments are ignored in simple format."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
# This is a comment
width=1920
# Another comment
height=1080  # Inline comment (not supported, but won't break)
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config['width'] == 1920
    assert config['height'] == 1080


@pytest.mark.unit
def test_load_simple_format_with_empty_lines(temp_dir, monkeypatch):
    """Test that empty lines are ignored."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
width=1920

height=1080


fps=30
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config['width'] == 1920
    assert config['height'] == 1080
    assert config['fps'] == 30


@pytest.mark.unit
def test_load_simple_format_with_quotes(temp_dir, monkeypatch):
    """Test that quoted values are handled correctly."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
codec="mp4v"
extension='mp4'
input="./my photos"
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config['codec'] == 'mp4v'
    assert config['extension'] == 'mp4'
    assert config['input'] == './my photos'


# ============================================================================
# Tests: Type Conversion
# ============================================================================

@pytest.mark.unit
def test_type_conversion_integers(temp_dir, monkeypatch):
    """Test that integer values are converted correctly."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
width=1920
height=1080
fps=30
duration=10
blur=195
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert isinstance(config['width'], int)
    assert isinstance(config['height'], int)
    assert isinstance(config['fps'], int)
    assert config['width'] == 1920


@pytest.mark.unit
def test_type_conversion_floats(temp_dir, monkeypatch):
    """Test that float values are converted correctly."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
zoom=0.0004
other_float=3.14159
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert isinstance(config['zoom'], float)
    assert config['zoom'] == 0.0004
    assert config['other_float'] == 3.14159


@pytest.mark.unit
def test_type_conversion_booleans(temp_dir, monkeypatch):
    """Test that boolean values are converted correctly."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
verbose=true
quiet=false
force=yes
dry_run=no
stitch=on
another=off
numeric_true=1
numeric_false=0
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config['verbose'] is True
    assert config['quiet'] is False
    assert config['force'] is True
    assert config['dry_run'] is False
    assert config['stitch'] is True
    assert config['another'] is False
    assert config['numeric_true'] is True
    assert config['numeric_false'] is False


@pytest.mark.unit
def test_type_conversion_strings(temp_dir, monkeypatch):
    """Test that string values are preserved."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
codec=mp4v
extension=mp4
input=./images
output=./videos
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert isinstance(config['codec'], str)
    assert config['codec'] == 'mp4v'
    assert config['extension'] == 'mp4'


# ============================================================================
# Tests: YAML Format
# ============================================================================

@pytest.mark.unit
def test_load_yaml_format(temp_dir, monkeypatch):
    """Test loading YAML format config file."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")

    config_path = temp_dir / 'imgtovideorc.yaml'
    create_config_file(config_path, """
width: 1920
height: 1080
fps: 30
duration: 10
codec: mp4v
extension: mp4
verbose: true
quiet: false
zoom: 0.0004
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config['width'] == 1920
    assert config['height'] == 1080
    assert config['fps'] == 30
    assert config['codec'] == 'mp4v'
    assert config['verbose'] is True
    assert config['zoom'] == 0.0004


# ============================================================================
# Tests: Config File Priority
# ============================================================================

@pytest.mark.unit
def test_config_priority_current_dir_over_home(temp_dir, monkeypatch):
    """Test that current directory config takes priority over home directory."""
    # Create config in temp home
    home_config = temp_dir / 'home' / '.imgtovideorc'
    create_config_file(home_config, """
width=1920
height=1080
    """)

    # Create config in temp current dir
    current_config = temp_dir / 'current' / '.imgtovideorc'
    create_config_file(current_config, """
width=3840
height=2160
    """)

    # Mock home directory and change to current
    with patch('pathlib.Path.home', return_value=temp_dir / 'home'):
        monkeypatch.chdir(temp_dir / 'current')
        config = load_config_file()

    # Should use current directory values
    assert config['width'] == 3840
    assert config['height'] == 2160


@pytest.mark.unit
def test_config_priority_simple_over_yaml(temp_dir, monkeypatch):
    """Test that .imgtovideorc takes priority over imgtovideorc.yaml in same directory."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not installed")

    # Create simple format config
    simple_config = temp_dir / '.imgtovideorc'
    create_config_file(simple_config, """
width=3840
    """)

    # Create YAML format config
    yaml_config = temp_dir / 'imgtovideorc.yaml'
    create_config_file(yaml_config, """
width: 1920
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    # Should use simple format (higher priority)
    assert config['width'] == 3840


# ============================================================================
# Tests: Error Handling
# ============================================================================

@pytest.mark.unit
def test_no_config_file_returns_empty_dict(temp_dir, monkeypatch):
    """Test that missing config file returns empty dict."""
    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config == {}


@pytest.mark.unit
def test_malformed_simple_format_skips_bad_lines(temp_dir, monkeypatch):
    """Test that malformed lines are skipped."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
width=1920
this_is_not_valid
height=1080
also not valid here
fps=30
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config['width'] == 1920
    assert config['height'] == 1080
    assert config['fps'] == 30
    # Bad lines should be skipped
    assert 'this_is_not_valid' not in config


@pytest.mark.unit
def test_empty_config_file(temp_dir, monkeypatch):
    """Test that empty config file returns empty dict."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, "")

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config == {}


@pytest.mark.unit
def test_config_file_with_only_comments(temp_dir, monkeypatch):
    """Test config file with only comments."""
    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
# This is a comment
# Another comment
    # More comments
    """)

    monkeypatch.chdir(temp_dir)

    config = load_config_file()
    assert config == {}


# ============================================================================
# Tests: Integration with argparse
# ============================================================================

@pytest.mark.integration
def test_config_loaded_by_parse_arguments(temp_dir, monkeypatch):
    """Test that parse_arguments loads and applies config."""
    from imgToVideo import parse_arguments

    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
width=3840
height=2160
fps=60
codec=mp4v
    """)

    monkeypatch.chdir(temp_dir)

    # Mock sys.argv to prevent parsing actual command line
    with patch('sys.argv', ['imgToVideo.py']):
        args = parse_arguments()

    assert args.width == 3840
    assert args.height == 2160
    assert args.fps == 60
    assert args.codec == 'mp4v'


@pytest.mark.integration
def test_cli_args_override_config(temp_dir, monkeypatch):
    """Test that CLI arguments override config file values."""
    from imgToVideo import parse_arguments

    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
width=3840
height=2160
fps=60
    """)

    monkeypatch.chdir(temp_dir)

    # Pass CLI arguments that override config
    with patch('sys.argv', ['imgToVideo.py', '--width', '1920', '--fps', '30']):
        args = parse_arguments()

    # CLI should override config
    assert args.width == 1920
    assert args.fps == 30
    # Config value should still be used for height (not overridden)
    assert args.height == 2160


@pytest.mark.integration
def test_config_with_boolean_flags(temp_dir, monkeypatch):
    """Test that boolean flags from config are applied."""
    from imgToVideo import parse_arguments

    config_path = temp_dir / '.imgtovideorc'
    create_config_file(config_path, """
verbose=true
force=true
stitch=true
    """)

    monkeypatch.chdir(temp_dir)

    with patch('sys.argv', ['imgToVideo.py']):
        args = parse_arguments()

    assert args.verbose is True
    assert args.force is True
    assert args.stitch is True
    assert args.quiet is False  # Not in config, should be default False
