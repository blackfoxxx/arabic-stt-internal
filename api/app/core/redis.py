"""
Redis configuration and utilities
"""

import json
import pickle
from typing import Any, Optional, Union, Dict, List
import redis.asyncio as aioredis
from redis.asyncio import Redis
import structlog
from contextlib import asynccontextmanager

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Global Redis connection
_redis_client: Optional[Redis] = None


async def init_redis() -> Redis:
    """Initialize Redis connection"""
    global _redis_client
    
    try:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=False,  # Handle binary data for caching
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={}
        )
        
        # Test connection
        await _redis_client.ping()
        logger.info("Redis connection initialized successfully")
        return _redis_client
        
    except Exception as e:
        logger.error("Failed to initialize Redis connection", error=str(e))
        raise


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


async def get_redis() -> Redis:
    """Get Redis client instance"""
    global _redis_client
    if not _redis_client:
        _redis_client = await init_redis()
    return _redis_client


async def get_redis_health() -> bool:
    """Check Redis health"""
    try:
        redis = await get_redis()
        await redis.ping()
        return True
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return False


class RedisCache:
    """Redis caching utilities"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def _get_client(self) -> Redis:
        """Get Redis client"""
        if not self.redis:
            self.redis = await get_redis()
        return self.redis
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            redis = await self._get_client()
            value = await redis.get(key)
            if value is None:
                return default
            return pickle.loads(value)
        except Exception as e:
            logger.error("Redis get failed", key=key, error=str(e))
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            redis = await self._get_client()
            serialized = pickle.dumps(value)
            if expire:
                await redis.setex(key, expire, serialized)
            else:
                await redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error("Redis set failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            redis = await self._get_client()
            result = await redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error("Redis delete failed", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            redis = await self._get_client()
            result = await redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error("Redis exists failed", key=key, error=str(e))
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            redis = await self._get_client()
            return await redis.incrby(key, amount)
        except Exception as e:
            logger.error("Redis increment failed", key=key, error=str(e))
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        try:
            redis = await self._get_client()
            return await redis.expire(key, seconds)
        except Exception as e:
            logger.error("Redis expire failed", key=key, error=str(e))
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values"""
        try:
            redis = await self._get_client()
            values = await redis.mget(keys)
            result = {}
            for i, key in enumerate(keys):
                if values[i] is not None:
                    result[key] = pickle.loads(values[i])
                else:
                    result[key] = None
            return result
        except Exception as e:
            logger.error("Redis get_many failed", keys=keys, error=str(e))
            return {key: None for key in keys}
    
    async def set_many(
        self, 
        mapping: Dict[str, Any], 
        expire: Optional[int] = None
    ) -> bool:
        """Set multiple values"""
        try:
            redis = await self._get_client()
            
            # Serialize all values
            serialized = {k: pickle.dumps(v) for k, v in mapping.items()}
            
            # Set all values
            await redis.mset(serialized)
            
            # Set expiration if specified
            if expire:
                for key in mapping.keys():
                    await redis.expire(key, expire)
            
            return True
        except Exception as e:
            logger.error("Redis set_many failed", error=str(e))
            return False


class RedisRateLimiter:
    """Redis-based rate limiting"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def _get_client(self) -> Redis:
        """Get Redis client"""
        if not self.redis:
            self.redis = await get_redis()
        return self.redis
    
    async def is_allowed(
        self, 
        identifier: str,
        limit: int,
        window: int,
        burst_limit: Optional[int] = None
    ) -> tuple[bool, dict]:
        """Check if request is allowed using token bucket algorithm"""
        try:
            redis = await self._get_client()
            
            # Use Lua script for atomic rate limiting
            lua_script = """
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            local burst_limit = tonumber(ARGV[4]) or limit
            
            local current = redis.call('HMGET', key, 'count', 'reset_time', 'burst_used')
            local count = tonumber(current[1]) or 0
            local reset_time = tonumber(current[2]) or (now + window)
            local burst_used = tonumber(current[3]) or 0
            
            -- Reset window if expired
            if now >= reset_time then
                count = 0
                burst_used = 0
                reset_time = now + window
            end
            
            -- Check if request is allowed
            local allowed = false
            if count < limit then
                allowed = true
                count = count + 1
            elseif burst_used < burst_limit then
                allowed = true
                burst_used = burst_used + 1
            end
            
            if allowed then
                redis.call('HMSET', key, 'count', count, 'reset_time', reset_time, 'burst_used', burst_used)
                redis.call('EXPIRE', key, window)
            end
            
            return {allowed and 1 or 0, count, limit, reset_time, burst_used, burst_limit}
            """
            
            import time
            result = await redis.eval(
                lua_script, 
                1, 
                f"rate_limit:{identifier}",
                limit, 
                window, 
                int(time.time()),
                burst_limit or limit
            )
            
            allowed, count, limit, reset_time, burst_used, burst_limit = result
            
            return bool(allowed), {
                'allowed': bool(allowed),
                'count': int(count),
                'limit': int(limit),
                'remaining': max(0, int(limit) - int(count)),
                'reset_time': int(reset_time),
                'burst_used': int(burst_used),
                'burst_remaining': max(0, int(burst_limit) - int(burst_used))
            }
            
        except Exception as e:
            logger.error("Rate limiting failed", identifier=identifier, error=str(e))
            # Fail open - allow request if rate limiting fails
            return True, {'error': str(e)}


class RedisJobQueue:
    """Redis-based job queue for Celery integration"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def _get_client(self) -> Redis:
        """Get Redis client"""
        if not self.redis:
            self.redis = await get_redis()
        return self.redis
    
    async def get_queue_length(self, queue_name: str = "default") -> int:
        """Get queue length"""
        try:
            redis = await self._get_client()
            return await redis.llen(f"celery:{queue_name}")
        except Exception as e:
            logger.error("Failed to get queue length", queue=queue_name, error=str(e))
            return 0
    
    async def get_active_jobs(self) -> int:
        """Get number of active jobs"""
        try:
            redis = await self._get_client()
            # Count active Celery workers
            active_keys = await redis.keys("celery-task-meta-*")
            active_count = 0
            for key in active_keys:
                task_data = await redis.get(key)
                if task_data and b"PENDING" in task_data:
                    active_count += 1
            return active_count
        except Exception as e:
            logger.error("Failed to get active jobs", error=str(e))
            return 0
    
    async def clear_queue(self, queue_name: str = "default") -> bool:
        """Clear job queue"""
        try:
            redis = await self._get_client()
            await redis.delete(f"celery:{queue_name}")
            return True
        except Exception as e:
            logger.error("Failed to clear queue", queue=queue_name, error=str(e))
            return False


# Global instances
cache = RedisCache()
rate_limiter = RedisRateLimiter()
job_queue = RedisJobQueue()