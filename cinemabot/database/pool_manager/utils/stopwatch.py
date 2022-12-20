import statistics
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from typing import Any, Generator, Optional


class Stopwatch:
    def __init__(self, window_size: int) -> None:
        self._times = defaultdict(lambda: deque(maxlen=window_size))  # type: ignore
        self._cache = {}  # type: ignore

    def get_time(self, obj: Any) -> Optional[float]:
        if obj not in self._times:
            return None
        if self._cache.get(obj) is None:
            self._cache[obj] = statistics.median(self._times[obj])
        return self._cache[obj]

    @contextmanager
    def __call__(self, obj: Any) -> Generator[None, None, None]:
        start_at = time.monotonic()
        yield
        self._times[obj].append(time.monotonic() - start_at)
        self._cache[obj] = None
