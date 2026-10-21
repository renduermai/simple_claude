
# 内存持久化多轮对话记忆（仅本次对话，版本2）
# 网址
# http://localhost:8000/langchainServer/playground/

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_community.chat_message_histories import ChatMessageHistory

from models import get_ali_model_client

# ========== 1. 带历史占位的提示词链 ==========
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template("你是一个AI助手"),
        # 作用就是在提示词中插入一段历史消息
        MessagesPlaceholder(variable_name="messages"),
        # 接收当前用户的问题 (必须加，否则不知道当前问的是什么)
        ("human", "{question}"),
    ]
)

client = get_ali_model_client()
parser = StrOutputParser()
chain = prompt | client | parser

# ========== 2. 内存历史工厂：使用字典模拟数据库 ==========
# 这里的 store 就是一个全局字典，用来在程序运行期间保存各个 session 的聊天记录
store = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    """按 session_id 隔离，支持多用户"""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


# 关键：使用 RunnableWithMessageHistory，它会自动帮你完成原来 while 循环里手动 add_message 的动作
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",  # 本轮输入字段名
    history_messages_key="messages",  # 历史占位名，与上面 MessagesPlaceholder 一致
)


# ========== 修改部分：给链包一层，简化 Playground UI ==========
def to_dict(query: str):
    """接收纯字符串，包装成字典传给后面的链，这样网页上就不会显示复杂的 Message 结构"""
    return {"question": query}


# 这样 Playground 就会认为输入只是一个简单的字符串，显示普通的文本框
final_chain = RunnableLambda(to_dict) | chain_with_history

# ========== 3. FastAPI + LangServe ==========
from fastapi import FastAPI
from langserve import add_routes

app = FastAPI(
    title="基于langchain的服务(内存版)",
    version="v1.6",
    description="内存持久化记忆的多轮问答",
)


def per_req_config_modifier(config: dict, request):
    """修改部分：如果没有传 session_id，默认使用 '001'"""
    session_id = request.headers.get("X-Session-Id")

    if not session_id:
        session_id = config.get("configurable", {}).get("session_id", "001")

    config.setdefault("configurable", {})["session_id"] = session_id
    return config


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