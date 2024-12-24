from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List
from schemas import GameState


class GameStateUpdate(BaseModel):
    game_state: GameState
    hp_change: int = Field(default=0, description="HPの変更値")
    items_to_add: List[str] = Field(
        default_factory=list, description="追加するアイテムのリスト"
    )
    turn_count_inc: int = Field(default=1, description="増加するターン数")


@tool(args_schema=GameStateUpdate)
def update_game_state(
    game_state: GameState,
    hp_change: int = 0,
    items_to_add: List[str] = None,
    turn_count_inc: int = 1,
) -> str:
    """ゲームの状態（HP、アイテム、ターン数など）を更新します。"""
    print(f"update_game_state: {game_state}")
    game_state.player_hp += hp_change
    if items_to_add:
        game_state.items.extend(items_to_add)
    game_state.turn_count += turn_count_inc

    if game_state.turn_count >= game_state.max_turns:
        game_state.current_status = "END"

    return f"GameState updated. HP={game_state.player_hp}, turn_count={game_state.turn_count}"
