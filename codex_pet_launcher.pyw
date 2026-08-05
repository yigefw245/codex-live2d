import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYW_PATH = os.path.join(BASE_DIR, ".venv", "Scripts", "pythonw.exe")
MAIN_PATH = os.path.join(BASE_DIR, "main.py")
PID_FILE = os.path.join(BASE_DIR, "pet.pid")
WATCHER_PID_FILE = os.path.join(BASE_DIR, "watcher.pid")
SHUTDOWN_FLAG = os.path.join(BASE_DIR, "pet_shutdown.flag")
DISABLED_FLAG = os.path.join(BASE_DIR, "pet_disabled.flag")
POLL_SECONDS = 3
HOST_NAMES = {"chatgpt.exe", "codex.exe"}

TH32CS_SNAPPROCESS = 0x00000002
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_TERMINATE = 0x0001

kernel32 = ctypes.windll.kernel32


class ProcessEntry32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_wchar * 260),
    ]


def process_names():
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == wintypes.HANDLE(-1).value:
        return []
    names = []
    entry = ProcessEntry32W()
    entry.dwSize = ctypes.sizeof(ProcessEntry32W)
    ok = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
    while ok:
        names.append(entry.szExeFile.lower())
        ok = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    kernel32.CloseHandle(snapshot)
    return names


def pid_alive(pid):
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False
    kernel32.CloseHandle(handle)
    return True


def pet_pid():
    try:
        with open(PID_FILE, encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return None


def pet_running():
    pid = pet_pid()
    return pid is not None and pid_alive(pid)


def launch_pet():
    subprocess.Popen(
        [PYW_PATH, MAIN_PATH],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def terminate_pid(pid):
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    kernel32.TerminateProcess.restype = wintypes.BOOL
    kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if handle:
        kernel32.TerminateProcess(handle, 0)
        kernel32.CloseHandle(handle)


def close_pet():
    if not pet_running():
        return True
    try:
        with open(SHUTDOWN_FLAG, "w", encoding="utf-8") as f:
            f.write("1")
    except OSError:
        pass
    deadline = time.time() + 6
    while time.time() < deadline:
        if not pet_running():
            return True
        time.sleep(0.3)
    pid = pet_pid()
    if pid is not None:
        terminate_pid(pid)
    return not pet_running()


def host_running():
    names = set(process_names())
    return bool(names & HOST_NAMES)


def disabled():
    return os.path.exists(DISABLED_FLAG)


def clear_disabled():
    try:
        os.remove(DISABLED_FLAG)
    except OSError:
        pass


def watcher_already_running():
    try:
        with open(WATCHER_PID_FILE, encoding="utf-8") as f:
            pid = int(f.read().strip())
        return pid_alive(pid)
    except Exception:
        return False


def main():
    if watcher_already_running():
        return
    with open(WATCHER_PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    was_host_running = False
    while True:
        host = host_running()
        if host and not was_host_running:
            clear_disabled()
        if host:
            if not pet_running() and not disabled():
                launch_pet()
        elif pet_running():
            close_pet()
        was_host_running = host
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
