import asyncio
from database import Base, engine  # Make sure `engine` is an instance of AsyncEngine
from model import ChatHistory  # import your model(s)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())
