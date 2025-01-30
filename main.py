import time
import os
import asyncio

from fastapi import FastAPI, HTTPException, Request, Response
from aiologger import Logger
from pydantic import HttpUrl
from dotenv import load_dotenv

from src.clients.google import GoogleSearchClient
from src.clients.duckduckgo import DuckDuckGoClient
from src.clients.gpt import OpenAIClient
from src.constants import SYSTEM_PROMPT, USER_PROMPT
from src.schemas.request import PredictionRequest, PredictionResponse
from src.utils.logger import setup_logger

load_dotenv()

app = FastAPI()
logger: Logger | None = None

google_client: GoogleSearchClient | None = None
duckduckgo_client: DuckDuckGoClient | None = None

gpt_client: OpenAIClient | None = None
gpt_model: str | None = None


def fetch_google_results(query):
    try:
        return google_client.search(query=query, num=3, language="lang_ru")
    except Exception as e:
        logger.error(f"Failed to parse Google: {e}")
        return []


def fetch_duckduckgo_results(query):
    try:
        return duckduckgo_client.search(query=query, num=5, language="ru-ru")
    except Exception as e:
        logger.error(f"Failed to parse DuckDuckGo: {e}")
        return []


@app.on_event("startup")
async def startup_event():
    global logger, google_client, duckduckgo_client, gpt_client, gpt_model

    logger = await setup_logger()

    google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_search_cx = os.getenv("GOOGLE_SEARCH_CX")
    google_client = GoogleSearchClient(google_search_api_key, google_search_cx)

    duckduckgo_client = DuckDuckGoClient()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_tunnel_url = os.getenv("OPENAI_TUNNEL_URL")
    gpt_client = OpenAIClient(openai_api_key, openai_tunnel_url, SYSTEM_PROMPT)
    gpt_model = os.getenv("OPENAI_MODEL")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    body = await request.body()
    await logger.info(
        f"Incoming request: {request.method} {request.url}\n"
        f"Request body: {body.decode()}"
    )

    response = await call_next(request)
    process_time = time.time() - start_time

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    await logger.info(
        f"Request completed: {request.method} {request.url}\n"
        f"Status: {response.status_code}\n"
        f"Response body: {response_body.decode()}\n"
        f"Duration: {process_time:.3f}s"
    )

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.post("/api/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    try:
        await logger.info(f"Processing prediction request with id: {body.id}")

        query = body.query
        search_query = query.split("\n")[0]

        google_results, duckduckgo_results = await asyncio.gather(
            asyncio.to_thread(fetch_google_results, search_query),
            asyncio.to_thread(fetch_duckduckgo_results, search_query)
        )

        gpt_query = USER_PROMPT.format(duckduckgo_results, google_results, query)

        response = gpt_client.chat_completion(query, gpt_model)

        prediction_response = PredictionResponse(
            id=body.id,
            answer=response.get("answer", 0),
            reasoning=f'{gpt_model}: {response.get("reasoning", "No reasoning provided")}',
            sources=[HttpUrl(source) for source in response.get("sources")],
        )

        await logger.info(f"Successfully processed request {body.id}")
        return prediction_response

    except ValueError as e:
        error_msg = str(e)
        await logger.error(f"Validation error for request {body.id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        await logger.error(f"Internal error processing request {body.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
