"""
TarkovScope - Módulo de Verificación y Actualización desde GitHub Releases / Git
Lógica pura sin dependencias de UI (100% testeable).
"""
import os
import re
import subprocess
import tempfile
from typing import Any, Callable, Dict, Mapping, Optional, Tuple
import requests

from core.config import APP_VERSION, GITHUB_REPO

_PYI_ENV_PREFIXES = ("_PYI_", "_MEIPASS")
_PYI_TEMP_PATH_VARS = ("TCL_LIBRARY", "TK_LIBRARY")


def build_clean_subprocess_env(
    base_env: Optional[Mapping[str, str]] = None,
) -> Dict[str, str]:
    """Devuelve una copia de las variables de entorno sin rastros del bootloader PyInstaller.

    Evita que procesos hijos (p. ej. el instalador de actualizaciones) hereden
    `_PYI_APPLICATION_HOME_DIR` o `_MEIPASS2`, lo que provoca fallos de validación
    en el bootloader `--onefile` de PyInstaller >= 6.22.1 al relanzar la app.
    """
    source = os.environ if base_env is None else base_env
    cleaned: Dict[str, str] = {}
    for key, val in source.items():
        upper_key = key.upper()
        if upper_key.startswith(_PYI_ENV_PREFIXES):
            continue
        if upper_key in _PYI_TEMP_PATH_VARS and "_MEI" in str(val).upper():
            continue
        cleaned[key] = val
    return cleaned


def launch_installer(exe_path: str) -> subprocess.Popen:
    """Inicia el instalador descargado con un entorno limpio de variables PyInstaller."""
    return subprocess.Popen(
        [exe_path],
        close_fds=True,
        env=build_clean_subprocess_env(),
    )


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


def _check_github_release_web_fallback(
    repo: str,
    current_version: str,
    timeout: float,
) -> Optional[Dict[str, Any]]:
    """Fallback sin rate-limit vía redirección web de github.com/<repo>/releases/latest."""
    latest_web_url = f"https://github.com/{repo}/releases/latest"
    headers = {"User-Agent": "TTC-TacticalTarkovCompanion-Updater"}
    try:
        resp = requests.get(latest_web_url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        final_url = str(resp.url or "")
        match = re.search(r"/releases/tag/([^/?#]+)", final_url)
        if not match:
            return None
        tag_name = match.group(1).strip()
        clean_tag = tag_name if tag_name.lower().startswith("v") else f"v{tag_name}"
        installer_name = f"TTC_Setup_{clean_tag}.exe"
        installer_url = f"https://github.com/{repo}/releases/download/{tag_name}/{installer_name}"
        return {
            "ok": True,
            "has_update": is_newer_version(tag_name, current_version),
            "current_version": current_version,
            "latest_version": tag_name,
            "release_url": final_url,
            "installer_url": installer_url,
            "installer_name": installer_name,
            "notes": f"Verificado vía web directa de GitHub (Release {tag_name}).",
        }
    except Exception:
        return None


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
        if resp.status_code in (403, 429):
            fb = _check_github_release_web_fallback(repo, current_version, timeout)
            if fb is not None:
                return fb
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        fb = _check_github_release_web_fallback(repo, current_version, timeout)
        if fb is not None:
            return fb
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
    fallback_url: Optional[str] = None
    fallback_name: Optional[str] = None
    for asset in payload.get("assets") or []:
        name = str(asset.get("name") or "")
        dl_url = str(asset.get("browser_download_url") or "")
        low = name.lower()
        if low.endswith(".exe") and dl_url:
            if "setup" in low or "installer" in low:
                installer_url = dl_url
                installer_name = name
                break
            if fallback_url is None:
                fallback_url = dl_url
                fallback_name = name
    if installer_url is None:
        installer_url = fallback_url
        installer_name = fallback_name

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
