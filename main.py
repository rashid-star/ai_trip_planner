from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from starlette.responses import JSONResponse
import logging
import os
import time
from typing import Literal
from uuid import uuid4

from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("wanderly.api")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class QueryRequest(BaseModel):
    question: str
    response_length: Literal["short", "standard", "detailed"] = "standard"


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/query")
async def query_travel_agent(query:QueryRequest):
    request_id = str(uuid4())
    started_at = time.perf_counter()
    try:
        graph = GraphBuilder(model_provider="groq", response_length=query.response_length)
        react_app=graph()
        #react_app = graph.build_graph()

        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)

        print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        # Assuming request is a pydantic object like: {"question": "your text"}
        messages={"messages": [query.question]}
        output = react_app.invoke(
            messages,
            config={
                "run_name": "wanderly-trip-planner",
                "tags": ["travel-planner", query.response_length],
                "metadata": {"request_id": request_id},
            },
        )

        # If result is dict with messages:
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  # Last AI response
        else:
            final_output = str(output)
        
        latency_ms = round((time.perf_counter() - started_at) * 1000)
        logger.info(
            "request_id=%s response_length=%s latency_ms=%s",
            request_id,
            query.response_length,
            latency_ms,
        )
        return {
            "answer": final_output,
            "request_id": request_id,
            "latency_ms": latency_ms,
            "response_length": query.response_length,
        }
    except Exception as e:
        logger.exception("request_id=%s trip planning failed", request_id)
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "request_id": request_id},
        )