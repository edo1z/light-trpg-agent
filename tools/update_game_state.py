from langchain_core.tools import tool
from typing import List
from schemas import GameState
from langgraph.types import Command
from typing import Dict, Any
from langchain_core.messages import ToolMessage


@tool
def update_game_state(
    game_state: GameState,
    hp_change: int = 0,
    items_to_add: List[str] = None,
    items_to_remove: List[str] = None,
    turn_count_inc: int = 0,
    tool_call_id: str = "default",
) -> Command:
    """ゲームの状態を一括で更新します。HP、アイテム、ターン数を同時に更新できます。"""
    items = game_state["items"].copy()
    if items_to_add:
        items.extend(items_to_add)
    if items_to_remove:
        for item in items_to_remove:
            if item in items:
                items.remove(item)

    new_turn = game_state["turn_count"] + turn_count_inc

    return Command(
        update={
            "player_hp": game_state["player_hp"] + hp_change,
            "items": items,
            "turn_count": new_turn,
            "current_status": (
                "END"
                if new_turn >= game_state["max_turns"]
                else game_state.get("current_status", "PLAYING")
            ),
            "messages": [
                ToolMessage(
                    content=f"ゲーム状態を更新しました：\nHP: {game_state['player_hp']} → {game_state['player_hp'] + hp_change}\nアイテム: {items}\nターン: {new_turn}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )
