from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from config import DATABASE_URI
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
import asyncpg
import aioredis
from config import REDIS_URL

async def async_database_exists(engine: AsyncEngine, db_name: str) -> bool:
    async with engine.connect() as conn:
        try:
            # This query checks the existence of the database
            result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
            return bool(list(result))
        except Exception as e:
            # Log the exception or handle it as necessary
            print(f"Error checking database existence: {e}")
            return False

# async def async_create_database(engine, url):
#     async with engine.connect() as conn:
#         await conn.execute(text(f"CREATE DATABASE {url.split('/')[-1]}"))


async def async_drop_database(url):
    # Extract the database name and credentials from the URL
    db_name = url.split('/')[-1]
    user = url.split('//')[1].split(':')[0]
    password = url.split(':')[2].split('@')[0]
    host = url.split('@')[1].split(':')[0]
    port = url.split(':')[3].split('/')[0]

    # Connect to the database server using the default 'postgres' database
    conn = await asyncpg.connect(user=user, password=password, database='postgres', host=host, port=port)
    try:
        # Terminate all other connections to the database to be dropped
        await conn.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = $1
              AND pid <> pg_backend_pid();
        """, db_name)  # noqa: F541
        
        # Execute DROP DATABASE command in autocommit mode
        await conn.execute(f'DROP DATABASE IF EXISTS {db_name}')
    finally:
        # Close the connection
        await conn.close()

async def async_create_database(uri: str, db_name: str):
    # Connect to the default 'postgres' database to create a new database
    temp_uri = uri.rsplit('/', 1)[0] + '/postgres'
    engine = create_async_engine(temp_uri, isolation_level="AUTOCOMMIT")
    
    async with engine.connect() as conn:
        await conn.execute(text(f"CREATE DATABASE {db_name}"))



async def flush_all_redis_data():
    # Connect to Redis using the URL from the configuration
    redis = aioredis.from_url(REDIS_URL)
    
    # Execute the flushall command to clear all data
    await redis.flushall()
    
    # Close the connection
    await redis.close()
    print("All Redis data cleared.")

async def recreate_database(uri: str):
    db_name = uri.split('/')[-1]
    # Connect to the default 'postgres' database to check existence and drop the database
    temp_uri = uri.rsplit('/', 1)[0] + '/postgres'
    temp_engine = create_async_engine(temp_uri, isolation_level="AUTOCOMMIT")

    if await async_database_exists(temp_engine, db_name):
        print(f"Dropping database {uri}")
        await async_drop_database(uri)
    
    print(f"Creating database {uri}")
    await async_create_database(uri, db_name)
    print("Database recreated successfully")

    print("Clearing Redis data")
    await flush_all_redis_data()
    print ("Redis data cleared successfully")




if __name__ == "__main__":
    asyncio.run(recreate_database(DATABASE_URI))