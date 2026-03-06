/*
 Navicat Premium Dump SQL

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 90500 (9.5.0)
 Source Host           : localhost:3306
 Source Schema         : smart_menu

 Target Server Type    : MySQL
 Target Server Version : 90500 (9.5.0)
 File Encoding         : 65001

 Date: 06/03/2026 18:52:46
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for menu_items
-- ----------------------------
DROP TABLE IF EXISTS `menu_items`;
CREATE TABLE `menu_items`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '菜品ID，主键自增',
  `dish_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜品名称',
  `price` decimal(8, 2) NOT NULL COMMENT '价格（元）',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '菜品描述',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜品分类',
  `spice_level` tinyint NULL DEFAULT 0 COMMENT '辣度等级：0-不辣，1-微辣，2-中辣，3-重辣',
  `flavor` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '口味特点',
  `main_ingredients` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '主要食材，多个食材用逗号分隔',
  `cooking_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '烹饪方法',
  `is_vegetarian` tinyint(1) NULL DEFAULT 0 COMMENT '是否素食：0-否，1-是',
  `allergens` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '过敏原信息，多个过敏原用逗号分隔',
  `is_available` tinyint(1) NULL DEFAULT 1 COMMENT '是否可供应：0-不可用，1-可用',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_category`(`category` ASC) USING BTREE,
  INDEX `idx_is_available`(`is_available` ASC) USING BTREE,
  INDEX `idx_is_vegetarian`(`is_vegetarian` ASC) USING BTREE,
  INDEX `idx_price`(`price` ASC) USING BTREE,
  INDEX `idx_spice_level`(`spice_level` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '菜单表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of menu_items
-- ----------------------------
INSERT INTO `menu_items` VALUES (1, '宫保鸡丁', 28.00, '经典川菜，鸡肉丁配花生米，酸甜微辣，口感丰富', '川菜', 2, '酸甜微辣', '鸡胸肉,花生米,青椒,红椒,葱段', '爆炒', 0, '花生,可能含有麸质', 1, '2025-07-01 10:45:02', '2025-07-01 10:45:02');
INSERT INTO `menu_items` VALUES (2, '麻婆豆腐', 18.00, '四川传统名菜，嫩滑豆腐配麻辣汤汁，下饭神器', '川菜', 3, '麻辣鲜香', '嫩豆腐,牛肉末,豆瓣酱,花椒', '烧炒', 0, '大豆,可能含有麸质', 1, '2025-07-01 10:45:02', '2025-09-26 14:43:58');
INSERT INTO `menu_items` VALUES (3, '清炒时蔬', 15.00, '新鲜时令蔬菜清炒，营养健康，口感清爽', '素食', 0, '清淡爽口', '时令蔬菜,蒜蓉', '清炒', 1, '', 1, '2025-07-01 10:45:02', '2025-09-26 14:53:33');
INSERT INTO `menu_items` VALUES (6, '东坡肉', 88.00, '选用五花肉经长时间慢炖，色泽红亮，肥而不腻，入口即化，是杭帮菜的经典之作。', '浙菜', 0, '醇厚咸甜', '五花肉、黄酒、老抽、冰糖', '红烧', 0, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (7, '夫妻肺片', 58.00, '精选牛肉与牛杂，配以特制红油和花生，麻辣鲜香，口感丰富，是成都街头的灵魂小吃。', '川菜', 3, '麻辣鲜香', '牛肉、牛杂、花生、芝麻', '凉拌', 0, '花生、芝麻', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (8, '西湖醋鱼', 72.00, '选用西湖草鱼，以糖醋汁浇淋，鱼肉鲜嫩，酸甜适口，是浙菜代表名菜。', '浙菜', 0, '酸甜鲜美', '草鱼、米醋、白糖、姜', '清蒸', 0, '鱼', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (9, '葱爆羊肉', 68.00, '精选内蒙古羔羊肉，大火爆炒，配以葱段，羊肉鲜嫩无膻味，葱香四溢。', '鲁菜', 1, '葱香咸鲜', '羊肉、大葱、蒜', '爆炒', 0, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (10, '粤式白切鸡', 78.00, '选用本地走地鸡，以浸煮方式保留鸡肉原汁原味，皮脆肉嫩，配以姜葱酱蘸食。', '粤菜', 0, '清淡鲜甜', '走地鸡、姜、葱、盐', '白煮', 0, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (11, '剁椒鱼头', 88.00, '选用新鲜花鲢鱼头，铺满自制剁椒蒸制，鱼肉鲜嫩，剁椒红艳，咸辣开胃。', '湘菜', 3, '咸辣鲜香', '花鲢鱼头、剁椒、蒜', '清蒸', 0, '鱼', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (12, '北京烤鸭卷饼', 128.00, '选用正宗北京鸭，经果木烤制，鸭皮酥脆，配以薄饼、黄瓜、葱段和甜面酱食用。', '京菜', 0, '醇香咸甜', '北京鸭、薄饼、黄瓜、大葱、甜面酱', '烤制', 0, '麸质', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (13, '冰糖莲藕排骨汤', 68.00, '选用湖北特产莲藕，与猪排骨同炖，加入冰糖提鲜，藕香浓郁，汤色乳白，滋补养颜。', '湘菜', 0, '清甜醇香', '莲藕、猪排骨、冰糖、枸杞', '炖煮', 0, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (14, '扬州炒饭', 45.00, '精选隔夜米饭，配以虾仁、叉烧、鸡蛋、葱花大火翻炒，粒粒分明，色泽金黄，鲜香四溢。', '淮扬菜', 0, '鲜香咸美', '米饭、虾仁、叉烧、鸡蛋、葱', '炒制', 0, '虾、蛋', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (15, '糖醋里脊', 65.00, '精选猪里脊肉，裹以薄芡炸至金黄，浇以特制糖醋汁，外酥里嫩，酸甜可口。', '鲁菜', 0, '酸甜可口', '猪里脊、白糖、米醋、番茄酱', '油炸', 0, '麸质', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (16, '蒙古烤肉拼盘', 138.00, '精选牛羊肉混拼，撒以孜然、辣椒粉，炭火烤制，肉质鲜嫩多汁，草原风味十足。', '蒙古菜', 2, '孜然香辣', '牛肉、羊肉、孜然、辣椒', '烤制', 0, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (17, '云南汽锅鸡', 98.00, '采用特制汽锅蒸制，天麻、枸杞与土鸡同蒸，汤汁清澈鲜美，鸡肉软糯，滋补养生。', '云南菜', 0, '清鲜甘甜', '土鸡、天麻、枸杞、姜', '汽蒸', 0, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (18, '麻酱豆腐丝', 32.00, '选用内酯豆腐切丝，淋上芝麻酱、蒜泥、香醋调制的酱汁，口感细腻，麻香浓郁，清爽开胃。', '素食', 0, '麻香醇厚', '内酯豆腐、芝麻酱、蒜、香醋', '凉拌', 1, '芝麻、大豆', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (19, '酸菜白肉锅', 88.00, '东北特色锅物，酸菜与五花肉同煮，酸香开胃，五花肉片薄嫩滑，汤底酸鲜，配以宽粉更美味。', '东北菜', 0, '酸鲜咸香', '五花肉、酸菜、宽粉、蒜', '炖煮', 0, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (20, '姜葱焗蟹', 168.00, '选用鲜活梭子蟹，以姜葱大火爆炒焗制，蟹肉鲜甜，姜葱香气四溢，是粤菜中的海鲜经典。', '粤菜', 1, '姜葱咸鲜', '梭子蟹、姜、葱、蒜', '焗炒', 0, '蟹、贝类', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (21, '酸辣土豆丝', 28.00, '精选本地黄心土豆，切丝爆炒，加入干辣椒和白醋调味，脆爽酸辣，是家常下饭菜首选。', '家常菜', 2, '酸辣爽脆', '土豆、干辣椒、蒜、白醋', '爆炒', 1, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (22, '蜜汁叉烧', 75.00, '选用梅花猪肉腌制入味，经炭炉烤制，表面蜜汁光亮，肉质嫩滑，甜咸交织，是粤式烧味的代表。', '粤菜', 0, '蜜甜咸香', '梅花猪肉、蜂蜜、叉烧酱、南乳', '烤制', 0, '麸质、大豆', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (23, '水煮牛肉', 78.00, '选用嫩牛里脊，以特制红汤烫熟，铺上大量干辣椒和花椒，浇热油激香，麻辣霸道，是川菜经典。', '川菜', 3, '麻辣鲜烫', '牛里脊、干辣椒、花椒、豆芽', '水煮', 0, '无', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (24, '清汤羊肉面', 52.00, '选用新疆羔羊肉，以香料慢炖清汤，配以手工拉面，汤底清澈鲜美，羊肉软烂，面条筋道。', '西北菜', 0, '清鲜醇厚', '羔羊肉、手工面、香料、葱', '炖煮', 0, '麸质', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');
INSERT INTO `menu_items` VALUES (25, '三杯鸡', 68.00, '以一杯米酒、一杯酱油、一杯麻油为底，与鸡块同炒收汁，九层塔提香，是台湾经典家常名菜。', '台湾菜', 1, '酱香甘甜', '鸡块、九层塔、米酒、酱油、麻油', '焖炒', 0, '大豆', 1, '2026-03-06 09:35:42', '2026-03-06 09:35:42');

-- ----------------------------
-- Table structure for order_items
-- ----------------------------
DROP TABLE IF EXISTS `order_items`;
CREATE TABLE `order_items`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `dish_id` int NOT NULL,
  `dish_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10, 2) NOT NULL,
  `subtotal` decimal(10, 2) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `dish_id`(`dish_id` ASC) USING BTREE,
  INDEX `order_id`(`order_id` ASC) USING BTREE,
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`dish_id`) REFERENCES `menu_items` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 32 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of order_items
-- ----------------------------
INSERT INTO `order_items` VALUES (1, 1, 2, '麻婆豆腐', 1, 18.00, 18.00);
INSERT INTO `order_items` VALUES (2, 2, 3, '清炒时蔬', 1, 15.00, 15.00);
INSERT INTO `order_items` VALUES (11, 6, 3, '清炒时蔬', 1, 15.00, 15.00);
INSERT INTO `order_items` VALUES (12, 7, 1, '宫保鸡丁', 1, 28.00, 28.00);
INSERT INTO `order_items` VALUES (13, 8, 1, '宫保鸡丁', 2, 28.00, 56.00);
INSERT INTO `order_items` VALUES (14, 9, 6, '东坡肉', 1, 88.00, 88.00);
INSERT INTO `order_items` VALUES (15, 9, 7, '夫妻肺片', 2, 58.00, 116.00);
INSERT INTO `order_items` VALUES (16, 9, 8, '西湖醋鱼', 2, 72.00, 144.00);
INSERT INTO `order_items` VALUES (17, 10, 9, '葱爆羊肉', 1, 68.00, 68.00);
INSERT INTO `order_items` VALUES (18, 10, 10, '粤式白切鸡', 2, 78.00, 156.00);
INSERT INTO `order_items` VALUES (19, 10, 11, '剁椒鱼头', 1, 88.00, 88.00);
INSERT INTO `order_items` VALUES (20, 11, 12, '北京烤鸭卷饼', 2, 128.00, 256.00);
INSERT INTO `order_items` VALUES (21, 11, 13, '冰糖莲藕排骨汤', 1, 68.00, 68.00);
INSERT INTO `order_items` VALUES (22, 11, 14, '扬州炒饭', 2, 45.00, 90.00);
INSERT INTO `order_items` VALUES (23, 12, 15, '糖醋里脊', 2, 65.00, 130.00);
INSERT INTO `order_items` VALUES (24, 12, 16, '蒙古烤肉拼盘', 1, 138.00, 138.00);
INSERT INTO `order_items` VALUES (25, 12, 17, '云南汽锅鸡', 1, 98.00, 98.00);
INSERT INTO `order_items` VALUES (26, 13, 18, '麻酱豆腐丝', 1, 32.00, 32.00);
INSERT INTO `order_items` VALUES (27, 13, 19, '酸菜白肉锅', 2, 88.00, 176.00);
INSERT INTO `order_items` VALUES (28, 13, 20, '姜葱焗蟹', 1, 168.00, 168.00);
INSERT INTO `order_items` VALUES (29, 14, 21, '酸辣土豆丝', 1, 28.00, 28.00);
INSERT INTO `order_items` VALUES (30, 14, 22, '蜜汁叉烧', 2, 75.00, 150.00);
INSERT INTO `order_items` VALUES (31, 14, 23, '水煮牛肉', 2, 78.00, 156.00);

-- ----------------------------
-- Table structure for orders
-- ----------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `order_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `contact_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `delivery_address` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `total_amount` decimal(10, 2) NOT NULL,
  `total_quantity` int NOT NULL,
  `status` tinyint NOT NULL DEFAULT 0,
  `delivery_distance` decimal(8, 2) NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `order_no`(`order_no` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of orders
-- ----------------------------
INSERT INTO `orders` VALUES (1, 2, '20250703105217285', '张三', '13812345678', '北京市海淀区中关村大街1号科技大厦A座1001室', 18.00, 1, 4, 15.10, '2025-07-03 10:52:17', '2025-07-03 11:05:43');
INSERT INTO `orders` VALUES (2, 2, '20250703110344662', '尚硅谷', '13624017478', '北京市昌平区回龙观东大街', 15.00, 1, 0, 3.19, '2025-07-03 11:03:44', '2025-07-03 11:03:44');
INSERT INTO `orders` VALUES (6, 2, '20250703162549259', '123', '13423456789', '北京市昌平区温都水城', 15.00, 1, 0, 1.62, '2025-07-03 16:25:49', '2025-07-03 16:25:49');
INSERT INTO `orders` VALUES (7, 2, '20251016212342363', 'hzk', '18438592661', '北京市昌平区回龙观', 28.00, 1, 0, 7.19, '2025-10-16 21:23:42', '2025-10-16 21:23:42');
INSERT INTO `orders` VALUES (8, 2, '20251016214926730', 'test', '13812345678', '北京市昌平区回龙观', 56.00, 2, 0, 7.19, '2025-10-16 21:49:26', '2025-10-16 21:49:26');
INSERT INTO `orders` VALUES (9, 3, '20260301174450100', '张三', '13900000001', '北京市海淀区中关村大街1号', 348.00, 5, 4, 1.95, '2026-03-01 17:44:51', '2026-03-01 17:44:51');
INSERT INTO `orders` VALUES (10, 3, '20260304174450101', '张三', '13900000001', '北京市海淀区中关村大街1号', 312.00, 4, 4, 2.84, '2026-03-04 17:44:51', '2026-03-04 17:44:51');
INSERT INTO `orders` VALUES (11, 4, '20260226174450102', '李四', '13900000002', '北京市朝阳区建国路88号', 414.00, 5, 4, 2.49, '2026-02-26 17:44:51', '2026-02-26 17:44:51');
INSERT INTO `orders` VALUES (12, 4, '20260303174450103', '李四', '13900000002', '北京市朝阳区建国路88号', 366.00, 4, 4, 0.61, '2026-03-03 17:44:51', '2026-03-03 17:44:51');
INSERT INTO `orders` VALUES (13, 5, '20260228174450104', '王五', '13900000003', '北京市西城区西单北大街120号', 376.00, 4, 4, 2.55, '2026-02-28 17:44:51', '2026-02-28 17:44:51');
INSERT INTO `orders` VALUES (14, 5, '20260305174450105', '王五', '13900000003', '北京市西城区西单北大街120号', 334.00, 5, 4, 1.59, '2026-03-05 17:44:51', '2026-03-05 17:44:51');

-- ----------------------------
-- Table structure for shopping_cart
-- ----------------------------
DROP TABLE IF EXISTS `shopping_cart`;
CREATE TABLE `shopping_cart`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `dish_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT 1,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_user_dish`(`user_id` ASC, `dish_id` ASC) USING BTREE,
  INDEX `dish_id`(`dish_id` ASC) USING BTREE,
  CONSTRAINT `shopping_cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `shopping_cart_ibfk_2` FOREIGN KEY (`dish_id`) REFERENCES `menu_items` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 45 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of shopping_cart
-- ----------------------------
INSERT INTO `shopping_cart` VALUES (19, 5, 1, 4, '2025-07-03 16:01:29', '2025-07-03 16:10:40');
INSERT INTO `shopping_cart` VALUES (20, 5, 2, 3, '2025-07-03 16:01:48', '2025-07-03 16:02:13');
INSERT INTO `shopping_cart` VALUES (21, 5, 3, 2, '2025-07-03 16:01:50', '2025-07-03 16:01:50');
INSERT INTO `shopping_cart` VALUES (25, 1, 9, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (26, 1, 6, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (27, 1, 14, 3, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (28, 1, 13, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (29, 2, 23, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (30, 2, 8, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (31, 2, 19, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (32, 2, 7, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (33, 4, 22, 3, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (34, 4, 6, 3, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (35, 4, 23, 3, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (36, 4, 12, 3, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (37, 5, 19, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (38, 5, 13, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (39, 5, 20, 3, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (40, 5, 14, 2, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (41, 3, 16, 2, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (42, 3, 14, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (43, 3, 10, 1, '2026-03-06 09:44:50', '2026-03-06 09:44:50');
INSERT INTO `shopping_cart` VALUES (44, 3, 12, 2, '2026-03-06 09:44:50', '2026-03-06 09:44:50');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  `is_active` tinyint(1) NULL DEFAULT 1,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin@example.com', NULL, '2025-07-02 09:46:39', NULL, 1);
INSERT INTO `users` VALUES (2, 'test', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'test@example.com', '13812345678', '2025-07-02 09:46:39', '2025-10-16 21:21:16', 1);
INSERT INTO `users` VALUES (3, 'testuser1', '85777f270ad7cf2a790981bbae3c4e484a1dc55e24a77390d692fbf1cffa12fa', 'testuser1@example.com', '13800138000', '2025-07-02 10:10:31', '2025-07-03 09:17:04', 1);
INSERT INTO `users` VALUES (4, 'test2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '123@qq.com', '13624007576', '2025-07-02 13:54:00', '2025-07-02 13:54:06', 1);
INSERT INTO `users` VALUES (5, 'testuser', '7e6e0c3079a08c5cc6036789b57e951f65f82383913ba1a49ae992544f1b4b6e', 'test@example.com', '13812345678', '2025-07-03 15:45:35', '2025-07-03 15:52:29', 1);

SET FOREIGN_KEY_CHECKS = 1;
