import asyncio
import functools
import logging
import os
import time

import aiohttp

import azure.functions as func


def timer(func):
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            print(
                f"Total execution time for async {func.__name__}(): {time.time() - start_time:_.2f} sec(s)."
            )
            if result:
                return result

        return wrapper
    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            print(
                f"Total execution time for sync {func.__name__}(): {time.time() - start_time:_.2f} sec(s)."
            )
            if result:
                return result

        return wrapper


@timer
async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("*******Starting main function*******")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            os.environ["LOGICAPP_URL"],
        ) as response:
            logging.info(response.status)

    return func.HttpResponse(status_code=200, body=f"Completed.")