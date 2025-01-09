import pytest
import logging
import requests
from modules.insta_module_v3 import download_reel

@pytest.fixture
def logger():
    return logging.getLogger('test_logger')

def is_valid_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def test_download_reel_returns_valid_video_url(logger):
    # Arrange
    test_url = "https://www.instagram.com/reel/CsmIhVQqsur/"
    
    # Act
    video_url = download_reel(test_url, logger)
    
    # Assert
    assert video_url is not None
    assert isinstance(video_url, str)
    assert video_url.startswith('https://')
    assert is_valid_url(video_url), "The returned URL is not accessible"

def test_download_reel_with_invalid_url(logger):
    # Arrange
    invalid_url = "https://instagram.com/invalid"
    
    # Act
    result = download_reel(invalid_url, logger)
    
    # Assert
    assert result is None

def test_download_reel_with_nonexistent_reel(logger):
    # Arrange
    nonexistent_url = "https://www.instagram.com/reel/nonexistentreel/"
    
    # Act
    result = download_reel(nonexistent_url, logger)
    
    # Assert
    assert result is None 