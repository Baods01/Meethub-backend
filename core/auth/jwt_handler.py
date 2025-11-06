from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
import os

# 从环境变量获取密钥，如果不存在则使用默认值(仅用于开发环境)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class JWTHandler:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        创建JWT访问令牌
        :param data: 要编码到令牌中的数据
        :param expires_delta: 可选的过期时间增量
        :return: JWT字符串
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        验证JWT令牌
        :param token: JWT字符串
        :return: 解码后的payload
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("exp") is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is missing expiration"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    @staticmethod
    def create_token_response(user_id: int) -> dict:
        """
        创建标准的令牌响应格式
        :param user_id: 用户ID
        :return: 包含访问令牌和类型的字典
        """
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = JWTHandler.create_access_token(
            data={"sub": str(user_id)},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }