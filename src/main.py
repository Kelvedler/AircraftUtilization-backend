from functools import partial
import multiprocessing as mp
import signal
import sys
import time

import psutil
import uvicorn

from core.settings import log_config, settings
from core.uvicorn import get_worker_number


def signal_handler(proc: mp.Process, *_) -> None:
    pid = proc.pid
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    proc.terminate()
    for _ in range(5):
        if proc.is_alive():
            time.sleep(1)
        else:
            break
    sys.exit(0)


def run() -> None:
    proc = mp.Process(
        target=uvicorn.run,
        args=("app:app",),
        kwargs={
            "host": settings.app.host,
            "port": settings.app.port,
            "log_config": log_config,
            "workers": get_worker_number(),
        },
    )
    proc.start()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, partial(signal_handler, proc))
    signal.pause()


if __name__ == "__main__":
    run()
