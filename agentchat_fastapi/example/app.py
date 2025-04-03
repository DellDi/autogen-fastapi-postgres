"""
示例应用 - 聊天界面示例
"""
import os
import sys
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 添加项目根目录到系统路径，以便导入api模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.legacy_routes import router as legacy_router

app = FastAPI(
    title="智能体聊天示例",
    description="基于FastAPI的智能体聊天示例应用",
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

# 包含旧版API路由（为了兼容性）
app.include_router(legacy_router)

@app.get("/")
async def root():
    """提供聊天界面HTML文件"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "app_agent.html"))

# 示例用法
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
