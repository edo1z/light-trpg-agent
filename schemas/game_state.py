from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Annotated, List
from typing_extensions import TypedDict


class GameState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    player_hp: int
    items: List[str]
    turn_count: int
    max_turns: int
    current_status: str
