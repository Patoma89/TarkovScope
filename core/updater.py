"""
TarkovScope - Módulo de Verificación y Actualización desde GitHub Releases / Git
Lógica pura sin dependencias de UI (100% testeable).
"""
import os
import re
import subprocess
import tempfile
from typing import Any, Callable, Dict, Optional, Tuple
import requests

from core.config import APP_VERSION, GITHUB_REPO


def parse_version(tag: str) -> Tuple[int, ...]:
    """Convierte una etiqueta de versión (ej: 'v1.1', 'V.1.1.0', '2.0.1') en tupla comparable."""
    cleaned = re.sub(r"^[vV]\.?\s*", "", (tag or "").strip())
    nums = [int(p) for p in re.findall(r"\d+", cleaned)]
    if not nums:
        return (0, 0, 0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])


def is_newer_version(remote_tag: str, current_version: str = APP_VERSION) -> bool:
    """Devuelve True si remote_tag es estrictamente mayor que current_version."""
    return parse_version(remote_tag) > parse_version(current_version)


def check_github_release(
    repo: str = GITHUB_REPO,
    current_version: str = APP_VERSION,
    timeout: float = 8.0,
) -> Dict[str, Any]:
    """Consulta la última Release publicada en GitHub para verificar si hay una nueva versión."""
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    releases_page = f"https://github.com/{repo}/releases"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "TTC-TacticalTarkovCompanion-Updater",
    }

    try:
        resp = requests.get(api_url, headers=headers, timeout=timeout)
        if resp.status_code == 404:
            return {
                "ok": True,
                "has_update": False,
                "current_version": current_version,
                "latest_version": current_version,
                "release_url": releases_page,
                "installer_url": None,
                "installer_name": None,
                "notes": "No hay releases publicadas todavía en GitHub.",
            }
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "current_version": current_version,
            "release_url": releases_page,
        }

    tag_name = str(payload.get("tag_name") or "").strip()
    html_url = str(payload.get("html_url") or releases_page)
    notes = str(payload.get("body") or "").strip()

    installer_url: Optional[str] = None
    installer_name: Optional[str] = None
    for asset in payload.get("assets") or []:
        name = str(asset.get("name") or "")
        dl_url = str(asset.get("browser_download_url") or "")
        if name.lower().endswith(".exe") and dl_url:
            installer_url = dl_url
            installer_name = name
            break

    return {
        "ok": True,
        "has_update": is_newer_version(tag_name, current_version),
        "current_version": current_version,
        "latest_version": tag_name or current_version,
        "release_url": html_url,
        "installer_url": installer_url,
        "installer_name": installer_name,
        "notes": notes,
    }


def download_installer(
    url: str,
    filename: str = "TTC_Setup.exe",
    progress_cb: Optional[Callable[[int], None]] = None,
    timeout: float = 60.0,
) -> str:
    """Descarga el instalador .exe a una carpeta temporal y devuelve su ruta local."""
    safe_name = os.path.basename(filename) or "TTC_Setup.exe"
    dest_path = os.path.join(tempfile.gettempdir(), safe_name)

    with requests.get(url, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length") or 0)
        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if progress_cb and total > 0:
                    pct = min(100, int((downloaded * 100) / total))
                    progress_cb(pct)

    return dest_path


def run_git_fast_forward_pull(repo_dir: str) -> Tuple[bool, str]:
    """Ejecuta 'git pull --ff-only' en el directorio del repositorio local."""
    try:
        proc = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=25,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if proc.returncode == 0:
            return True, out or "Repositorio actualizado correctamente."
        return False, err or out or "No se pudo actualizar con git pull."
    except Exception as exc:
        return False, str(exc)
