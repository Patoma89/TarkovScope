"""
TarkovScope - Atajo Global Nativo de Windows (Win32 RegisterHotKey)
Permite mostrar, restaurar u ocultar la ventana desde cualquier juego o monitor
sin dependencias externas (usa únicamente ctypes + user32/kernel32).
"""
import ctypes
import logging
import sys
import threading
from ctypes import wintypes
from typing import Callable, Optional, Tuple

logger = logging.getLogger("TarkovScope.GlobalHotkey")

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

_MOD_ALIASES = {
    "alt": MOD_ALT,
    "ctrl": MOD_CONTROL,
    "control": MOD_CONTROL,
    "shift": MOD_SHIFT,
    "win": MOD_WIN,
    "super": MOD_WIN,
}

_FUNCTION_KEYS = {f"F{n}": 0x6F + n for n in range(1, 13)}


def parse_hotkey_spec(spec: str) -> Tuple[int, int]:
    """Convierte una cadena como 'Ctrl+Alt+T' en (modifiers, virtual_key_code)."""
    parts = [p.strip() for p in str(spec or "").split("+") if p.strip()]
    if not parts:
        raise ValueError("Especificación de atajo vacía")

    modifiers = 0
    vk_code: Optional[int] = None

    for token in parts:
        low = token.lower()
        if low in _MOD_ALIASES:
            modifiers |= _MOD_ALIASES[low]
            continue

        if vk_code is not None:
            raise ValueError(f"Múltiples teclas principales en atajo: {spec!r}")

        up = token.upper()
        if up in _FUNCTION_KEYS:
            vk_code = _FUNCTION_KEYS[up]
        elif len(up) == 1 and ("A" <= up <= "Z" or "0" <= up <= "9"):
            vk_code = ord(up)
        else:
            raise ValueError(f"Tecla no soportada en atajo: {token!r}")

    if vk_code is None:
        raise ValueError(f"Falta tecla principal en atajo: {spec!r}")

    if modifiers:
        modifiers |= MOD_NOREPEAT

    return modifiers, vk_code


class WindowsGlobalHotkey:
    """Registra un atajo global en Windows dentro de un hilo demonio dedicado."""

    def __init__(self, hotkey_spec: str, callback: Callable[[], None], hotkey_id: int = 1) -> None:
        self.hotkey_spec = hotkey_spec
        self.modifiers, self.vk_code = parse_hotkey_spec(hotkey_spec)
        self.callback = callback
        self.hotkey_id = int(hotkey_id)
        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._ready_event = threading.Event()
        self._registered = False

    def start(self) -> bool:
        """Inicia el listener Win32. Retorna False de forma segura si no aplica o está ocupado."""
        if not sys.platform.startswith("win"):
            return False
        if self._thread is not None and self._thread.is_alive():
            return self._registered

        self._ready_event.clear()
        self._registered = False
        self._thread = threading.Thread(target=self._run_loop, name="TTCGlobalHotkey", daemon=True)
        self._thread.start()
        self._ready_event.wait(timeout=2.0)
        return self._registered

    def _run_loop(self) -> None:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
        user32.RegisterHotKey.restype = wintypes.BOOL
        user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.UnregisterHotKey.restype = wintypes.BOOL
        user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
        user32.GetMessageW.restype = ctypes.c_int
        kernel32.GetCurrentThreadId.restype = wintypes.DWORD

        self._thread_id = int(kernel32.GetCurrentThreadId())
        try:
            ok = bool(user32.RegisterHotKey(None, self.hotkey_id, self.modifiers, self.vk_code))
        except Exception as exc:
            logger.warning("Error registrando atajo global %s: %s", self.hotkey_spec, exc)
            self._ready_event.set()
            return

        if not ok:
            logger.warning("No se pudo registrar el atajo global %s (puede estar en uso).", self.hotkey_spec)
            self._ready_event.set()
            return

        self._registered = True
        self._ready_event.set()

        msg = wintypes.MSG()
        try:
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                    try:
                        self.callback()
                    except Exception as exc:
                        logger.warning("Error en callback de atajo global %s: %s", self.hotkey_spec, exc)
        finally:
            try:
                user32.UnregisterHotKey(None, self.hotkey_id)
            except Exception:
                pass
            self._registered = False

    def stop(self) -> None:
        """Detiene el loop de mensajes Win32 y libera el atajo global."""
        if not sys.platform.startswith("win"):
            return
        thread = self._thread
        tid = self._thread_id
        if thread is not None and thread.is_alive() and tid:
            try:
                user32 = ctypes.windll.user32
                user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
                user32.PostThreadMessageW.restype = wintypes.BOOL
                user32.PostThreadMessageW(tid, WM_QUIT, 0, 0)
            except Exception:
                pass
            thread.join(timeout=1.5)
        self._thread = None
        self._thread_id = None
        self._registered = False
