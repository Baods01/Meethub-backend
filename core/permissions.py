"""
权限常量定义模块
提供系统中所有预设权限的常量定义
权限格式: 模块名_操作
权限值格式: 模块名:操作
"""

# 用户管理权限
USER_CREATE = "user:create"  # 创建用户
USER_READ = "user:read"      # 读取用户信息
USER_UPDATE = "user:update"  # 更新用户信息
USER_DELETE = "user:delete"  # 删除用户
USER_LIST = "user:list"      # 用户列表查看
USER_ROLES = "user:roles"    # 用户角色管理

# 角色管理权限
ROLE_CREATE = "role:create"  # 创建角色
ROLE_READ = "role:read"      # 读取角色信息
ROLE_UPDATE = "role:update"  # 更新角色信息
ROLE_DELETE = "role:delete"  # 删除角色
ROLE_LIST = "role:list"      # 角色列表查看
ROLE_PERMISSIONS = "role:permissions"  # 角色权限管理

# 活动管理权限
ACTIVITY_CREATE = "activity:create"    # 创建活动
ACTIVITY_READ = "activity:read"        # 读取活动信息
ACTIVITY_UPDATE = "activity:update"    # 更新活动信息
ACTIVITY_DELETE = "activity:delete"    # 删除活动
ACTIVITY_LIST = "activity:list"        # 活动列表查看
ACTIVITY_PUBLISH = "activity:publish"  # 发布活动
ACTIVITY_CANCEL = "activity:cancel"    # 取消活动
ACTIVITY_ARCHIVE = "activity:archive"  # 归档活动

# 报名管理权限
ENROLLMENT_CREATE = "enrollment:create"  # 创建报名
ENROLLMENT_READ = "enrollment:read"      # 读取报名信息
ENROLLMENT_UPDATE = "enrollment:update"  # 更新报名信息
ENROLLMENT_DELETE = "enrollment:delete"  # 删除报名
ENROLLMENT_LIST = "enrollment:list"      # 报名列表查看
ENROLLMENT_APPROVE = "enrollment:approve"  # 审核报名
ENROLLMENT_CHECKIN = "enrollment:checkin"  # 签到管理

# 系统管理权限
SYSTEM_SETTINGS = "system:settings"      # 系统设置管理
SYSTEM_LOG = "system:log"                # 系统日志查看
SYSTEM_BACKUP = "system:backup"          # 系统备份
SYSTEM_RESTORE = "system:restore"        # 系统恢复

# AI助手权限
AI_ASSISTANT_USE = "ai:use"              # 使用AI助手
AI_ASSISTANT_ADMIN = "ai:admin"          # 管理AI助手设置

# 预定义权限集合
# 超级管理员权限集
SUPER_ADMIN_PERMISSIONS = {
    USER_CREATE, USER_READ, USER_UPDATE, USER_DELETE, USER_LIST, USER_ROLES,
    ROLE_CREATE, ROLE_READ, ROLE_UPDATE, ROLE_DELETE, ROLE_LIST, ROLE_PERMISSIONS,
    ACTIVITY_CREATE, ACTIVITY_READ, ACTIVITY_UPDATE, ACTIVITY_DELETE, ACTIVITY_LIST,
    ACTIVITY_PUBLISH, ACTIVITY_CANCEL, ACTIVITY_ARCHIVE,
    ENROLLMENT_CREATE, ENROLLMENT_READ, ENROLLMENT_UPDATE, ENROLLMENT_DELETE,
    ENROLLMENT_LIST, ENROLLMENT_APPROVE, ENROLLMENT_CHECKIN,
    SYSTEM_SETTINGS, SYSTEM_LOG, SYSTEM_BACKUP, SYSTEM_RESTORE,
    AI_ASSISTANT_USE, AI_ASSISTANT_ADMIN
}

# 活动组织者权限集
ORGANIZER_PERMISSIONS = {
    USER_READ, USER_LIST,
    ACTIVITY_CREATE, ACTIVITY_READ, ACTIVITY_UPDATE, ACTIVITY_DELETE, ACTIVITY_LIST,
    ACTIVITY_PUBLISH, ACTIVITY_CANCEL, ACTIVITY_ARCHIVE,
    ENROLLMENT_READ, ENROLLMENT_LIST, ENROLLMENT_APPROVE, ENROLLMENT_CHECKIN,
    AI_ASSISTANT_USE
}

# 普通用户权限集
USER_PERMISSIONS = {
    USER_READ,
    ACTIVITY_READ, ACTIVITY_LIST,
    ENROLLMENT_CREATE, ENROLLMENT_READ, ENROLLMENT_UPDATE, ENROLLMENT_DELETE,
    AI_ASSISTANT_USE
}