"""
Pruebas unitarias de core/sync_service.py con red simulada (sin tráfico real).
"""
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import insert_ammunition_batch
from core.sync_service import SyncService


class _Resp:
    def __init__(self, status=200, payload=None):
        self.status_code = status
        self._payload = payload if payload is not None else {}

    def json(self):
        return self._payload


class TestSyncService(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        self.db = tmp.name
        self.events = []

    def tearDown(self):
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(self.db + suffix)
            except OSError:
                pass

    def _cb(self, pct, msg):
        self.events.append((pct, msg))

    @mock.patch("core.sync_service.get_datastore")
    @mock.patch("core.sync_service.prebake_all_assets")
    @mock.patch("core.sync_service.requests.get", side_effect=ConnectionError("sin red"))
    @mock.patch("core.sync_service.requests.post", side_effect=ConnectionError("sin red"))
    def test_offline_with_empty_db_reports_failure(self, _post, _get, _prebake, _ds):
        service = SyncService(self.db)
        with mock.patch("core.sync_service.is_db_populated", return_value=False):
            ok = service.sync_all(self._cb)
        self.assertFalse(ok)
        self.assertEqual(self.events[-1][0], 0)
        self.assertIn("Error de conexión", self.events[-1][1])

    @mock.patch("core.sync_service.get_datastore")
    @mock.patch("core.sync_service.prebake_all_assets")
    @mock.patch("core.sync_service.requests.get", side_effect=ConnectionError("sin red"))
    @mock.patch("core.sync_service.requests.post", side_effect=ConnectionError("sin red"))
    def test_offline_with_populated_db_falls_back_to_local(self, _post, _get, _prebake, ds):
        service = SyncService(self.db)
        with mock.patch("core.sync_service.is_db_populated", return_value=True):
            ok = service.sync_all(self._cb)
        self.assertTrue(ok)
        self.assertEqual(self.events[-1][0], 100)
        self.assertIn("sin conexión", self.events[-1][1])
        ds.return_value.refresh.assert_called()

    @mock.patch("core.sync_service.get_datastore")
    @mock.patch("core.sync_service.prebake_all_assets")
    @mock.patch("core.sync_service.requests.get", return_value=_Resp(404))
    @mock.patch("core.sync_service.requests.post", return_value=_Resp(500))
    def test_http_errors_use_seeded_fallback_and_complete(self, _post, _get, prebake, ds):
        service = SyncService(self.db)
        ok = service.sync_all(self._cb)
        self.assertTrue(ok)
        percentages = [p for p, _ in self.events]
        self.assertEqual(percentages, sorted(percentages), "el progreso debe ser monótono")
        self.assertEqual(percentages[-1], 100)
        prebake.assert_called_once()
        ds.return_value.refresh.assert_called()

    @mock.patch("core.sync_service.get_datastore")
    @mock.patch("core.sync_service.prebake_all_assets")
    @mock.patch("core.sync_service.requests.get", return_value=_Resp(404))
    @mock.patch("core.sync_service.requests.post", return_value=_Resp(500))
    def test_callback_is_optional(self, _post, _get, _prebake, _ds):
        self.assertTrue(SyncService(self.db).sync_all())


if __name__ == "__main__":
    unittest.main()
