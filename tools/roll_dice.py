from langchain_core.tools import tool
import random


@tool
def roll_dice(dice_spec: str) -> str:
    """サイコロを振ります（例：1d6, 2d6）。結果を整数で返します。"""
    if "d6" in dice_spec:
        num_dice = int(dice_spec.split("d")[0])
        total = 0
        for _ in range(num_dice):
            total += random.randint(1, 6)
        return str(total)
    return "4"  # fallback mock
