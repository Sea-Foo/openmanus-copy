import asyncio

from src.logger import logger


async def main():

    try:
        prompt = input("Enter your prompy: ")

    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")


if __name__ == "__main__":
    asyncio.run(main())
