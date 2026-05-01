import os
import subprocess


def hidden_startup_options() -> tuple[subprocess.STARTUPINFO | None, int]:
    startupinfo = None
    creationflags = 0
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return startupinfo, creationflags


def terminate_process_tree(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return

    proc.terminate()
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/F", "/T"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
