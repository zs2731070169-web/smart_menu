import logging
import os
from dataclasses import dataclass

import dotenv

from tools.request_tool import get

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


@dataclass
class AMapConfig:
    """
    高德地图工具环境变量配置类
    """
    API_KEY = os.getenv("AMAP_API_KEY", "")  # 高德地图API Key，必须在环境变量中设置
    MERCHANT_LONGITUDE = os.getenv("MERCHANT_LONGITUDE", "")  # 默认商户经度，格式为字符串，例如 "116.397128"
    MERCHANT_LATITUDE = os.getenv("MERCHANT_LATITUDE", "")  # 默认商户纬度，格式为字符串，例如 "39.916527"
    DELIVERY_RADIUS = int(os.getenv("DELIVERY_RADIUS", "3000"))  # 默认配送半径为3000米
    DEFAULT_PATH_MODE = os.getenv("DEFAULT_PATH_MODE", "2")  # 默认路径规划模式为骑行
    PATH_MODE = {
        "0": "driving",  # 驾车
        "1": "walking",  # 步行
        "2": "electrobike",  # 骑行
    }

    def __post_init__(self):
        if not self.API_KEY:
            raise ValueError("AMAP_API_KEY is not set in environment variables.")

    @classmethod
    def get_path_mode(cls, mode: str) -> str:
        """
        获取路径规划模式的编码
        :param mode: 路径规划模式，支持 "driving", "walking", "electrobike"
        :return: 对应的编码字符串
        """
        return cls.PATH_MODE.get(mode, cls.DEFAULT_PATH_MODE)


# 检查和获取配送信息是否有效
def check_delivery_info(address: str, mode: str) -> dict:
    """
    检查和获取配送信息包括距离、预计时间和路径规划步骤
    :param address: 目的地地址字符串
    :param mode: 路径规划模式，支持 "0"（驾车）、"1"（步行）、"2"（骑行），默认为 "2"
    :return: 包含配送信息的字典
    """
    try:
        # 获取地理位置编码信息，包括经纬度和格式化地址
        geocode_info = get_geocode(address)
        if not geocode_info.get("status", False):
            return {
                "status": geocode_info["status"],
                "message": geocode_info.get("message", "获取配送地址失败。")
            }
        longitude = geocode_info["longitude"]
        latitude = geocode_info["latitude"]

        # 获取路径规划信息，包括距离、预计时间和路径规划步骤
        direction_info = get_direction(longitude, latitude, mode or AMapConfig.DEFAULT_PATH_MODE)
        if not direction_info.get("status", False):
            return {
                "status": direction_info["status"],
                "message": direction_info.get("message", "获取配送路线失败。")
            }

        # 需要判断是否在配送范围内，如果不在配送范围内，则返回距离和预计时间，但不返回路径规划步骤
        distance = direction_info.get("distance", "")
        is_range = float(distance) <= AMapConfig.DELIVERY_RADIUS
        if not is_range:
            return {
                "status": is_range,
                "message": "超出配送范围。",
            }

        # 把距离转换为公里，如果距离超过1000米，则转为公里单位，并保留一位小数
        if distance:
            distance = int(distance)
            distance = f"{distance / 1000:.2f}" if distance >= 1000 else distance

        return {
            "status": True,
            "formatted_address": geocode_info["formatted_address"],
            "in_range": is_range,
            "distance": distance,
            "duration": direction_info.get("duration", "")
        }
    except Exception as e:
        logger.error(f"Failed to get delivery information for address '{address}': {e}")
        return {
            "status": False,
            "message": f"An error occurred while fetching delivery information: {e}"
        }


# 获取高德地理位置编码
def get_geocode(address: str) -> dict:
    """
    获取高德地理位置编码
    :param address: 地址字符串
    :return: 包含经纬度信息的字典
    """
    try:
        if not address:
            raise ValueError("Address must be provided.")

        geo_data = get(
            url="https://restapi.amap.com/v3/geocode/geo?parameters",
            params={
                "key": AMapConfig.API_KEY,
                "address": address.strip(),
                "output": "JSON"
            }
        )

        # 返回值为 0 或 1，0 表示请求失败；1 表示请求成功。
        geo_data["status"] = int(geo_data.get("status", 0))
        if geo_data["status"] != 1:
            return {
                "status": False,
                "message": f"Failed to get geocode for address '{address}': {geo_data.get('info', 'Unknown error')}"
            }

        # geocodes 是一个列表，包含一个或多个地理编码结果。我们取第一个最精确的结果
        geocodes = geo_data.get("geocodes", [{}])[0]
        # location 字段包含经纬度信息，格式为 "经度,纬度"，我们需要分割它来获取单独的经度和纬度
        location = geocodes.get("location", "").split(",")
        return {
            "status": True,
            "formatted_address": geocodes.get("formatted_address", ""),
            "longitude": location[0] if geo_data.get("geocodes") else "",
            "latitude": location[1] if geo_data.get("geocodes") else ""
        }
    except Exception as e:
        logger.error(f"Failed to get geocode for address '{address}': {e}")
        raise e


def get_direction(longitude: str, latitude: str, mode: str) -> dict:
    """
    获取高德地图路径规划
    :param longitude: 目的地经度
    :param latitude: 目的地纬度
    :return: 包含路径规划信息的字典
    """
    try:
        if not longitude or not latitude:
            raise ValueError("Both longitude and latitude must be provided.")

        if mode not in AMapConfig.PATH_MODE:
            raise ValueError(f"Invalid mode '{mode}'. Supported modes are: {', '.join(AMapConfig.PATH_MODE.keys())}")

        direction_data = get(
            url=f"https://restapi.amap.com/v5/direction/{AMapConfig.get_path_mode(mode)}?parameters",
            params={
                "key": AMapConfig.API_KEY,
                "origin": f"{AMapConfig.MERCHANT_LONGITUDE},{AMapConfig.MERCHANT_LATITUDE}",
                "destination": f"{longitude},{latitude}",
                "output": "JSON"
            }
        )

        # 返回值为 0 或 1，0 表示请求失败；1 表示请求成功。
        direction_data["status"] = int(direction_data.get("status", 0))
        if direction_data["status"] != 1:
            return {
                "status": False,
                "message": f"Failed to get direction for destination '{longitude},{latitude}': {direction_data.get('info', 'Unknown error')}"
            }

        # route 字段包含路径规划结果，paths 是一个列表，包含一个或多个路径规划方案。我们取第一个最优的方案
        direction = direction_data.get("route", {}).get("paths", [{}])[0]

        # 驾车模式
        if mode == "0":
            return {
                "status": True,
                "distance": direction.get("distance", ""),  # 距离，单位为米
                # "restriction": direction["restriction"],  # 驾车路径规划限制信息，例如 "限行"、"高速"等
                # "steps": direction.get("steps", []),  # 路径规划步骤列表，每个步骤包含具体的行驶指引信息
            }
        # 步行模式和电动车模式
        elif mode:
            # 步行或电动车路径规划的预计时间
            duration = direction.get("cost", {}).get("duration", "") if mode == "1" else direction.get("duration", "")
            # 路径的预计时间，单位为秒，如果是<60，则转为分钟，如果是>=60，则转为小时+分钟
            cost_time = 0
            if duration:
                duration = int(duration)
                if duration < 3600:
                    cost_time = duration // 60
                else:
                    hours = duration // 3600
                    minutes = duration % 3600 // 60
                    cost_time = f"{hours}.{minutes}" if minutes else hours

            return {
                "status": True,
                "distance": direction.get("distance", ""),  # 距离，单位为米
                "duration": f"{cost_time} {"分钟" if duration < 3600 else "小时"}",  # 预计时间，单位为小时/分钟
                # "steps": direction.get("steps", []),  # 路径规划步骤列表，每个步骤包含具体的行驶指引信息
            }
    except Exception as e:
        logger.error(f"Failed to get direction for '{longitude},{latitude}': {e}")
        raise


if __name__ == '__main__':
    # # 示例地址
    # address = "天安门"
    # geocode_info = get_geocode(address)
    # print(f"Geocode info for '{address}': {geocode_info}")
    #
    # # 示例路径规划
    # longitude = geocode_info["longitude"]
    # latitude = geocode_info["latitude"]
    # direction_info = get_direction(longitude, latitude, mode="2")
    # print(f"Direction info for destination '{longitude},{latitude}': {direction_info}")
    #
    # # 示例地址
    # address = "北京人民大会堂"
    # geocode_info = get_geocode(address)
    # print(f"Geocode info for '{address}': {geocode_info}")
    #
    # # 示例路径规划
    # longitude = geocode_info["longitude"]
    # latitude = geocode_info["latitude"]
    # direction_info = get_direction(longitude, latitude, mode="1")
    # print(f"Direction info for destination '{longitude},{latitude}': {direction_info}")
    #
    # # 示例地址
    # address = "北京市海淀区人民法院"
    # geocode_info = get_geocode(address)
    # print(f"Geocode info for '{address}': {geocode_info}")
    #
    # # 示例路径规划
    # longitude = geocode_info["longitude"]
    # latitude = geocode_info["latitude"]
    # direction_info = get_direction(longitude, latitude, mode="0")
    # print(f"Direction info for destination '{longitude},{latitude}': {direction_info}")

    # 示例地址
    address = "北京市海淀区人民法院"
    delivery_info = check_delivery_info(address, mode="2")
    print(
        f"配送距离：{delivery_info.get('distance', '未知')} {'公里' if 'distance' in delivery_info and isinstance(delivery_info['distance'], str) and '.' in delivery_info['distance'] else '米'}")
    print(f"是否在配送范围内：{'是' if delivery_info.get('in_range') else '否'}")
    print(f"预计配送时间：{delivery_info.get('duration', '未知')}")
    print(f"出发地：{AMapConfig.MERCHANT_LONGITUDE},{AMapConfig.MERCHANT_LATITUDE}")
    print(f"目的地：{delivery_info.get('formatted_address', '未知')}")
