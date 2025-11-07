from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import LoginRequest, Token
from schemas.users import UserCreate, UserResponse
from dao.user_dao import UserDAO
from core.auth.jwt_handler import JWTHandler
import bcrypt

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    :param form_data: 表单数据，包含username和password
    :return: JWT令牌
    """
    # 获取用户数据访问对象
    user_dao = UserDAO()
    
    # 查询用户
    user = await user_dao.get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    # 处理密码长度限制
    password_bytes = form_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # 验证密码
    stored_password = user.password.encode('utf-8')
    if not bcrypt.checkpw(password_bytes, stored_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成JWT令牌
    token_data = JWTHandler.create_token_response(user.id)
    
    return Token(**token_data)

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """
    用户注册接口
    :param user: 用户创建请求模型
    :return: 创建的用户信息
    """
    try:
        user_dao = UserDAO()
        
        # 检查用户名是否已存在
        existing_user = await user_dao.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        existing_email = await user_dao.get_user_by_email(user.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        
        # 创建用户
        created_user = await user_dao.create_user(user.model_dump())
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="用户创建失败"
            )
            
        # 分配普通用户角色（角色ID为11）
        role_added = await user_dao.add_user_role(created_user.id, 11)
        if not role_added:
            # 如果角色分配失败，记录错误但不影响用户创建
            print(f"警告：无法为用户 {created_user.username} 分配普通用户角色")
        
        # 获取用户角色
        user_roles = await created_user.roles.all()
        
        # 构建响应
        response_data = {
            "id": created_user.id,
            "username": created_user.username,
            "email": created_user.email,
            "phone": created_user.phone,
            "nickname": created_user.nickname,
            "bio": created_user.bio,
            "avatar": created_user.avatar,
            "is_active": created_user.is_active,
            "is_verified": created_user.is_verified,
            "created_at": created_user.created_at,
            "updated_at": created_user.updated_at,
            "last_login": created_user.last_login,
            "roles": user_roles
        }
        
        return response_data
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )