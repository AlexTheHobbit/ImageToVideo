"""
Shared pytest fixtures for Image to Video Converter tests.

This module provides fixtures for:
- Test images (various aspect ratios and sizes)
- Temporary directories for test output
- Mock video codecs
- Common test data and constants
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Tuple

import pytest
import numpy as np
import cv2


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test output.

    Automatically cleaned up after the test completes.

    Yields:
        Path: Path to temporary directory
    """
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_image_wide(temp_dir) -> Path:
    """
    Create a wide (landscape) test image - 1920x1080.

    Returns:
        Path: Path to created test image
    """
    img = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    # Add some visual content - gradient for better testing
    for i in range(1080):
        img[i, :] = [i * 255 // 1080, 128, 255 - (i * 255 // 1080)]

    img_path = temp_dir / "test_wide.jpg"
    cv2.imwrite(str(img_path), img)
    return img_path


@pytest.fixture
def sample_image_narrow(temp_dir) -> Path:
    """
    Create a narrow (portrait) test image - 1080x1920.

    Returns:
        Path: Path to created test image
    """
    img = np.random.randint(0, 255, (1920, 1080, 3), dtype=np.uint8)
    # Add some visual content - vertical gradient
    for i in range(1920):
        img[i, :] = [255 - (i * 255 // 1920), 128, i * 255 // 1920]

    img_path = temp_dir / "test_narrow.jpg"
    cv2.imwrite(str(img_path), img)
    return img_path


@pytest.fixture
def sample_image_square(temp_dir) -> Path:
    """
    Create a square test image - 1080x1080.

    Returns:
        Path: Path to created test image
    """
    img = np.random.randint(0, 255, (1080, 1080, 3), dtype=np.uint8)
    # Add checkerboard pattern
    for i in range(0, 1080, 100):
        for j in range(0, 1080, 100):
            if (i // 100 + j // 100) % 2 == 0:
                img[i:i+100, j:j+100] = [255, 255, 255]
            else:
                img[i:i+100, j:j+100] = [0, 0, 0]

    img_path = temp_dir / "test_square.jpg"
    cv2.imwrite(str(img_path), img)
    return img_path


@pytest.fixture
def sample_image_small(temp_dir) -> Path:
    """
    Create a small test image - 320x240.

    Tests upscaling behavior.

    Returns:
        Path: Path to created test image
    """
    img = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
    img[:] = [100, 150, 200]  # Solid color for predictability

    img_path = temp_dir / "test_small.jpg"
    cv2.imwrite(str(img_path), img)
    return img_path


@pytest.fixture
def sample_image_large(temp_dir) -> Path:
    """
    Create a large test image - 3840x2160 (4K).

    Tests downscaling behavior.

    Returns:
        Path: Path to created test image
    """
    img = np.random.randint(0, 255, (2160, 3840, 3), dtype=np.uint8)
    # Add diagonal gradient
    for i in range(2160):
        for j in range(3840):
            intensity = int(((i + j) / (2160 + 3840)) * 255)
            img[i, j] = [intensity, intensity // 2, 255 - intensity]

    img_path = temp_dir / "test_large.jpg"
    cv2.imwrite(str(img_path), img)
    return img_path


@pytest.fixture
def sample_processed_image() -> np.ndarray:
    """
    Create a pre-processed image array (simulating scaleAndBlur output).

    Returns:
        np.ndarray: 1920x1080 BGR image array
    """
    img = np.zeros((1080, 1920, 3), dtype=np.uint8)
    # Create gradient pattern
    for i in range(1080):
        img[i, :] = [i * 255 // 1080, 128, 255 - (i * 255 // 1080)]
    return img


@pytest.fixture
def standard_video_params() -> dict:
    """
    Standard video parameters for testing.

    Returns:
        dict: Common video parameters
    """
    return {
        'width': 1920,
        'height': 1080,
        'fps': 25,
        'duration': 10,
        'zoom_rate': 0.0004,
        'blur': 195,
    }


@pytest.fixture
def available_codecs() -> list:
    """
    Get list of available video codecs on the system.

    Returns:
        list: List of codec fourcc codes that work on this system
    """
    import sys
    import io

    # Test common codecs
    test_codecs = ['mp4v', 'xvid', 'mjpg', 'avc1', 'x264']
    available = []

    for codec in test_codecs:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec)

            # Suppress stderr during test
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()

            with tempfile.NamedTemporaryFile(suffix='.avi', delete=False) as tmp:
                tmp_path = tmp.name

            writer = cv2.VideoWriter(tmp_path, fourcc, 25, (640, 480))
            if writer.isOpened():
                test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                writer.write(test_frame)
                writer.release()

                if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 100:
                    available.append(codec)

                os.remove(tmp_path)

            sys.stderr = old_stderr
        except:
            pass

    return available if available else ['mp4v']  # Fallback to mp4v


@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path: Path to project root
    """
    return Path(__file__).parent.parent


@pytest.fixture
def imgToVideo_script(project_root) -> Path:
    """
    Get path to the main imgToVideo.py script.

    Returns:
        Path: Path to imgToVideo.py
    """
    return project_root / "imgToVideo.py"
