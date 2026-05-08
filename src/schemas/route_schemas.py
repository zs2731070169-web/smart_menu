import os

import dotenv
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class MenuResp(BaseModel):
    menus: list[dict] = Field(default_factory=list, description="菜单项列表")
    status: bool = Field(default=False,
                         description="查询状态，True表示成功查询到菜单项，False表示未查询到菜单项或查询失败")
    message: str = Field(default="", description="查询结果的消息描述")
    count: int = Field(default=0, description="查询到的菜单项数量")


class DeliveryResp(BaseModel):
    message: str = Field(default="", description="配送信息获取结果的消息描述")
    status: bool
    in_range: bool = Field(default=False, description="配送地址是否在配送范围内")
    distance: str = Field(default="0", description="配送距离，单位为公里")
    formatted_address: str = Field(default="", description="配送地址的格式化字符串")
    duration: str = Field(default="", description="配送预计时间，格式为小时和分钟，例如 '1小时30分钟'")


class DeliveryReq(BaseModel):
    address: str = Field(default="", description="配送地址")  # 配送地址
    mode: str = Field(os.getenv("DEFAULT_PATH_MODE"), description="配送方式")  # 默认骑行模式

class ChatResp(BaseModel):
    status: bool
    message: dict = Field(default=dict, description="聊天回复消息")
