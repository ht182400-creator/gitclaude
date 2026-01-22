from fastapi import Request, HTTPException, status, Depends
from fastapi import Request, HTTPException, status
import time
import os

# Rate limiter configuration
WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
LIMIT = int(os.getenv('RATE_LIMIT_LIMIT', '10'))

# Try to use Redis if REDIS_URL is provided, otherwise fall back to in-memory store
_store = {}
_redis = None
try:
    import redis
    REDIS_URL = os.getenv('REDIS_URL')
    if REDIS_URL:
        _redis = redis.from_url(REDIS_URL)
except Exception:
    _redis = None


def _get_key(request: Request):
    client = request.client.host if request.client else 'unknown'
    return client


def rate_limiter(request: Request):
    key = _get_key(request)
    now = int(time.time())
    window = now // WINDOW
    if _redis:
        redis_key = f"ratelimit:{key}:{window}"
        try:
            val = _redis.incr(redis_key)
            if val == 1:
                _redis.expire(redis_key, WINDOW)
            if val > LIMIT:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail='Too many requests')
        except Exception:
            # on Redis error, fall back to in-memory logic
            pass
        return True

    # in-memory fallback (per-process only)
    rec = _store.get(key)
    if rec and rec[0] == window:
        if rec[1] >= LIMIT:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail='Too many requests')
        rec[1] += 1
    else:
        _store[key] = [window, 1]
    return True
