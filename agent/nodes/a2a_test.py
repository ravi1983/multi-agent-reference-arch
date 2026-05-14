import httpx
import json

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import (
    display_agent_card,
    new_text_message,
    get_artifact_text,
    get_message_text,
)
from a2a.types.a2a_pb2 import (
    Role,
    SendMessageRequest,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


def chunk_text(chunk) -> str:
    if chunk.task:
        for artifact in chunk.task.artifacts:
            text = get_artifact_text(artifact)
            if text:
                return text

        if chunk.task.status and chunk.task.status.message:
            return get_message_text(chunk.task.status.message) or ""

    return ""


def ids_from_chunk(chunk):
    if chunk.task:
        return chunk.task.context_id, chunk.task.id
    return None, None


async def main() -> None:
    # --8<-- [start:A2ACardResolver]
    base_url = "http://127.0.0.1:9095"

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default
        )

        # --8<-- [end:A2ACardResolver]

        print(
            f"Attempting to fetch public agent card from: {base_url}{AGENT_CARD_WELL_KNOWN_PATH}"
        )
        public_card = await resolver.get_agent_card()
        print("\nSuccessfully fetched public agent card:")
        display_agent_card(public_card)

        print("\n--- Non-Streaming Call ---")
        # --8<-- [start:message_send]
        config = ClientConfig(streaming=False)
        client = await create_client(agent=public_card, client_config=config)
        print("\nNon-streaming Client initialized.")

        message = new_text_message("show me washers", role=Role.ROLE_USER)
        request = SendMessageRequest(message=message)

        print("Response:")
        async for chunk in client.send_message(request):
            text = chunk_text(chunk)
            if text:
                items = text
                print(text)

            c_id, t_id = ids_from_chunk(chunk)
            context_id = c_id or context_id
        print("*******************************")
        message = new_text_message(
            f"Place order {json.loads(items)['items']}",
            role=Role.ROLE_USER,
            context_id=context_id,
        )
        request = SendMessageRequest(message=message)
        print(f"Context ID: {context_id}")

        print("Response:")
        async for chunk in client.send_message(request):
            text = chunk_text(chunk)
            if text:
                print(text)

        # --8<-- [end:message_send]


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
