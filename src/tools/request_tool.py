# 构建http会话，支持http和https协议
import json
import logging

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get(url: str, **kwargs):
    """
    构建http get请求操作
    :param url:
    :param kwargs:
    :return:
    """
    return request("GET", url, **kwargs)


def post(url: str, **kwargs):
    """
    构建http post请求操作
    :param url:
    :param kwargs:
    :return:
    """
    return request("POST", url, **kwargs)


def request(method: str, url: str, **kwargs):
    """
    构建http请求操作
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    try:
        session = build_session()
        # 发送http请求，支持http和https协议
        return http_request(session, method, url, **kwargs)
    # 如果不支持SSL协议，就降级处理
    except requests.exceptions.SSLError as e:
        logger.warning(f"SSL error occurred: {e}. Retrying without SSL verification.")
        session = Session()
        return http_request(session, method, url, **kwargs)
    # 反序列化异常
    except json.decoder.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        raise e
    # 兜底异常
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e


def build_session(max_retries: int = 3, backoff_factor: float = 1):
    """
    构建一个支持重试机制的HTTP会话，适用于http和https协议
    :param max_retries:
    :param backoff_factor:
    :return:
    """
    retry = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,  # 重试间隔时间的指数增长因子，例如：1, 2, 4, 8秒等
        status_forcelist=[429, 500, 502, 503, 504],
        # 需要重试的HTTP状态码列表，例如：429（请求过多）、500（服务器错误）、502（错误网关）、503（服务不可用）和504（网关超时）等
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)  # 将适配器注册到http协议
    session.mount('https://', adapter)  # 将适配器注册到https协议
    return session


def http_request(session: Session, method: str, url: str, timeout: int = 10, **kwargs):
    try:
        response = session.request(
            method,
            url,
            timeout=timeout,
            **kwargs
        )
        # 检查响应状态码，如果不是200-299范围内的状态码，则抛出HTTPError异常
        response.raise_for_status()
        return response.json()
    # 请求失败异常
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed after retrying without SSL verification: {e}")
        raise e
