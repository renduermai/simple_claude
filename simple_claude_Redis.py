# 内存持久化多轮对话记忆（版本3）
# 网址
# http://localhost:8000/langchainServer/playground/

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda  # 新增导入

from models import get_ali_model_client

# ========== 1. 带历史占位的提示词链 ==========
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个AI助手，请结合历史对话回答问题。"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

client = get_ali_model_client()
chain = prompt | client | StrOutputParser()

# ========== 2. Redis 历史工厂 ==========
REDIS_URL = "redis://localhost:6379/0"


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=60 * 60 * 24,
    )


chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)


# ========== 修改部分：给链包一层，简化 Playground UI ==========
def to_dict(query: str):
    """接收纯字符串，包装成字典传给后面的链"""
    return {"question": query}


# 这样 Playground 就会认为输入只是一个简单的字符串，显示普通的文本框
final_chain = RunnableLambda(to_dict) | chain_with_history

# ========== 3. FastAPI + LangServe ==========
from fastapi import FastAPI
from langserve import add_routes

app = FastAPI(
    title="基于langchain的服务",
    version="v1.6",
    description="Redis持久化记忆的多轮问答",
)


def per_req_config_modifier(config: dict, request):
    """修改部分：如果没有传 session_id，默认使用 '001'"""
    session_id = request.headers.get("X-Session-Id")

    # 从 config 中获取，或者使用默认值 "001"
    if not session_id:
        session_id = config.get("configurable", {}).get("session_id", "001")

    # 强制写回 config 中
    config.setdefault("configurable", {})["session_id"] = session_id
    return config


# 修改部分：这里传入包装后的 final_chain
add_routes(
    app,
    final_chain,
    path="/langchainServer",
    per_req_config_modifier=per_req_config_modifier,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# 网址
# http://localhost:8000/langchainServer/playground/