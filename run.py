"""
智能点餐助手 启动脚本

启动uvicorn web服务器
"""
import asyncio

import uvicorn


async def main():
    """
    配置并启动 uvicorn 服务器。
    """
    config = uvicorn.Config("api.main:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

