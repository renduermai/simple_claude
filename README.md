## 痛点
中国用户无法使用Claude，ChatGPT，少数用户会调用API，但只支持单轮对话，无法和AI多轮沟通

## 项目功能
本项目基于Python3.11、langchain、Docker、Redis
可利用API完成本地多轮有记忆的会话
目前提供3个版本：
- 版本 1: 无记忆，本地单轮对话
- 版本 2：有本轮对话记忆（langchain组件实现）。结束运行后，AI不会有历史记忆
- 版本 3: 记忆存在本地（langchain、Docker、Redis实现）。结束运行后，只要输出同样的session_id，就能唤醒所有该id的记忆，记忆文本完整存储在Redis

## 效果展示
### 版本1
本地运行 simple_claude.py 启动后
打开网址：http://localhost:8000/langchainServer/playground/
<img width="2145" height="1362" alt="image" src="https://github.com/user-attachments/assets/1e3bb87d-dc96-4d28-bc94-a87e05af4451" />
该版本内置了私藏提示词，让AI回答尽可能完善，角度丰富，理解问题背后的问题

### 版本2
本地运行 simple_claude_chat.py 启动后
打开网址：http://localhost:8000/langchainServer/playground/
<img width="2145" height="1362" alt="image" src="https://github.com/user-attachments/assets/6aed10d5-2430-42ac-b79c-dc9b64141969" />


### 版本2
本地运行 simple_claude_chat.py 启动后
打开网址：http://localhost:8000/langchainServer/playground/

