import asyncio

from app.utils.seed import seed_database


if __name__ == "__main__":
    asyncio.run(seed_database())
