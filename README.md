# Wanderly AI Trip Planner

Wanderly is an AI-powered travel planner that creates day-by-day itineraries with destination research, weather, activities, restaurants, transport suggestions, and expense estimates.

## Features

- Streamlit UI with example prompts, backend status, conversation history, and Markdown download
- FastAPI backend with `/health` and `/query` endpoints
- LangGraph agent loop with conditional tool routing through LangChain tools
- Configurable response styles with token budgets (`short`, `standard`, `detailed`)
- Request IDs, latency metrics, structured logs, and LangSmith-compatible run metadata
- Groq-powered travel planning
- Weather, Google Places, Tavily fallback search, currency conversion, and trip calculators
- Configurable model in `config/config.yaml`

## Requirements

- Python 3.10+
- A Groq API key
- Optional keys for weather, Google Places, Tavily, and currency conversion tools

## Setup

Install dependencies with uv:

```powershell
uv pip install -r requirements.txt
```

Create a `.env` file in the project root. Use the exact variable names below:

```env
GROQ_API_KEY=your_groq_key
OPENWEATHERMAP_API_KEY=your_openweather_key
GPLACES_API_KEY=your_google_places_key
TAVILY_API_KEY=your_tavily_key
EXCHANGE_RATE_API_KEY=your_exchange_rate_key
```

The Google Places, weather, Tavily, and exchange-rate keys support tool features. Keep `.env` private and never commit real keys.

Optional LangSmith observability can be enabled in `.env`:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=wanderly-trip-planner
```

When enabled, each request is tagged with its response style and request ID so you can inspect graph runs, tool calls, latency, and failures in LangSmith.

## Run the application

Start the backend in one terminal:

```powershell
uv run uvicorn main:app --reload
```

Start the Streamlit UI in a second terminal:

```powershell
uv run streamlit run app.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`.

The backend API is available at `http://localhost:8000`. Test its health endpoint:

```powershell
curl http://localhost:8000/health
```

## API example

```powershell
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"Plan a 5-day trip to Goa\", \"response_length\":\"standard\"}'
```

## Project structure

```text
agent/            LangGraph workflow
config/           Model configuration
prompt_library/   Travel-agent system prompt
tools/            LangChain tools
utils/            API clients and shared helpers
app.py            Streamlit frontend
main.py           FastAPI backend
```

## Architecture and resume highlights

1. FastAPI validates the request and assigns a request ID.
2. `GraphBuilder` creates a LangGraph state graph with an agent node and a conditional tool node.
3. The LangChain model selects weather, places, currency, or calculator tools when needed.
4. The graph returns a concise itinerary with response-length-specific token limits.
5. API logs capture request ID and latency, while optional LangSmith tracing captures the run and tool path.

## Safety and data notes

AI-generated plans can contain outdated prices, opening hours, weather, or travel requirements. Verify important details before booking. Rotate any API key that has been exposed and keep `.env` out of Git.
