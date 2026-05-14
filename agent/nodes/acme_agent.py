import os
import json
import httpx
import logging

from langchain_core.messages import AIMessage

from agent.models.graph_models import B2BGraphState
from agent.models.llm_models import PlanType
from agent.nodes.common.find_plan_for_agent import find_plan_for_agent

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import (
    new_text_message,
    get_artifact_text,
    get_message_text,
)
from a2a.types.a2a_pb2 import Role, SendMessageRequest
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


def _process_input(state):
    return "".join(
        f"{p}. Items: {state['items']}" if p.place_order else p
        for p in find_plan_for_agent(state["plans"], PlanType.ACME_AGENT)
    )


def _chunk_text(chunk) -> str:
    if chunk.task:
        for artifact in chunk.task.artifacts:
            text = get_artifact_text(artifact)
            if text:
                return text

        if chunk.task.status and chunk.task.status.message:
            return get_message_text(chunk.task.status.message) or ""

    return ""


def _ids_from_chunk(chunk):
    if chunk.task:
        return chunk.task.context_id, chunk.task.id
    return None, None


# Initialize a global variable to hold the client
_ACME_CLIENT_CACHE = None


async def _get_shared_client(base_url):
    global _ACME_CLIENT_CACHE

    # If client exists, return it immediately
    if _ACME_CLIENT_CACHE is not None:
        return _ACME_CLIENT_CACHE

    # Otherwise, initialize it once
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        public_card = await resolver.get_agent_card()

        config = ClientConfig(streaming=False)
        _ACME_CLIENT_CACHE = await create_client(
            agent=public_card, client_config=config
        )

    return _ACME_CLIENT_CACHE


async def acme_agent(state: B2BGraphState):
    base_url = os.environ["REMOTE_AGENT_URL"]

    client = await _get_shared_client(base_url)

    input = "".join(find_plan_for_agent(state["plans"], PlanType.ACME_AGENT))
    logging.info(f"Input to acme agent is: {input}")

    message = new_text_message(
        input, role=Role.ROLE_USER, context_id=state.get("a2a_context_id", None)
    )
    request = SendMessageRequest(message=message)

    async for chunk in client.send_message(request):
        text = _chunk_text(chunk)
        if text:
            response = json.loads(text)

        context_id, _ = _ids_from_chunk(chunk)

    result = {
        "messages": AIMessage(content=text),
        "items": response["items"],
        "a2a_context_id": context_id,
    }
    if response["order_number"] is not None:
        result["order_numbers"] = [response["order_number"]]

    return result
