from langchain_core.messages import SystemMessage


def build_system_prompt(response_length: str) -> SystemMessage:
    limits = {
        "short": "Keep the response under 350 words. Use one activity per day and one budget summary.",
        "standard": "Keep the response under 700 words. Use 2-3 activities per day and a compact budget.",
        "detailed": "Keep the response under 1200 words. Include useful details, but avoid long descriptions or repetition.",
    }
    limit = limits[response_length]
    return SystemMessage(
        content=f"""You are a practical AI travel planner. Use tools only when they add useful
current information. Return a clean Markdown itinerary:
- A one-line trip summary and assumptions
- A day-by-day plan
- 2-3 stay or food suggestions
- An estimated budget and daily average
- One useful weather or transport note
{limit}
Clearly label estimates and say when live data is unavailable.
"""
    )