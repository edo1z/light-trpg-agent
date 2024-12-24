from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List
from game_state import GameState


class SummarizeStoryInput(BaseModel):
    game_state: GameState
    input_text: str = Field(default="", description="追加のコンテキスト（オプション）")


@tool(args_schema=SummarizeStoryInput)
def summarize_story(game_state: GameState, input_text: str = "") -> str:
    """これまでのストーリーログを要約して短い物語形式にまとめます。"""
    story_log = game_state.story_log
    summary = "Here's a quick summary of your adventure:\n"
    summary += "\n".join(story_log)
    return summary
