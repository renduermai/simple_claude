# 版本1（保持langchain构造，只是UI升级）
# 无记忆、无工具、可优化问题
import time
import threading
from langgraph.checkpoint.memory import MemorySaver
from models import get_ali_model_client
from langchain.agents import create_agent
from langchain_core.tools import tool
import datetime

@tool
def get_current_time():
    """获取当前时间"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(current_time)
    return current_time

@tool
def get_date():
    """获取今天日期"""
    return datetime.datetime.now().strftime("%Y-%m-%d")


import webbrowser
@tool
def open_browser(url, browser_name=None):
    """获取浏览器，打开网站"""
    if browser_name:
        browser = webbrowser.get(browser_name)
    else:
        browser = webbrowser

    # 打开浏览器并导航到指定url
    browser.open(url)


import socket
@tool
def get_local_ip():
    """获取本地IP地址"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]



import winsound;
@tool
def ding():
    """让电脑叮一声"""
    winsound.Beep(1000, 200)

import subprocess
@tool
def open_calculator():
    """打开计算器"""
    try:
        subprocess.Popen(["calc.exe"])
        return "打开计算器成功"
    except Exception as e:
        print(e)
        return f"打开计算器失败,{e}"

@tool
def open_browser(url):
    """打开浏览器并导航到指定url"""
    try:
        webbrowser.open(url)
        return "已打开浏览器并导航到指定url"
    except Exception as e:
        print(e)
        return f"打开浏览器失败,{e}"

system_prompt="用中文回答"
model = get_ali_model_client()

tools = [get_current_time, get_date, open_browser, get_local_ip, ding, open_calculator, open_browser]


agent =create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,

)


# ==================== 新增：历史快照（避免 Gradio 认为对象未变而跳过刷新） ====================
def _snapshot(history):
    """浅拷贝历史，避免 Gradio 因对象引用相同而跳过刷新。"""
    return [dict(m) for m in history]


# 通过前端输入问题
# 与前端交互处理LLM响应
def process_llm_response(query, show_history):
    """占位 → 动态计时 → 最终结果，全流程流式 yield。"""
    query = (query or "").strip()
    if not query:
        yield show_history, ""
        return

    show_history = show_history or []
    new_history = show_history + [
        {"role": "user", "content": query},
        {"role": "assistant", "content": "⏳ 正在查询大模型... 0.0s"}
    ]
    # 第一次立刻写入（同时清空输入框）
    yield _snapshot(new_history), ""

    result = {}
    start = time.perf_counter()

    def worker():
        try:
            # 使用Agent处理查询
            response = agent.invoke(
                input={"messages": [{"role": "user", "content": query}]},
                config={"configurable": {"thread_id": "user_1"}}
            )
            print(f"LLM输出: {response}")

            # 正确提取回答内容 - 只显示output部分
            if isinstance(response, dict) and 'messages' in response:
                result["text"] = response["messages"][-1].content
            else:
                result["text"] = str(response)
        except Exception as e:
            result["error"] = str(e)

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    # 主线程轮询，实时刷新占位消息里的秒数
    while t.is_alive():
        elapsed = time.perf_counter() - start
        current = _snapshot(new_history)
        current[-1]["content"] = f"⏳ 正在查询大模型... {elapsed:.1f}s"
        yield current, ""
        time.sleep(0.2)

    t.join()
    elapsed = time.perf_counter() - start

    if "error" in result:
        response_text = f"请求出错: {result['error']}"
        print(response_text)
    else:
        response_text = result.get("text", "")
        if not isinstance(response_text, str):
            response_text = str(response_text)
        if not response_text.strip():
            response_text = "（模型未返回内容）"
        response_text = f"{response_text}"

    # 把“正在查询...”那条消息的内容替换为最终结果
    new_history[-1]["content"] = response_text
    yield new_history, ""


# 前端界面展示 (Gradio)
import gradio as gr

with gr.Blocks(title="simple Claude v1") as demo:
    gr.HTML('<center><h1>simple Claude v1</h1></center>')

    with gr.Row():
        with gr.Column(scale=10):
            # 【修改点】删除了 type="messages" 参数，让它根据当前版本自适应
            chatbot = gr.Chatbot(height=650)

    with gr.Row():
        msg = gr.Textbox(
            show_label=False,      # 不显示标签
            container=False,       # 去掉外层留白，更紧凑
            placeholder="该版本无记忆功能，您想了解什么呢？（回车或点“提交”均可）",
            scale=1,
        )

        submit_btn = gr.Button(
            "提交",
            size="sm",
            variant="primary",
            scale=0,
            min_width=64,
        )

    with gr.Row():
        examples = gr.Examples(
            examples=[
                '现在几点了',
                '今天几月几号',
                '帮我打开计算器',
                'ding一声',
                '帮我访问淘宝网',
                '本机IP是多少'
            ],
            inputs=[msg]
        )

    clear = gr.ClearButton([chatbot, msg])

    # 绑定提交事件
    msg.submit(process_llm_response, inputs=[msg, chatbot], outputs=[chatbot, msg])
    # 按钮提交（等价于回车；yield 里已把 msg 置空）
    submit_btn.click(process_llm_response, inputs=[msg, chatbot], outputs=[chatbot, msg])

if __name__ == '__main__':
    # 启动服务，端口设置为7779
    demo.launch(server_port=7779)