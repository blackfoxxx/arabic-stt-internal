#!/usr/bin/env python3
"""
Database initialization script
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import get_async_engine, Base
from app.models import *  # Import all models

async def init_database():
    """Initialize database tables and extensions"""
    
    print("🔄 Initializing database...")
    
    engine = get_async_engine()
    
    try:
        async with engine.begin() as conn:
            # Create extensions
            print("📦 Creating PostgreSQL extensions...")
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pg_trgm"'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "unaccent"'))
            
            # Create all tables
            print("🏗️  Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            
            print("✅ Database initialized successfully!")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())