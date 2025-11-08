from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from schemas.auth import (
    LoginRequest, Token, RefreshTokenResponse,
    PasswordResetVerify, PasswordReset
)
from schemas.users import UserCreate, UserResponse
from dao.user_dao import UserDAO
from core.auth.jwt_handler import JWTHandler
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.permission_checker import requires_permissions
from core.permissions import USER_READ
import bcrypt

router = APIRouter(prefix="/auth", tags=["认证"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口 (OAuth2密码模式)
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
    if not await user_dao.verify_password(user, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成JWT令牌
    token_data = JWTHandler.create_token_response(user.id)
    
    return Token(**token_data)

@router.post("/login/credential", response_model=Token)
async def login_by_credential(login_data: LoginRequest):
    """
    用户登录接口 (支持邮箱/用户名/手机号登录)
    :param login_data: 登录请求数据，包含username(可以是用户名/邮箱/手机号)和password
    :return: JWT令牌
    """
    # 获取用户数据访问对象
    user_dao = UserDAO()
    
    # 尝试通过不同的凭证查询用户
    user = await user_dao.get_user_by_username(login_data.username)
    if not user:
        user = await user_dao.get_user_by_email(login_data.username)
    if not user:
        user = await user_dao.get_user_by_phone(login_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱/手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not await user_dao.verify_password(user, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱/手机号或密码错误",
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
        
@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    authorized: bool = Depends(JWTAuthMiddleware()),
    has_permission: bool = requires_permissions([USER_READ])
):
    """
    获取当前登录用户信息
    :param request: FastAPI请求对象
    :return: 当前用户信息
    """
    try:
        if not hasattr(request.state, 'user'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未认证或会话已过期"
            )
        
        user = request.state.user
        # 获取用户角色
        user_roles = await user.roles.all()
        
        # 构建响应
        response_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "nickname": user.nickname,
            "bio": user.bio,
            "avatar": user.avatar,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
            "roles": user_roles
        }
        
        return response_data
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )

@router.post("/refresh", response_model=RefreshTokenResponse, description="刷新访问令牌")
async def refresh_token(request: Request, authorized: bool = Depends(JWTAuthMiddleware())):
    """
    刷新访问令牌
    此接口需要用户已经登录（提供有效的访问令牌）
    返回一个新的访问令牌
    """
    try:
        if not hasattr(request.state, 'user'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未认证或会话已过期"
            )
        
        user = request.state.user
        
        # 生成新的访问令牌
        token_data = JWTHandler.create_token_response(user.id)
        
        return RefreshTokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"]
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        )

@router.post("/reset-password/verify", description="验证用户身份")
async def verify_reset_password(verify_data: PasswordResetVerify):
    """
    验证用户身份以重置密码
    :param verify_data: 包含邮箱和手机号的验证数据
    :return: 验证结果
    """
    try:
        user_dao = UserDAO()
        
        # 通过邮箱查找用户
        user = await user_dao.get_user_by_email(verify_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到该用户"
            )
        
        # 验证手机号是否匹配
        if user.phone != verify_data.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱和手机号不匹配"
            )
        
        return {
            "message": "身份验证成功",
            "verified": True
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"身份验证失败: {str(e)}"
        )

@router.post("/reset-password", description="重置用户密码")
async def reset_password(reset_data: PasswordReset):
    """
    重置用户密码
    :param reset_data: 包含邮箱、手机号和新密码的重置数据
    :return: 重置结果
    """
    try:
        user_dao = UserDAO()
        
        # 通过邮箱查找用户
        user = await user_dao.get_user_by_email(reset_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到该用户"
            )
        
        # 验证手机号是否匹配
        if user.phone != reset_data.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱和手机号不匹配"
            )
        
        # 更新用户密码
        update_result = await user_dao.update_user(
            user.id, 
            {"password": reset_data.new_password}
        )
        
        if not update_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="密码更新失败"
            )
        
        return {
            "message": "密码重置成功",
            "success": True
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码重置失败: {str(e)}"
        )