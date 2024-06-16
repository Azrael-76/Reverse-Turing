from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from scripts.DoubaoLite4k import chat_with_Doubao
from scripts.generate_speech_fishspeech import generate_speech

app = FastAPI()

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的方法
    allow_headers=["*"],  # 允许的头部
)


class ChatRequest(BaseModel):
    message: str
    user_id: str  # 可用于处理上下文对话


@app.get("/")
def read_root():
    return {"Hello": "World"}


class Message(BaseModel):
    message: str
    character: str


@app.post("/message")
async def receive_message(message: Message):
    # 这里可以添加处理消息的逻辑
    print(
        "##############################################  Received message:",
        message.message,
    )
    try:
        # result = ernie(message.message, message.character) # 调用百度ERNIE模型
        result = chat_with_Doubao(
            message.message, message.character
        )  # 调用DoubaoLite模型
        print("AI response:", result)

        # 生成语音
        audio_file_path = generate_speech(result)

        return {
            "status": "Message received successfully",
            "result": result,
            "audio_file": audio_file_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(chat_request: ChatRequest):
    """
    接收用户的输入，返回聊天机器人的回复。
    """
    print("成功接收用户输入：", chat_request.message)
    # user_input = chat_request.message
    # user_id = chat_request.user_id
    try:
        # response = get_response(user_input, user_id)
        response = "这是一个测试回复"
        return {"message": response}
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-prompt")
def get_prompt():
    """
    返回一个预设的提示信息。
    """
    # 这里可以根据实际情况返回不同的提示信息
    return {"prompt": "请输入您的图像生成描述"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
