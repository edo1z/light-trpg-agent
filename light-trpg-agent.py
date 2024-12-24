from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from tools import roll_dice, update_game_state, summarize_story
from langgraph.graph import StateGraph
from schemas import GameState

# .envファイルの読み込み
load_dotenv()

# OpenAI GPT-4モデルの初期化
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4", temperature=0.7)

# プロンプトテンプレートの作成
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたはTRPGのゲームマスターです。
    ジャンルは: {genre}
    主人公の名前は: {protagonist}

    プレイヤーと対話しながら、物語を進行させてください。

    以下のツールが利用可能です：
    - roll_dice: サイコロを振る（例：2d6）。戦闘や判定時に使用してください。
    - update_game_state: HP、アイテム、ターン数の更新時に使用してください。
    - summarize_story: 3ターン経過時やセッション終了時に物語を要約します。

    現在の状態：
    - HP: {game_state.player_hp}
    - アイテム: {game_state.items}
    - ターン: {game_state.turn_count}/{game_state.max_turns}
    - 世界観: {game_state.world_intro}

    ルール：
    1. プレイヤーのアクションごとにツールを適切に使用してください
    2. 3ターンでセッションは終了します
    3. 戦闘や判定時は必ずroll_diceを使用してください
    4. HPやアイテムの変更時は必ずupdate_game_stateを使用してください
    5. セッション終了時はsummarize_storyで物語を要約してください
    """,
        ),
        ("human", "{input}"),
    ]
)

# ツールの設定
tools = [roll_dice, update_game_state, summarize_story]


# GameMasterノードの定義
def game_master(inputs):
    # AIの応答を取得
    response = llm.invoke(
        prompt.format(
            game_state=inputs["game_state"],
            input=inputs["user_input"],
            genre=inputs.get("genre", "ファンタジー"),
            protagonist=inputs.get("protagonist", "勇者"),
        )
    )

    # GameStateの更新
    inputs["game_state"].story_log.append(response.content)
    inputs["game_state"].current_status = "IN_PROGRESS"

    return {
        "response": response.content,
        "game_state": inputs["game_state"],  # 更新したGameStateを返す
    }


# グラフの作成
builder = StateGraph(GameState)
builder.add_node("game_master", game_master)
builder.set_entry_point("game_master")
graph = builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    # 初期ゲーム状態の作成
    initial_state = GameState(
        world_intro="あなたは小さな村の冒険者です。村の近くに現れた魔物を退治することになりました。",
        player_hp=10,
        items=["短剣", "回復薬"],
        current_status="START",
    )

    # 初期設定
    config = {"configurable": {"thread_id": "test-thread"}}

    print("=== TRPGセッション開始 ===")
    print(initial_state.world_intro)
    print("あなたはどうしますか？")

    # チャットループ
    while True:
        user_input = input("> ")
        if user_input.lower() in ["quit", "exit", "終了"]:
            break

        result = graph.invoke(
            {
                "game_state": initial_state,
                "user_input": user_input,
                "genre": "ファンタジー",
                "protagonist": "冒険者",
            },
            config=config,
        )

        print("\nGM:", result["response"])

        if initial_state.current_status == "END":
            print("\n=== セッション終了 ===")
            break
