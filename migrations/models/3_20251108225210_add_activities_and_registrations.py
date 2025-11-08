from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `activities` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '活动ID',
    `title` VARCHAR(100) NOT NULL COMMENT '活动名称',
    `description` LONGTEXT NOT NULL COMMENT '活动简介',
    `cover_image` VARCHAR(255) NOT NULL COMMENT '封面图片URL',
    `location` VARCHAR(255) NOT NULL COMMENT '活动地点',
    `start_time` DATETIME(6) NOT NULL COMMENT '活动开始时间',
    `end_time` DATETIME(6) NOT NULL COMMENT '活动结束时间',
    `max_participants` INT NOT NULL COMMENT '招募人数上限',
    `current_participants` INT NOT NULL COMMENT '当前报名人数' DEFAULT 0,
    `tags` JSON NOT NULL COMMENT '活动标签',
    `target_audience` JSON NOT NULL COMMENT '面向人群(专业/年级)',
    `benefits` JSON NOT NULL COMMENT '活动收益(志愿时/综测等)',
    `status` VARCHAR(20) NOT NULL COMMENT '活动状态' DEFAULT 'draft',
    `views_count` INT NOT NULL COMMENT '浏览量' DEFAULT 0,
    `is_deleted` BOOL NOT NULL COMMENT '是否删除' DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `publisher_id` INT NOT NULL COMMENT '活动发布者',
    CONSTRAINT `fk_activiti_users_3c6bf3e1` FOREIGN KEY (`publisher_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='活动表';
        CREATE TABLE IF NOT EXISTS `registrations` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '报名ID',
    `registration_time` DATETIME(6) NOT NULL COMMENT '报名时间' DEFAULT CURRENT_TIMESTAMP(6),
    `status` VARCHAR(20) NOT NULL COMMENT '报名状态' DEFAULT 'pending',
    `comment` LONGTEXT COMMENT '报名备注',
    `additional_info` JSON COMMENT '附加信息',
    `check_in_time` DATETIME(6) COMMENT '签到时间',
    `check_out_time` DATETIME(6) COMMENT '签退时间',
    `feedback` LONGTEXT COMMENT '活动反馈',
    `rating` INT COMMENT '活动评分(1-5)',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `activity_id` INT NOT NULL COMMENT '所属活动',
    `participant_id` INT NOT NULL COMMENT '报名者',
    UNIQUE KEY `uid_registratio_partici_7de432` (`participant_id`, `activity_id`),
    CONSTRAINT `fk_registra_activiti_9682a093` FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_registra_users_6b14a5cb` FOREIGN KEY (`participant_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='活动报名表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `registrations`;
        DROP TABLE IF EXISTS `activities`;"""


MODELS_STATE = (
    "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"
    "cVEEt7D4tc0WbT4N8vIvJYdcKA=="
)
