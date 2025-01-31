import time

from fastapi import FastAPI, HTTPException, Request, Response
from aiologger import Logger
from pydantic import HttpUrl

from src.schemas.request import PredictionRequest, PredictionResponse
from src.utils.logger import setup_logger


from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
import json
from src.agent.agents import ITMOCrew

load_dotenv()

app = FastAPI()
crew: ITMOCrew | None = None
logger: Logger | None = None


@app.on_event("startup")
async def startup_event():
    global logger, crew

    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_api_base = os.getenv("OPENAI_API_BASE")
    model = os.getenv("OPENAI_MODEL")

    logger = await setup_logger()

    gpt = ChatOpenAI(
        openai_api_base=openai_api_base,
        openai_api_key=openai_api_key,
        model_name=model,
    )

    crew = ITMOCrew()
    crew.init_model(gpt)


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

        inputs = {'search_query': body.query}
        response = await crew.crew().kickoff_async(inputs=inputs)
        response = json.loads(response.json)

        prediction_response = PredictionResponse(
            id=body.id,
            answer=response.get("answer", 0),
            reasoning=f'{os.getenv("OPENAI_MODEL")}: {response.get("reasoning", "No reasoning provided")}',
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
