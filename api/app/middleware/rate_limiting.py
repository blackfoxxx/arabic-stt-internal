"""
Rate limiting middleware
"""

import time
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.core.redis import rate_limiter

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/metrics"] or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Get identifier (user ID or IP)
        user_id = getattr(request.state, 'user_id', None)
        identifier = user_id or request.client.host
        
        # Different limits based on authentication
        if user_id:
            limit = 1000  # Authenticated: 1000 req/hour
            window = 3600
            burst_limit = 100
        else:
            limit = 100   # Anonymous: 100 req/hour
            window = 3600  
            burst_limit = 20
        
        # Check rate limit
        try:
            allowed, info = await rate_limiter.is_allowed(
                identifier, limit, window, burst_limit
            )
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": "Too many requests",
                        "retry_after": info.get('reset_time', time.time() + 3600) - time.time()
                    }
                )
            
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(info.get('limit', limit))
            response.headers["X-RateLimit-Remaining"] = str(info.get('remaining', 0))
            response.headers["X-RateLimit-Reset"] = str(info.get('reset_time', time.time() + 3600))
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Rate limiting error", error=str(e))
            # Fail open - allow request if rate limiting fails
            return await call_next(request)