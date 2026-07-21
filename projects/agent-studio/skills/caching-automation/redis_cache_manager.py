#!/usr/bin/env python3
"""
Redis Cache Manager — TTL, warming, invalidation, distributed locking
"""
import argparse, json, redis, time, hashlib, logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("redis_cache")

class RedisCacheManager:
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        self.r = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
        self._check_connection()
    
    def _check_connection(self):
        try:
            self.r.ping()
            logger.info(f"Connected to Redis {self.r.connection_pool.connection_kwargs['host']}:{self.r.connection_pool.connection_kwargs['port']}")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def get(self, key: str) -> Optional[str]:
        return self.r.get(key)
    
    def set(self, key: str, value, ttl: int = 300):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.r.setex(key, ttl, value)
    
    def delete(self, key: str):
        self.r.delete(key)
    
    def get_with_expiry(self, key: str):
        """Returns (value, expiry_timestamp) or (None, None)"""
        p = self.r.pipeline()
        p.get(key)
        p.ttl(key)
        val, ttl = p.execute()
        if val is None:
            return None, None
        return val, time.time() + (ttl if ttl > 0 else 0)
    
    def invalidate_pattern(self, pattern: str):
        keys = self.r.keys(pattern)
        if keys:
            self.r.delete(*keys)
            logger.info(f"Invalidated {len(keys)} keys matching '{pattern}'")
    
    def stats(self):
        info = self.r.info("stats")
        keyspace = self.r.info("keyspace")
        print(f"  Keyspace: {keyspace}")
        print(f"  Total commands: {info.get('total_commands_processed', 0)}")
        print(f"  Keyspace hits: {info.get('keyspace_hits', 0)}")
        print(f"  Keyspace misses: {info.get('keyspace_misses', 0)}")
        hit_rate = info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1) * 100
        print(f"  Hit rate: {hit_rate:.1f}%")
    
    def warm(self, keys_data):
        """keys_data: list of {key, fetch_fn} dicts"""
        count = 0
        for entry in keys_data:
            key = entry["key"]
            value = entry["value"]
            ttl = entry.get("ttl", 300)
            self.set(key, value, ttl)
            count += 1
        logger.info(f"Warmed {count} cache entries")
    
    def distributed_lock(self, key: str, ttl: int = 10):
        """Acquire a distributed lock using SET NX EX."""
        lock_key = f"lock:{key}"
        acquired = self.r.set(lock_key, "1", nx=True, ex=ttl)
        return acquired
    
    def release_lock(self, key: str):
        self.r.delete(f"lock:{key}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=6379)
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--warm", action="store_true")
    parser.add_argument("--keys-file", default="")
    args = parser.parse_args()
    
    try:
        manager = RedisCacheManager(host=args.host, port=args.port)
        if args.stats:
            manager.stats()
        elif args.warm:
            if args.keys_file:
                with open(args.keys_file) as f:
                    keys_data = json.load(f)
            else:
                keys_data = []
            manager.warm(keys_data)
        else:
            print("Redis Cache Manager ready. Use --stats or --warm")
    except redis.ConnectionError:
        print("⚠️ Redis not available — install and start Redis first: redis-server")

if __name__ == "__main__":
    main()
