import multiprocessing


def get_worker_number() -> int:
    return multiprocessing.cpu_count() * 2 + 1
