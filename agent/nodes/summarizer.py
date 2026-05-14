import logging

from langchain.messages import RemoveMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

from agent.models.graph_models import B2BGraphState
from agent.nodes.common.model import llm_mini


def _generate_summary(state: B2BGraphState):
    """Generates new summary"""
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is a summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    return llm_mini.invoke(state["messages"] + [HumanMessage(summary_message)]).content


def summarizer(state: B2BGraphState):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=300,
        start_on="human",
        end_on=("human", "tool"),
    )
    kept_ids = {m.id for m in trimmed_messages}
    delete_messages = [
        RemoveMessage(id=msg.id) for msg in state["messages"] if msg.id not in kept_ids
    ]

    # Generate summary ONLY if messages were deleted
    if len(delete_messages) > 0:
        logging.info(f"Deleted {len(delete_messages)} messages. Generating summary.")
        summary = _generate_summary(state)
        return {"summary": summary, "messages": delete_messages}
    else:
        logging.info("No messages deleted. Not generating summary.")
        return {"messages": delete_messages}
