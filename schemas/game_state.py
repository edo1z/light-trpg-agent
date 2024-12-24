from pydantic import BaseModel, Field
from typing import List


class GameState(BaseModel):
    session_id: str = Field(description="ユーザー単位またはセッションごとのID")
    world_intro: str = Field(default="", description="初期世界観説明")
    story_log: List[str] = Field(
        default_factory=list, description="これまでの描写や行動のログ"
    )
    player_hp: int = Field(default=10, description="プレイヤーのHP")
    items: List[str] = Field(default_factory=list, description="所持アイテムリスト")
    turn_count: int = Field(default=0, description="現在のターン数")
    max_turns: int = Field(default=3, description="セッション終了までの最大ターン数")
    current_status: str = Field(
        default="START", description="ゲームの状態（START/IN_PROGRESS/END）"
    )
