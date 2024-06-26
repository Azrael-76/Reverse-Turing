from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import sys

# 添加项目根目录到sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from scripts.DoubaoLite4k import chat_with_Doubao
from scripts.generate_speech_fishspeech import generate_speech
from rag_service import RAGService  # 导入RAG服务

app = FastAPI()

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的方法
    allow_headers=["*"],  # 允许的头部
)


class Message(BaseModel):
    query: str
    character: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/message")
async def receive_message(message: Message):
    try:
        # 这里可以添加处理消息的逻辑
        print("Received query:", message.query)
        print("Received character:", message.character)
        # 添加retrieved_docs
        retrieved_docs = "等待检索..."
        print("Retrieved docs:", retrieved_docs)

        # 调用RAG服务进行检索
        print("Initializing RAG service...")
        rag_service = RAGService()
        print("RAG service initialized successfully")
        retrieved_docs = rag_service.retrieve(message.character + message.query)
        print("Retrieved docs:", retrieved_docs)
        combined_input = (
            message.query + " " + " ".join(retrieved_docs) + " " + message.character
        )

        # 调用DoubaoLite模型
        print("Calling DoubaoLite model...")
        result = chat_with_Doubao(
            message.query,
            retrieved_docs,
        )
        print("AI response:", result)

        # 生成语音
        # audio_file_path = generate_speech(result)

        return {
            "status": "Message received successfully",
            "result": result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_prompt")
def get_prompt():
    """
    返回一个预设的提示信息。
    """
    # 这里可以根据实际情况返回不同的提示信息
    return {"prompt": "请输入您的图像生成描述"}


@app.post("/question")
async def get_question(request: Request):
    try:
        question_type = await request.body()  # 获取原始请求体内容
        question_type = question_type.decode("utf-8")  # 将字节流解码为字符串
        print("Received question_type:", question_type)  # 打印接收到的 question_type
        message = Message(query="根据设定随机生成一个问题", character=question_type)
        result = chat_with_Doubao(
            message.query,
            message.character,
        )
        print("AI response:", result)

        # 生成语音
        # audio_file_path = generate_speech(result)

        return {
            "status": "Message received successfully",
            "result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
