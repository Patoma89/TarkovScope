"""
Tests unitarios para el módulo de actualización (core/updater.py).
"""
import unittest
from unittest.mock import MagicMock, patch

from core.updater import (
    build_clean_subprocess_env,
    check_github_release,
    is_newer_version,
    launch_installer,
    parse_version,
)


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

    def test_build_clean_subprocess_env_strips_pyinstaller_vars(self):
        dirty_env = {
            "PATH": r"C:\Windows\System32",
            "SYSTEMROOT": r"C:\Windows",
            "_PYI_APPLICATION_HOME_DIR": r"C:\Users\patom\AppData\Local\Temp\_MEI12345",
            "_PYI_ARCHIVE_FILE": r"C:\Users\patom\AppData\Local\TTC\TTC.exe",
            "_PYI_PARENT_PROCESS_LEVEL": "1",
            "_PYI_SPLASH_IPC": "1234",
            "_MEIPASS2": r"C:\Users\patom\AppData\Local\Temp\_MEI12345",
            "TCL_LIBRARY": r"C:\Users\patom\AppData\Local\Temp\_MEI12345\tcl",
            "TK_LIBRARY": r"C:\Python\tcl\tk8.6",
        }
        cleaned = build_clean_subprocess_env(dirty_env)
        self.assertEqual(cleaned["PATH"], r"C:\Windows\System32")
        self.assertEqual(cleaned["SYSTEMROOT"], r"C:\Windows")
        self.assertEqual(cleaned["TK_LIBRARY"], r"C:\Python\tcl\tk8.6")
        for key in (
            "_PYI_APPLICATION_HOME_DIR",
            "_PYI_ARCHIVE_FILE",
            "_PYI_PARENT_PROCESS_LEVEL",
            "_PYI_SPLASH_IPC",
            "_MEIPASS2",
            "TCL_LIBRARY",
        ):
            self.assertNotIn(key, cleaned)

    @patch("core.updater.subprocess.Popen")
    def test_launch_installer_uses_clean_env(self, mock_popen):
        with patch.dict(
            "os.environ",
            {
                "_PYI_APPLICATION_HOME_DIR": r"C:\Temp\_MEI9999",
                "_PYI_PARENT_PROCESS_LEVEL": "1",
            },
            clear=False,
        ):
            launch_installer(r"C:\Temp\TTC_Setup_v1.3.1.exe")

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], [r"C:\Temp\TTC_Setup_v1.3.1.exe"])
        self.assertTrue(kwargs["close_fds"])
        self.assertNotIn("_PYI_APPLICATION_HOME_DIR", kwargs["env"])
        self.assertNotIn("_PYI_PARENT_PROCESS_LEVEL", kwargs["env"])


if __name__ == "__main__":
    unittest.main()
