"""Minimal Celery stub for test environments without celery installed."""


class _StubTask:
    """Wraps a plain function so it behaves like a bound Celery task in tests."""

    def __init__(self, fn, bind: bool = True):
        self._fn = fn
        self.request = type("req", (), {"retries": 0})()
        self.max_retries = 3
        self._bind = bind

    def __call__(self, *args, **kwargs):
        if self._bind:
            return self._fn(self, *args, **kwargs)
        return self._fn(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)

    def delay(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)

    def retry(self, exc=None, countdown=0):
        raise exc or RuntimeError("retry")


def shared_task(fn=None, *, bind=False, max_retries=3, **_kwargs):  # type: ignore[misc]
    """Drop-in replacement for celery.shared_task with no broker dependency."""
    def decorator(f):
        return _StubTask(f, bind=bind)
    if fn is not None:
        return decorator(fn)
    return decorator


MaxRetriesExceededError = Exception  # type: ignore[assignment]
