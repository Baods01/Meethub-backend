from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(128) NOT NULL COMMENT '密码',
    `email` VARCHAR(255) UNIQUE COMMENT '邮箱',
    `phone` VARCHAR(11) UNIQUE COMMENT '手机号',
    `avatar` VARCHAR(255) COMMENT '头像URL',
    `nickname` VARCHAR(50) COMMENT '昵称',
    `bio` LONGTEXT COMMENT '个人简介',
    `profile_attributes` JSON COMMENT '用户个性属性',
    `is_active` BOOL NOT NULL COMMENT '是否激活' DEFAULT 1,
    `is_verified` BOOL NOT NULL COMMENT '是否验证' DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `last_login` DATETIME(6) COMMENT '最后登录时间'
) CHARACTER SET utf8mb4 COMMENT='用户表';
CREATE TABLE IF NOT EXISTS `roles` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID',
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT '角色编码',
    `description` LONGTEXT COMMENT '角色描述',
    `is_active` BOOL NOT NULL COMMENT '是否激活' DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `permissions` JSON COMMENT '权限列表'
) CHARACTER SET utf8mb4 COMMENT='角色表';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user_roles` (
    `users_id` INT NOT NULL,
    `roles_id` INT NOT NULL,
    FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`roles_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_user_roles_users_i_c3bcd4` (`users_id`, `roles_id`)
) CHARACTER SET utf8mb4 COMMENT='用户角色';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "h/LV+hZnt5/B9gZoMP"
)
