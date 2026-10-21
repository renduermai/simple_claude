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
<img width="2145" height="1362" alt="img_v3_0216m_a493c4f6-4609-4460-830a-2df3fe3f95fg" src="https://github.com/user-attachments/assets/0166087e-15c8-408a-960a-0b6700383f7b" />
该版本可以支持多用户会话，只要切换session_id即可，每个用户的会话记忆隔离
但本版本只支持本次程序运行的记忆，程序关闭后，再次启用无上次会话记忆

### 版本3
本地运行 simple_claude_chat.py 启动后
打开网址：http://localhost:8000/langchainServer/playground/
<img width="2145" height="1362" alt="image" src="https://github.com/user-attachments/assets/b0b0ac30-15ed-45d6-8ca9-c10fc1df4378" />
<img width="2145" height="1362" alt="image" src="https://github.com/user-attachments/assets/2df339e7-1d34-4ae2-b6ba-b97d0ae6654b" />

打开 redis 可查看本地存档的问答数据
网址：http://localhost:8001/redis-stack/browser
<img width="2159" height="1301" alt="image" src="https://github.com/user-attachments/assets/be3647a2-2ae9-4fc3-94d4-b480dbdd5684" />

关闭程序后，重新启动
<img width="2145" height="1362" alt="image" src="https://github.com/user-attachments/assets/6687d570-0fb1-40f9-a255-d1d7d150908d" />

## 总结
该项目以极简的方式完成了国外大模型的调用，加上记忆功能后，基本能满足普通用户聊天和记忆的需求，并且可以通过html界面直接交互
不过，本项目的记忆目前是完整保存的，随着聊天内容和文本的增加，每次会话将会消耗越来越多的token，在使用的时候需要注意适用场景
