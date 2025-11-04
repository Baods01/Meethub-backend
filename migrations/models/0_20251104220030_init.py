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
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
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
    "eJztmm1P4zgQgP9K1U+cxK3StHnhvpXC3fYE9ATlbrXLKnISp41InG7iANWK/35j5/2tpK"
    "XQLvAlasczif3M2JmZ9mfX9UzsBJ+uA+wH3T86P7sEuRg+FAcOO120WGRiJqBId7hmmKro"
    "AfWRQUFoISfAIDJxYPj2gtoeYao3oSKJ6k0oi33lJlRVWWV2pmeAoU1mVRUZib2bUFJUnS"
    "mGxP4RYo16M0zn2Af1b99BbBMTP+Ag+bq41SwbO2ZhObbJbsDlGl0uuGxM6J9ckc1B1wzP"
    "CV2SKS+WdO6RVNsmlElnmGAfUcxuT/2QLZKEjhPDSNYdzTRTiaaYszGxhUKHoWLWq0mNT8"
    "qUYhvDI4w4zCzy3Yw98XexN1AGal8eqKDCZ5VKlMdoqRmHyJDTuJh2H/k4oijS4EgzhszR"
    "/HOF5GiO/HqUeZsSUJh6GWiC76WJQkgNBLMlVRc9aA4mMzqHr5KwAuG/w8vR5+HlgST8xu"
    "7twWaItshFPCLyIUY5o7pAQXDv+TXx2Uw1b7Mdqokgw5pt4ae4SrohA11V6G1CtCeqLZCC"
    "ViNTPlaEil1kO+sQTQ02whmH4BZi9EhAGFjq+kYsRUlqwRK0GlnysVKAAo+19nxqsGOWsj"
    "jQ4ar0EcRo31I2is5em+DsNcdmr4wT3cH56q/DM7PYCtBnbfWj/gCugmFdX57tTYQS27hd"
    "98WUt9k5VlnuS7DrjyxhP95Juu1VWU7xQ0O+FKvvHOMAi4hddcSOUFVgnw29HdIVCKenX6"
    "bsJm4Q/HDy6A7Oh184VXcZj5xNLv5K1HOoR2eT4xJiO9AgVbbvaoL22PMcjEhDbpq3KxHX"
    "wfClXv7pqVsJXdFi6ZQIKYBsGcBcNvvPZ348mZwVmB+Py1Cvz49P4ezlDgAlm0ZJfZzGFk"
    "jfYd+Gp9TkWE+xzlu+Iu3G+imP+wipBlRRutEyV3gd3IaPGQwN0SrtExihtovrcRctS7TN"
    "2PRT8uHVs1yxB9mEBHrgBcli/CVr0PK8hpWZE+Is44206rAZn59eTYfn/xTccTKcnrIRsX"
    "DaJNIDuXS2pzfp/Deefu6wr52vk4tTztUL6MznT8z0pl+7bE4opJ5GvHsNmblMK5EmuAru"
    "Dhfmhu4uWu6bu2XZGjBH68I7dnc8+czbDgqo5ngzm6zr7aLlFry91fxLEQTeE2C1l6ywfW"
    "5J0vqO/0UcnYCpbGzWPrNuc80fJtCRcXuPfFOrjHii16RbHXJFt7ar5MMLOKhG0zkiy6nH"
    "rjyexsAZEaMu64k7lZfJfXbTUFKPTBGuoiKuFSqZNHswX5BWasSmy/Oxw4/NfFcu4uf5HP"
    "0tXqZctaiVmbolHuM28Rid+144mydiLfUHIIYn4+g9PxpejYYnPNC0CmAeNy4iaMZlbMGP"
    "h6WZ1/SW0yU195bTybTpLWcuaOwt51XecW85w7AvveW1y/c96SnnA4r1lPepijdgP63DNN"
    "HfJ6aK1XtGb3n7TPOTraBt7pCUzHbeKSmcg30DSkrVahu2H52St9op+Sjdaw6Ut1LLfZTu"
    "78rdfPK7qOeyeuR59Vz6z5O3Wc+lyyvXc1k9XKzn8jVbuZ7L13rPq+fSsGks54bYt415t6"
    "aei0cOVxV0KNN5qqJLvFRF/35qtWYGr1yf3UHw1ea8zeVEzmTH/1FpT/Hlf6tmW2MNiLH6"
    "rwmwJ7Spv0Cr+e8TQk1VSygmNSnL31eTi6bCNjUpgbwmsMBvpm3Qw45jB/T7fmJdQZGten"
    "XJVa6uSpkFuwEruV4vV6h5vTz+DxGLfgY="
)
