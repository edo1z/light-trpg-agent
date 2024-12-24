from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from tools import roll_dice, update_game_state
from langgraph.graph import StateGraph
from schemas import GameState
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

template = ChatPromptTemplate(
    [
        (
            "system",
            """あなたはTRPGのゲームマスターです。

    プレイヤーと対話しながら、物語を進行させてください。

    以下のツールが利用可能です：
    - roll_dice: サイコロを振る（例：2d6）。戦闘や判定時に使用してください。
    - update_game_state: ゲームの状態（HP・アイテム・ターン）を一括で更新します。

    重要な制約：
    - 状態の更新（HP・アイテム・ターン）は必ず1回のupdate_game_stateで行ってください
    - update_game_stateからのToolMessageを受け取った後は、新たなツール呼び出しを行わないでください
    - roll_diceは連続して使用可能です
    - プレイヤーのアクションごとに必ずターン数を1増やしてください
    - 最初の質問で決まったターン数を超えたらセッションを終了し、必ず物語を要約して表示してください

    ルール：
    1. 最初は以下の順で1つずつ質問してください：
       a) まずジャンルを質問（ファンタジー、SF、ホラーなど）
       b) 次に主人公の名前を質問
       c) 次に世界観と目標を質問
       d) 次にターン数を質問（3〜10の間）
       e) その後、あなたがroll_diceで2d6を振ってHPを決定
       f) 最後に、あなたがroll_diceで1d6を振り、出た目の数だけアイテムをランダムに設定

    2. プレイ開始時と各ターン開始時には必ず以下を表示：
       - 現在のターン数
       - 現在のHP
       - 所持アイテム一覧

    3. プレイヤーのアクションごとにツールを適切に使用してください
    4. 戦闘や判定時は必ずroll_diceを使用してください
    5. 状態の更新は必ずupdate_game_stateを使用してください
    6. セッション終了時は必ず物語を要約して表示してください
    """,
        ),
        ("placeholder", "{messages}"),
    ]
)
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0.7
)
tools = [roll_dice, update_game_state]
llm = llm.bind_tools(tools)
model = template | llm


def game_master(state: GameState):
    response = model.invoke({"messages": state["messages"]})
    return {**state, "messages": [response]}


builder = StateGraph(GameState)
builder.add_node("game_master", game_master)
builder.set_entry_point("game_master")
builder.add_node("tools", ToolNode(tools=tools))
builder.add_conditional_edges(
    "game_master",
    tools_condition,
)
builder.add_edge("tools", "game_master")
graph = builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test-thread"}}

    print("\n=== TRPGセッション開始 ===\n")

    # 初期ストリーム
    for event in graph.stream(
        {
            "messages": [HumanMessage(content="")],
        },
        config=config,
    ):
        if isinstance(event, dict) and "game_master" in event:
            print("\nGM:", event["game_master"]["messages"][-1].content)

    # メインループ
    while True:
        user_input = input("\n> ")
        for event in graph.stream(
            {
                "messages": [HumanMessage(content=user_input)],
            },
            config=config,
        ):
            if isinstance(event, dict) and "game_master" in event:
                print("\nGM:", event["game_master"]["messages"][-1].content)
            else:
                print("\nイベント:", event)
