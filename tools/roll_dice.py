from langchain_core.tools import tool
import random


@tool
def roll_dice(dice_spec: str) -> str:
    """サイコロを振ります（例：1d6, 2d6）。結果を整数で返します。"""
    print(f"roll_dice: {dice_spec}")
    if "d6" in dice_spec:
        num_dice = int(dice_spec.split("d")[0])
        total = 0
        for _ in range(num_dice):
            total += random.randint(1, 6)
        print(f"roll_dice_result: {total}")
        return str(total)
    print("roll_dice_fallback: 4")
    return "4"  # fallback mock
