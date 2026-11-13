"""
Tests unitarios para el módulo de actualización (core/updater.py).
"""
import unittest
from unittest.mock import MagicMock, patch

from core.updater import check_github_release, is_newer_version, parse_version


class TestUpdater(unittest.TestCase):
    def test_parse_version_variants(self):
        self.assertEqual(parse_version("v1.1"), (1, 1, 0))
        self.assertEqual(parse_version("V.1.1"), (1, 1, 0))
        self.assertEqual(parse_version("1.1.0"), (1, 1, 0))
        self.assertEqual(parse_version("v2.0.1"), (2, 0, 1))
        self.assertEqual(parse_version(""), (0, 0, 0))

    def test_is_newer_version(self):
        self.assertTrue(is_newer_version("v1.2.0", "1.1.0"))
        self.assertTrue(is_newer_version("V.1.1.1", "1.1.0"))
        self.assertFalse(is_newer_version("v1.1", "1.1.0"))
        self.assertFalse(is_newer_version("v1.0.9", "1.1.0"))

    @patch("core.updater.requests.get")
    def test_check_github_release_finds_update_and_installer(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "tag_name": "v1.2.0",
            "html_url": "https://github.com/Patoma89/TarkovScope/releases/tag/v1.2.0",
            "body": "Mejoras de rendimiento",
            "assets": [
                {
                    "name": "TTC_Setup_v1.2.exe",
                    "browser_download_url": "https://example.com/TTC_Setup_v1.2.exe",
                }
            ],
        }
        mock_get.return_value = mock_resp

        res = check_github_release(repo="Patoma89/TarkovScope", current_version="1.1.0")
        self.assertTrue(res["ok"])
        self.assertTrue(res["has_update"])
        self.assertEqual(res["latest_version"], "v1.2.0")
        self.assertEqual(res["installer_name"], "TTC_Setup_v1.2.exe")

    @patch("core.updater.requests.get")
    def test_check_github_release_handles_404_gracefully(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        res = check_github_release(repo="Patoma89/TarkovScope", current_version="1.1.0")
        self.assertTrue(res["ok"])
        self.assertFalse(res["has_update"])


if __name__ == "__main__":
    unittest.main()
