"""
FastAPI智能体聊天应用 - 主入口文件
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api.routes import router as api_router
from api.legacy_routes import router as legacy_router

# 创建FastAPI应用
app = FastAPI(
    title="智能体聊天API",
    description="基于FastAPI的智能体聊天应用，支持会话管理和消息处理",
    version="0.2.1"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")

# 包含API路由
app.include_router(api_router, prefix="/api")

# 包含旧版API路由（为了兼容性）
app.include_router(legacy_router)

# 示例用法
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
