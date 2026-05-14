import httpx
from langchain_openai import ChatOpenAI

http_client = httpx.Client(
    # verify=False,
    timeout=20
)

llm = ChatOpenAI(model="gpt-4.1", temperature=0, http_client=http_client)

llm_mini = ChatOpenAI(model="gpt-4.1-mini", temperature=0, http_client=http_client)
