from langchain_core.tools import tool
from typing import List
from schemas import GameState


@tool
def update_turn(game_state: GameState, turn_count_inc: int = 1) -> str:
    """ターン数を更新し、必要に応じてゲーム終了判定を行います。"""
    print(f"[DEBUG] update_turn: turn_count_inc={turn_count_inc}")
    game_state.turn_count += turn_count_inc
    if game_state.turn_count >= game_state.max_turns:
        game_state.current_status = "END"
    return f"ターンを更新しました。現在のターン: {game_state.turn_count}"


@tool
def update_hp(game_state: GameState, hp_change: int) -> str:
    """プレイヤーのHPを更新します。"""
    print(f"[DEBUG] update_hp: hp_change={hp_change}")
    game_state.player_hp += hp_change
    return f"HPを更新しました。現在のHP: {game_state.player_hp}"


@tool
def manage_inventory(
    game_state: GameState,
    items_to_add: List[str] = None,
    items_to_remove: List[str] = None,
) -> str:
    """インベントリのアイテムを追加・削除します。"""
    print(f"[DEBUG] manage_inventory: add={items_to_add}, remove={items_to_remove}")
    if items_to_add:
        game_state.items.extend(items_to_add)
    if items_to_remove:
        for item in items_to_remove:
            if item in game_state.items:
                game_state.items.remove(item)
    return f"インベントリを更新しました。現在のインベントリ: {game_state.items}"
