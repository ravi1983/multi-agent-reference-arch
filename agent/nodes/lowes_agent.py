import json
import httpx

from langchain_core.messages import AIMessage

from agent.model.graph_models import B2BGraphState
from agent.model.llm_models import  PlanType
from agent.nodes.common.find_plan_for_agent import find_plan_for_agent

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import display_agent_card, new_text_message, get_artifact_text, get_message_text
from a2a.types.a2a_pb2 import Role, SendMessageRequest
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

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

async def lowes_agent(state: B2BGraphState):
    base_url = 'http://localhost:9095'

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default
        )

        # --8<-- [end:A2ACardResolver]

        print(
            f'Attempting to fetch public agent card from: {base_url}{AGENT_CARD_WELL_KNOWN_PATH}'
        )
        public_card = await resolver.get_agent_card()
        print('\nSuccessfully fetched public agent card:')
        display_agent_card(public_card)

        print('\n--- Non-Streaming Call ---')
        # --8<-- [start:message_send]
        config = ClientConfig(streaming=False)
        client = await create_client(agent=public_card, client_config=config)
        print('\nNon-streaming Client initialized.')

        input = "".join(find_plan_for_agent(state['plans'], PlanType.LOWES_AGENT))
        print(f'Input to lowes agent is: {input}')
        message = new_text_message(input, role=Role.ROLE_USER)
        request = SendMessageRequest(message=message)

        print('Response:')
        async for chunk in client.send_message(request):
            text = _chunk_text(chunk)
            if text:
                response = json.loads(text)
            
            context_id= _ids_from_chunk(chunk)
        print(response['items'])
        print(response['order_number'])


        result = {
            'messages': AIMessage(content=text),
            'items': response['items']
        }
        if response['order_number'] is not None:
            result["order_numbers"] = [response['order_number']]

        return result
