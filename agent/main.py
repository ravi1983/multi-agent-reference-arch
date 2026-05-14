from fastapi import FastAPI
from pydantic import BaseModel
from agent.create_b2b_agent import create_b2b_agent

# python -m uvicorn agent.main:app --reload

app = FastAPI()

class Message(BaseModel):
    input: str
    thread_id: str

ecom_agent = create_b2b_agent()

def invoke_agent(message: Message):
    config = {'configurable': {'thread_id': message.thread_id}}
    return ecom_agent.ainvoke({'input': message.input}, config=config)

def print_messages(messages):
    for m in messages:
        m.pretty_print()

@app.post("/ce")
def invoke_for_ce(message: Message):
    return invoke_agent(message)

@app.post("/")
async def invoke(message: Message):
    out = await invoke_agent(message)

    print_messages(out.get('messages', []))

    return {
        "MessagesSize": len(out.get('messages', [])),
        "Summary": out.get('summary', ''),
        "Plans": out.get('plans', ''),
        "Items": out.get('items', ''),
        "Cart": out.get('cart', ''),
        "OrderNumbers": out.get('order_numbers', ''),
    }