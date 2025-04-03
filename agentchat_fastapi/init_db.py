#!/usr/bin/env python
"""
数据库初始化脚本

用于在服务器环境中执行以下操作：
1. 检查数据库是否存在，不存在则创建
2. 执行数据库迁移脚本
"""

import os
import sys
import asyncio
import logging
from typing import Optional
import subprocess
import argparse
from urllib.parse import urlparse

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("db_init")

def parse_database_url(url: str) -> tuple:
    """解析数据库连接URL"""
    parsed = urlparse(url)
    username = parsed.username
    password = parsed.password
    database = parsed.path[1:]  # 去掉开头的 '/'
    hostname = parsed.hostname
    port = parsed.port or 5432
    
    return hostname, port, username, password, database

def check_database_exists(hostname: str, port: int, username: str, 
                         password: str, database: str) -> bool:
    """检查数据库是否存在"""
    try:
        # 连接到默认的postgres数据库
        conn = psycopg2.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        return exists
    except Exception as e:
        logger.error(f"检查数据库时出错: {e}")
        return False

def create_database(hostname: str, port: int, username: str, 
                   password: str, database: str) -> bool:
    """创建数据库"""
    try:
        # 连接到默认的postgres数据库
        conn = psycopg2.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE {database}")
        
        cursor.close()
        conn.close()
        logger.info(f"数据库 '{database}' 创建成功")
        return True
    except Exception as e:
        logger.error(f"创建数据库时出错: {e}")
        return False

def run_migrations(project_dir: str) -> bool:
    """运行数据库迁移"""
    try:
        logger.info("执行数据库迁移...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"迁移输出:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"迁移警告:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"执行迁移时出错: {e}")
        logger.error(f"错误输出: {e.stderr}")
        return False

async def main(env_file: Optional[str] = None):
    """主函数"""
    # 加载环境变量
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()
    
    # 获取数据库URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("未找到DATABASE_URL环境变量")
        return False
    
    # 解析数据库URL
    hostname, port, username, password, database = parse_database_url(database_url)
    logger.info(f"数据库信息: 主机={hostname}, 端口={port}, 用户={username}, 数据库={database}")
    
    # 检查数据库是否存在
    if check_database_exists(hostname, port, username, password, database):
        logger.info(f"数据库 '{database}' 已存在")
    else:
        logger.info(f"数据库 '{database}' 不存在，正在创建...")
        if not create_database(hostname, port, username, password, database):
            logger.error("数据库创建失败，退出")
            return False
    
    # 获取项目目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 运行迁移
    if run_migrations(project_dir):
        logger.info("数据库初始化完成")
        return True
    else:
        logger.error("数据库迁移失败")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument("--env", help="环境变量文件路径", default=None)
    args = parser.parse_args()
    
    success = asyncio.run(main(args.env))
    sys.exit(0 if success else 1)
