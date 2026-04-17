import random
import time


MOCK_RESPONSES = {
    "default": [
        "Agent is running in production mode with mock LLM output.",
        "Request received successfully. This is a mock response.",
        "Your production-ready agent is working correctly.",
    ],
    "docker": ["Docker packages your app and dependencies for consistent runtime."],
    "deploy": ["Deployment is the process of releasing your app to a cloud environment."],
    "redis": ["Redis provides fast in-memory storage for shared state across instances."],
}


def ask(question: str, delay: float = 0.05) -> str:
    time.sleep(delay + random.uniform(0, 0.03))
    lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in lower:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])


def ask_stream(question: str):
    response = ask(question)
    for token in response.split():
        time.sleep(0.03)
        yield token + " "
