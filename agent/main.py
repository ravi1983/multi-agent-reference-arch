from fastapi import FastAPI
from langfuse import observe, propagate_attributes
from pydantic import BaseModel
from langfuse.langchain import CallbackHandler
from agent.create_b2b_agent import create_b2b_agent

# python -m uvicorn agent.main:app --reload

app = FastAPI()


class Message(BaseModel):
    input: str
    session_id: str
    user_id: str


ecom_agent = create_b2b_agent()
langfuse_handler = CallbackHandler()


def _invoke_agent(message: Message):
    with propagate_attributes(session_id=message.session_id, user_id=message.user_id):
        config = {
            "configurable": {"thread_id": message.user_id},
            "callbacks": [langfuse_handler],
        }
        return ecom_agent.ainvoke({"input": message.input}, config=config)


def _print_messages(messages):
    for m in messages:
        m.pretty_print()


@observe
@app.post("/ce")
async def invoke_for_ce(message: Message):
    return await _invoke_agent(message)


@observe
@app.post("/")
async def invoke(message: Message):
    out = await _invoke_agent(message)
    _print_messages(out.get("messages", []))

    return {
        "MessagesSize": len(out.get("messages", [])),
        "Summary": out.get("summary", ""),
        "Plans": out.get("plans", ""),
        "Items": out.get("items", ""),
        "Cart": out.get("cart", ""),
        "OrderNumbers": out.get("order_numbers", ""),
    }
