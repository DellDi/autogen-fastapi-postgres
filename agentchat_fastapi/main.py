"""
FastAPI智能体聊天应用 - 主入口文件
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# 确保安装了greenlet
try:
    import greenlet
except ImportError:
    import subprocess
    print("安装greenlet依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "greenlet"])
    import greenlet

# 导入数据库引擎和相关组件
from agentchat_fastapi.api.database import engine, get_db

# 创建应用启动和关闭的上下文管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行
    print("应用启动，初始化数据库连接...")
    # 应用运行中...
    yield
    # 应用关闭时执行
    print("应用关闭，清理资源...")
    await engine.dispose()

# 创建FastAPI应用
app = FastAPI(
    title="智能体聊天API",
    description="基于FastAPI的智能体聊天应用，支持会话管理和消息处理",
    version="0.2.5",
    lifespan=lifespan
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

# 导入路由
from agentchat_fastapi.api.routes import router as api_router

# 包含API路由
app.include_router(api_router, prefix="/api")

# 示例用法
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
