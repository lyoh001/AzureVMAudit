import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("*******Starting main function*******")

    return func.HttpResponse(status_code=200, body=f"Ready.")
