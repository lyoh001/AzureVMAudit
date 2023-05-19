import asyncio
import functools
import logging
import os
import time

import aiohttp

import azure.functions as func
from azure.storage.blob import BlobServiceClient


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
    try:
        async with aiohttp.ClientSession() as session:
            blob_service_client = BlobServiceClient.from_connection_string(
                os.environ["CONN_STR"]
            )
            blob_client = blob_service_client.get_blob_client("final", "vmaudit.csv")

            async with session.post(
                url=os.environ["LOGICAPP_URL"],
                json={"attachment": blob_client.download_blob().content_as_text()},
            ) as response:
                logging.info(response.status)

        return func.HttpResponse(status_code=200, body="Completed.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

        return func.HttpResponse(status_code=500, body="Error occurred.")
