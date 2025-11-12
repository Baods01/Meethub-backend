/*
 Navicat Premium Data Transfer

 Source Server         : 1
 Source Server Type    : MySQL
 Source Server Version : 80042
 Source Host           : localhost:3306
 Source Schema         : meethub_db

 Target Server Type    : MySQL
 Target Server Version : 80042
 File Encoding         : 65001

 Date: 12/11/2025 20:49:14
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '角色名称',
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '角色编码',
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '角色描述',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  `permissions` json NULL COMMENT '权限列表',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  UNIQUE INDEX `code`(`code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '角色表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of roles
-- ----------------------------
INSERT INTO `roles` VALUES (9, '超级管理员', 'super_admin', '系统超级管理员，具有所有权限', 1, '2025-11-07 18:00:04.186097', '2025-11-07 18:00:04.186097', '[\"user:list\", \"activity:publish\", \"enrollment:read\", \"system:backup\", \"role:update\", \"activity:cancel\", \"enrollment:create\", \"activity:create\", \"system:restore\", \"role:create\", \"activity:delete\", \"role:list\", \"role:delete\", \"enrollment:approve\", \"activity:archive\", \"enrollment:delete\", \"system:settings\", \"activity:update\", \"ai:use\", \"user:roles\", \"user:create\", \"enrollment:list\", \"user:delete\", \"user:update\", \"enrollment:checkin\", \"activity:read\", \"system:log\", \"ai:admin\", \"role:permissions\", \"activity:list\", \"user:read\", \"role:read\", \"enrollment:update\"]');
INSERT INTO `roles` VALUES (10, '活动组织者', 'organizer', '活动组织者，可以创建和管理活动', 1, '2025-11-07 18:00:04.433280', '2025-11-07 18:00:04.433280', '[\"user:list\", \"activity:publish\", \"activity:update\", \"enrollment:read\", \"activity:list\", \"ai:use\", \"user:read\", \"enrollment:list\", \"activity:delete\", \"activity:cancel\", \"enrollment:checkin\", \"activity:read\", \"activity:create\", \"enrollment:approve\", \"activity:archive\"]');
INSERT INTO `roles` VALUES (11, '普通用户', 'normal_user', '普通用户，可以参与活动', 1, '2025-11-07 18:00:04.445400', '2025-11-07 18:00:04.445400', '[\"enrollment:delete\", \"enrollment:read\", \"activity:list\", \"ai:use\", \"user:read\", \"enrollment:create\", \"enrollment:update\", \"activity:read\"]');

SET FOREIGN_KEY_CHECKS = 1;
