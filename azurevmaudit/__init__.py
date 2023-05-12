import asyncio
import base64
import functools
import logging
import os
import time

import aiohttp
import azure.functions as func
import pandas as pd

df, rest_api_headers = pd.DataFrame(), ""
CONN_STR = os.environ["CONN_STR"]


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


def get_api_headers_decorator(func):
    @functools.wraps(func)
    async def wrapper(session, *args, **kwargs):
        return {
            "Authorization": f"Basic {base64.b64encode(bytes(os.environ[args[0]], 'utf-8')).decode('utf-8')}"
            if "PAT" in args[0]
            else f"Bearer {os.environ[args[0]] if 'EA' in args[0] else await func(session, *args, **kwargs)}",
            "Content-Type": "application/json-patch+json"
            if "PAT" in args[0]
            else "application/json",
        }

    return wrapper


@get_api_headers_decorator
async def get_api_headers(session, *args, **kwargs):
    oauth2_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    oauth2_body = {
        "client_id": os.environ[args[0]],
        "client_secret": os.environ[args[1]],
        "grant_type": "client_credentials",
        "scope" if "GRAPH" in args[0] else "resource": args[2],
    }
    async with session.post(
        url=args[3], headers=oauth2_headers, data=oauth2_body
    ) as resp:
        return (await resp.json())["access_token"]


async def fetch(session, subscription_id):
    print(f"starting: {subscription_id}")
    async with session.get(
        url=f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Compute/virtualMachines?api-version=2023-03-01",
        headers=rest_api_headers,
    ) as response:
        return (await response.json())["value"]


@timer
async def main(req: func.HttpRequest) -> func.HttpResponse:
    global df, rest_api_headers
    logging.info("*******Starting main function*******")
    async with aiohttp.ClientSession() as session:
        (rest_api_headers,) = await asyncio.gather(
            *(
                get_api_headers(session, *param)
                for param in [
                    [
                        "REST_CLIENT_ID",
                        "REST_CLIENT_SECRET",
                        "https://management.azure.com",
                        f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}/oauth2/token",
                    ]
                ]
            )
        )
        async with session.post(
            "https://management.azure.com/providers/Microsoft.Management/getEntities?api-version=2020-05-01",
            headers=rest_api_headers,
        ) as response:
            df_mg = pd.json_normalize((await response.json())["value"])

        total_resources = await asyncio.gather(
            *(fetch(session, subscription_id) for subscription_id in df_mg["id"])
        )
        df = pd.concat(
            [pd.json_normalize(resources) for resources in total_resources],
            ignore_index=True,
        )

    return func.HttpResponse(status_code=200, body=f"Ready.")
