#!/usr/bin/env python3
"""
Cache Strategy Implementations — cache-aside, write-through, write-behind patterns
"""
import time, hashlib, json, logging
from typing import Any, Callable, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cache_strategies")

class CacheAside:
    """Cache-Aside pattern: app manages cache, DB is source of truth."""
    
    def __init__(self, cache_backend):
        self.cache = cache_backend  # any get(key)/set(key, value, ttl)/delete(key) backend
    
    def get(self, key: str, fetch_fn: Callable[[], Any], ttl: int = 300) -> Any:
        cached = self.cache.get(key)
        if cached is not None:
            logger.info(f"CACHE HIT: {key}")
            return cached
        logger.info(f"CACHE MISS: {key} — fetching from source")
        value = fetch_fn()
        self.cache.set(key, value, ttl)
        return value
    
    def invalidate(self, key: str):
        self.cache.delete(key)
        logger.info(f"INVALIDATED: {key}")


class WriteThrough:
    """Write-Through: write to cache and DB simultaneously."""
    
    def __init__(self, cache_backend, db):
        self.cache = cache_backend
        self.db = db
    
    def write(self, key: str, value: Any, ttl: int = 300):
        # Write to DB first
        self.db.set(key, value)
        # Then update cache
        self.cache.set(key, value, ttl)
        logger.info(f"WRITE-THROUGH: {key}")


class WriteBehind:
    """Write-Behind: write to cache, async flush to DB."""
    
    def __init__(self, cache_backend, db, flush_interval: int = 5):
        self.cache = cache_backend
        self.db = db
        self.dirty = {}  # pending writes
        self.flush_interval = flush_interval
        self._last_flush = time.time()
    
    def write(self, key: str, value: Any, ttl: int = 300):
        self.cache.set(key, value, ttl)
        self.dirty[key] = value
        
        if time.time() - self._last_flush > self.flush_interval:
            self._flush()
    
    def _flush(self):
        for key, value in self.dirty.items():
            self.db.set(key, value)
        self.dirty.clear()
        self._last_flush = time.time()
        logger.info(f"FLUSHED {len(self.dirty)} dirty keys to DB")


class ProbabilisticEarlyExpiration:
    """Prevent cache stampede with probabilistic early refresh."""
    
    def __init__(self, cache, fetch_fn, beta: float = 1.0):
        self.cache = cache
        self.fetch_fn = fetch_fn
        self.beta = beta  # higher = more aggressive early refresh
    
    def get(self, key: str, ttl: int = 300) -> Any:
        value, expiry = self.cache.get_with_expiry(key)
        if value is None:
            return self.fetch_fn()
        
        age = time.time() - expiry + ttl
        # Probabilistic refresh: refresh when remaining TTL is small relative to total
        refresh_prob = self.beta * (age / ttl) ** 2
        if refresh_prob > 0.1:  # simplified threshold
            # Asynchronously refresh (in production, use threading/task queue)
            logger.info(f"EARLY REFRESH: {key} (prob={refresh_prob:.2f})")
            # In practice: queue refresh task, return stale value immediately
            return value
        
        return value


def main():
    print("Cache Strategy Examples:")
    print("1. Cache-Aside — read-heavy, DB source of truth")
    print("2. Write-Through — consistent reads, slower writes")
    print("3. Write-Behind — fast writes, eventual consistency")
    print("4. Probabilistic Early Expiration — stampede prevention")
    print("\nSee source code for usage patterns.")

if __name__ == "__main__":
    main()
