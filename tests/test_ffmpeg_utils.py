"""
Tests for FFmpeg Detection & Download Service

Tests cover:
- Platform detection
- Binary path resolution
- FFmpeg verification
- Download logic
- Cache functionality
- Manual installation instructions
"""

import platform
from pathlib import Path
from unittest.mock import Mock, patch
from django.core.cache import cache
from django.test import TestCase

from samplify.utils.ffmpeg import (
    get_platform,
    get_bin_directory,
    get_expected_binary_path,
    verify_ffmpeg,
    download_ffmpeg,
    get_manual_install_instructions,
    get_ffmpeg_path,
    check_ffmpeg_available,
    CACHE_KEY,
    BINARY_NAMES,
    FFMPEG_URLS,
)


class TestPlatformDetection(TestCase):
    """Test OS platform detection"""

    def test_get_platform_returns_valid_os(self):
        """Test that get_platform returns a valid OS name"""
        platform_name = get_platform()
        self.assertIn(platform_name, ['Windows', 'Darwin', 'Linux'])

    def test_get_platform_matches_system(self):
        """Test that get_platform matches platform.system()"""
        self.assertEqual(get_platform(), platform.system())


class TestBinaryPathResolution(TestCase):
    """Test FFmpeg binary path resolution"""

    def test_get_bin_directory_structure(self):
        """Test bin directory structure is correct"""
        bin_dir = get_bin_directory()
        self.assertIsInstance(bin_dir, Path)
        self.assertTrue(str(bin_dir).endswith(get_platform()))

    def test_get_expected_binary_path_includes_platform(self):
        """Test expected binary path includes platform-specific directory"""
        expected_path = get_expected_binary_path()
        self.assertIsInstance(expected_path, Path)
        self.assertIn(get_platform(), str(expected_path))

    def test_get_expected_binary_path_has_correct_extension(self):
        """Test binary path has correct extension for platform"""
        expected_path = get_expected_binary_path()
        platform_name = get_platform()
        expected_name = BINARY_NAMES[platform_name]

        self.assertTrue(str(expected_path).endswith(expected_name))

    def test_binary_name_windows_has_exe_extension(self):
        """Test Windows binary name has .exe extension"""
        self.assertEqual(BINARY_NAMES['Windows'], 'ffmpeg.exe')

    def test_binary_name_unix_no_extension(self):
        """Test Unix-like systems have no extension"""
        self.assertEqual(BINARY_NAMES['Darwin'], 'ffmpeg')
        self.assertEqual(BINARY_NAMES['Linux'], 'ffmpeg')


class TestFFmpegVerification(TestCase):
    """Test FFmpeg binary verification"""

    @patch('subprocess.run')
    def test_verify_ffmpeg_success(self, mock_run):
        """Test successful FFmpeg verification"""
        mock_run.return_value = Mock(returncode=0, stdout="ffmpeg version", stderr="")

        test_path = Path('/fake/path/ffmpeg')
        result = verify_ffmpeg(test_path)

        self.assertTrue(result)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn('-version', args)

    @patch('subprocess.run')
    def test_verify_ffmpeg_failure(self, mock_run):
        """Test failed FFmpeg verification"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")

        test_path = Path('/fake/path/ffmpeg')
        result = verify_ffmpeg(test_path)

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_verify_ffmpeg_timeout(self, mock_run):
        """Test FFmpeg verification timeout handling"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='ffmpeg', timeout=10)

        test_path = Path('/fake/path/ffmpeg')
        result = verify_ffmpeg(test_path)

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_verify_ffmpeg_not_found(self, mock_run):
        """Test FFmpeg verification when binary not found"""
        mock_run.side_effect = FileNotFoundError()

        test_path = Path('/fake/path/ffmpeg')
        result = verify_ffmpeg(test_path)

        self.assertFalse(result)


class TestManualInstallInstructions(TestCase):
    """Test manual installation instructions"""

    def test_get_manual_install_instructions_returns_string(self):
        """Test that manual instructions return a string"""
        instructions = get_manual_install_instructions()
        self.assertIsInstance(instructions, str)
        self.assertGreater(len(instructions), 0)

    def test_manual_instructions_include_platform_specific_info(self):
        """Test instructions include platform-specific information"""
        instructions = get_manual_install_instructions()
        platform_name = get_platform()

        if platform_name == 'Windows':
            self.assertIn('ffmpeg.exe', instructions)
        elif platform_name == 'Darwin':
            self.assertIn('brew', instructions.lower())
        elif platform_name == 'Linux':
            self.assertIn('apt-get', instructions.lower())

    def test_manual_instructions_include_bin_directory(self):
        """Test instructions include bin directory path"""
        instructions = get_manual_install_instructions()
        bin_dir = get_bin_directory()
        self.assertIn(str(bin_dir), instructions)


class TestFFmpegDownload(TestCase):
    """Test FFmpeg download functionality"""

    def test_ffmpeg_urls_configured_for_all_platforms(self):
        """Test download URLs exist for all platforms"""
        self.assertIn('Windows', FFMPEG_URLS)
        self.assertIn('Darwin', FFMPEG_URLS)
        self.assertIn('Linux', FFMPEG_URLS)

    def test_ffmpeg_urls_are_valid_https(self):
        """Test all download URLs use HTTPS"""
        for platform_name, url in FFMPEG_URLS.items():
            self.assertTrue(url.startswith('https://'))

    @patch('samplify.utils.ffmpeg.get_platform')
    def test_download_ffmpeg_unsupported_platform(self, mock_platform):
        """Test download fails gracefully for unsupported platform"""
        mock_platform.return_value = 'UnknownOS'

        with patch.dict('samplify.utils.ffmpeg.FFMPEG_URLS', {}, clear=True):
            result = download_ffmpeg()
            self.assertFalse(result)


class TestFFmpegPathCaching(TestCase):
    """Test FFmpeg path caching functionality"""

    def setUp(self):
        """Clear cache before each test"""
        cache.clear()

    def tearDown(self):
        """Clear cache after each test"""
        cache.clear()

    @patch('samplify.utils.ffmpeg.verify_ffmpeg')
    @patch('pathlib.Path.exists')
    def test_get_ffmpeg_path_caches_result(self, mock_exists, mock_verify):
        """Test that successful path is cached"""
        mock_exists.return_value = True
        mock_verify.return_value = True

        # First call
        path1 = get_ffmpeg_path()
        self.assertIsNotNone(path1)

        # Verify cache was set
        cached_path = cache.get(CACHE_KEY)
        self.assertEqual(cached_path, path1)

    @patch('samplify.utils.ffmpeg.verify_ffmpeg')
    @patch('pathlib.Path.exists')
    def test_get_ffmpeg_path_uses_cache(self, mock_exists, mock_verify):
        """Test that cached path is used on subsequent calls"""
        test_path = '/fake/cached/path'
        cache.set(CACHE_KEY, test_path, 3600)

        with patch('pathlib.Path.exists', return_value=True):
            result = get_ffmpeg_path()
            self.assertEqual(result, test_path)

        # verify_ffmpeg should not be called when using cache
        mock_verify.assert_not_called()

    @patch('samplify.utils.ffmpeg.verify_ffmpeg')
    @patch('pathlib.Path.exists')
    def test_get_ffmpeg_path_force_refresh_bypasses_cache(self, mock_exists, mock_verify):
        """Test force_refresh bypasses cache"""
        cache.set(CACHE_KEY, '/old/path', 3600)
        mock_exists.return_value = True
        mock_verify.return_value = True

        get_ffmpeg_path(force_refresh=True)

        # Should have called verify, not used cache
        mock_verify.assert_called()


class TestCheckFFmpegAvailable(TestCase):
    """Test FFmpeg availability check"""

    @patch('samplify.utils.ffmpeg.get_ffmpeg_path')
    def test_check_ffmpeg_available_returns_true_when_found(self, mock_get_path):
        """Test returns True when FFmpeg is found"""
        mock_get_path.return_value = '/path/to/ffmpeg'

        result = check_ffmpeg_available()

        self.assertTrue(result)

    @patch('samplify.utils.ffmpeg.get_ffmpeg_path')
    def test_check_ffmpeg_available_returns_false_when_not_found(self, mock_get_path):
        """Test returns False when FFmpeg is not found"""
        mock_get_path.return_value = None

        result = check_ffmpeg_available()

        self.assertFalse(result)


class TestIntegration(TestCase):
    """Integration tests for FFmpeg service"""

    def setUp(self):
        """Clear cache before integration tests"""
        cache.clear()

    def tearDown(self):
        """Clear cache after integration tests"""
        cache.clear()

    @patch('samplify.utils.ffmpeg.download_ffmpeg')
    @patch('samplify.utils.ffmpeg.verify_ffmpeg')
    @patch('pathlib.Path.exists')
    def test_get_ffmpeg_path_downloads_if_not_exists(self, mock_exists, mock_verify, mock_download):
        """Test automatic download when FFmpeg not found"""
        # First check: doesn't exist
        # Second check (after download): exists
        mock_exists.side_effect = [False, True]
        mock_download.return_value = True
        mock_verify.return_value = True

        result = get_ffmpeg_path()

        self.assertIsNotNone(result)
        mock_download.assert_called_once()

    @patch('samplify.utils.ffmpeg.download_ffmpeg')
    @patch('samplify.utils.ffmpeg.verify_ffmpeg')
    @patch('pathlib.Path.exists')
    def test_get_ffmpeg_path_returns_none_if_download_fails(self, mock_exists, mock_verify, mock_download):
        """Test returns None if download fails"""
        mock_exists.return_value = False
        mock_download.return_value = False

        result = get_ffmpeg_path()

        self.assertIsNone(result)
        mock_download.assert_called_once()
