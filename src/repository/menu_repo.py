import logging

import mysql

from tools.db_tool import DBConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_menus_repo() -> list[dict]:
    """
    获取所有菜单项
    :return: 菜单项列表
    """
    try:
        with DBConnection() as db:
            # 执行查询语句获取所有菜单项
            db.cursor.execute(
                "SELECT id, dish_name, price, description, category, spice_level, flavor, "
                "main_ingredients, cooking_method, is_vegetarian, allergens, is_available "
                "FROM menu_items WHERE is_available = TRUE"
            )
            menus = db.cursor.fetchall()

            if not menus:
                logger.warning("No menus found in the database.")
                return []

            logger.info("Successfully fetched all menus.")
            return menus

    except mysql.connector.Error as err:
        logger.error(f"Error fetching menus: {err}")
        return []
