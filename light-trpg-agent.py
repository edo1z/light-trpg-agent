from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from tools import roll_dice, update_game_state, summarize_story
from langgraph.graph import StateGraph
from schemas import GameState

load_dotenv()

tools = [roll_dice, update_game_state, summarize_story]

template = ChatPromptTemplate(
    [
        (
            "system",
            """あなたはTRPGのゲームマスターです。
    ジャンルは: ファンタジー
    主人公の名前は: ヒカキン

    プレイヤーと対話しながら、物語を進行させてください。

    以下のツールが利用可能です：
    - roll_dice: サイコロを振る（例：2d6）。戦闘や判定時に使用してください。
    - update_game_state: HP、アイテム、ターン数の更新時に使用してください。
    - summarize_story: 3ターン経過時やセッション終了時に物語を要約します。

    ルール：
    1. プレイヤーのアクションごとにツールを適切に使用してください
    2. 3ターンでセッションは終了します
    3. 戦闘や判定時は必ずroll_diceを使用してください
    4. HPやアイテムの変更時は必ずupdate_game_stateを使用してください
    5. セッション終了時はsummarize_storyで物語を要約してください
    """,
        ),
        ("placeholder", "{messages}"),
    ]
)
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4", temperature=0.7)
model = template | llm


def game_master(state: GameState):
    response = model.invoke({"messages": state["messages"]})
    return {"messages": [response]}


builder = StateGraph(GameState)
builder.add_node("game_master", game_master)
builder.set_entry_point("game_master")
graph = builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test-thread"}}
    while True:
        user_input = input("> ")
        result = graph.invoke(
            {
                "messages": [HumanMessage(content=user_input)],
            },
            config=config,
        )

        print("\nGM:", result["messages"][-1].content)
