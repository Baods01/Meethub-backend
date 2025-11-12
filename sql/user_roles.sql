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

 Date: 12/11/2025 20:49:55
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for user_roles
-- ----------------------------
DROP TABLE IF EXISTS `user_roles`;
CREATE TABLE `user_roles`  (
  `users_id` int NOT NULL,
  `roles_id` int NOT NULL,
  UNIQUE INDEX `uidx_user_roles_users_i_c3bcd4`(`users_id` ASC, `roles_id` ASC) USING BTREE,
  INDEX `roles_id`(`roles_id` ASC) USING BTREE,
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`roles_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户角色' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_roles
-- ----------------------------
INSERT INTO `user_roles` VALUES (12, 9);
INSERT INTO `user_roles` VALUES (27, 9);
INSERT INTO `user_roles` VALUES (31, 9);
INSERT INTO `user_roles` VALUES (32, 9);
INSERT INTO `user_roles` VALUES (33, 9);
INSERT INTO `user_roles` VALUES (34, 9);
INSERT INTO `user_roles` VALUES (35, 9);
INSERT INTO `user_roles` VALUES (36, 9);
INSERT INTO `user_roles` VALUES (37, 9);
INSERT INTO `user_roles` VALUES (38, 9);
INSERT INTO `user_roles` VALUES (39, 9);
INSERT INTO `user_roles` VALUES (40, 9);
INSERT INTO `user_roles` VALUES (41, 10);
INSERT INTO `user_roles` VALUES (42, 10);
INSERT INTO `user_roles` VALUES (43, 10);
INSERT INTO `user_roles` VALUES (44, 10);
INSERT INTO `user_roles` VALUES (45, 10);
INSERT INTO `user_roles` VALUES (46, 10);
INSERT INTO `user_roles` VALUES (47, 10);
INSERT INTO `user_roles` VALUES (48, 10);
INSERT INTO `user_roles` VALUES (49, 10);
INSERT INTO `user_roles` VALUES (50, 10);
INSERT INTO `user_roles` VALUES (51, 10);
INSERT INTO `user_roles` VALUES (52, 10);
INSERT INTO `user_roles` VALUES (53, 10);
INSERT INTO `user_roles` VALUES (54, 10);
INSERT INTO `user_roles` VALUES (55, 10);
INSERT INTO `user_roles` VALUES (56, 10);
INSERT INTO `user_roles` VALUES (57, 10);
INSERT INTO `user_roles` VALUES (58, 10);
INSERT INTO `user_roles` VALUES (59, 10);
INSERT INTO `user_roles` VALUES (60, 10);
INSERT INTO `user_roles` VALUES (28, 11);
INSERT INTO `user_roles` VALUES (29, 11);
INSERT INTO `user_roles` VALUES (30, 11);
INSERT INTO `user_roles` VALUES (61, 11);
INSERT INTO `user_roles` VALUES (62, 11);
INSERT INTO `user_roles` VALUES (63, 11);
INSERT INTO `user_roles` VALUES (64, 11);
INSERT INTO `user_roles` VALUES (65, 11);
INSERT INTO `user_roles` VALUES (66, 11);
INSERT INTO `user_roles` VALUES (67, 11);
INSERT INTO `user_roles` VALUES (68, 11);
INSERT INTO `user_roles` VALUES (69, 11);
INSERT INTO `user_roles` VALUES (70, 11);
INSERT INTO `user_roles` VALUES (71, 11);
INSERT INTO `user_roles` VALUES (72, 11);
INSERT INTO `user_roles` VALUES (73, 11);
INSERT INTO `user_roles` VALUES (74, 11);
INSERT INTO `user_roles` VALUES (75, 11);
INSERT INTO `user_roles` VALUES (76, 11);
INSERT INTO `user_roles` VALUES (77, 11);
INSERT INTO `user_roles` VALUES (78, 11);
INSERT INTO `user_roles` VALUES (79, 11);
INSERT INTO `user_roles` VALUES (80, 11);
INSERT INTO `user_roles` VALUES (81, 11);
INSERT INTO `user_roles` VALUES (82, 11);
INSERT INTO `user_roles` VALUES (83, 11);
INSERT INTO `user_roles` VALUES (84, 11);
INSERT INTO `user_roles` VALUES (85, 11);
INSERT INTO `user_roles` VALUES (86, 11);
INSERT INTO `user_roles` VALUES (87, 11);
INSERT INTO `user_roles` VALUES (88, 11);
INSERT INTO `user_roles` VALUES (89, 11);
INSERT INTO `user_roles` VALUES (90, 11);
INSERT INTO `user_roles` VALUES (91, 11);
INSERT INTO `user_roles` VALUES (92, 11);
INSERT INTO `user_roles` VALUES (93, 11);
INSERT INTO `user_roles` VALUES (94, 11);
INSERT INTO `user_roles` VALUES (95, 11);
INSERT INTO `user_roles` VALUES (96, 11);
INSERT INTO `user_roles` VALUES (97, 11);
INSERT INTO `user_roles` VALUES (98, 11);
INSERT INTO `user_roles` VALUES (99, 11);
INSERT INTO `user_roles` VALUES (100, 11);
INSERT INTO `user_roles` VALUES (101, 11);
INSERT INTO `user_roles` VALUES (102, 11);
INSERT INTO `user_roles` VALUES (103, 11);
INSERT INTO `user_roles` VALUES (104, 11);
INSERT INTO `user_roles` VALUES (105, 11);
INSERT INTO `user_roles` VALUES (106, 11);
INSERT INTO `user_roles` VALUES (107, 11);
INSERT INTO `user_roles` VALUES (108, 11);
INSERT INTO `user_roles` VALUES (109, 11);
INSERT INTO `user_roles` VALUES (110, 11);
INSERT INTO `user_roles` VALUES (111, 11);
INSERT INTO `user_roles` VALUES (112, 11);
INSERT INTO `user_roles` VALUES (113, 11);
INSERT INTO `user_roles` VALUES (114, 11);
INSERT INTO `user_roles` VALUES (115, 11);
INSERT INTO `user_roles` VALUES (116, 11);
INSERT INTO `user_roles` VALUES (117, 11);
INSERT INTO `user_roles` VALUES (118, 11);
INSERT INTO `user_roles` VALUES (119, 11);
INSERT INTO `user_roles` VALUES (120, 11);
INSERT INTO `user_roles` VALUES (121, 11);
INSERT INTO `user_roles` VALUES (122, 11);
INSERT INTO `user_roles` VALUES (123, 11);
INSERT INTO `user_roles` VALUES (124, 11);
INSERT INTO `user_roles` VALUES (125, 11);
INSERT INTO `user_roles` VALUES (126, 11);
INSERT INTO `user_roles` VALUES (127, 11);
INSERT INTO `user_roles` VALUES (128, 11);
INSERT INTO `user_roles` VALUES (129, 11);
INSERT INTO `user_roles` VALUES (130, 11);
INSERT INTO `user_roles` VALUES (131, 11);

SET FOREIGN_KEY_CHECKS = 1;
