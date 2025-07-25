import jwt
import asyncio

from fastapi import APIRouter, Depends, Response, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.auth import (
    create_access_token,
    create_refresh_token,
    authenticate_user,
    get_password_hash,
)
from app.dependencies import get_current_user, check_permission
from app.models import User
from app.dao import UserDAO
from app.config import settings
from app.schemas import SUserRegister, SUserUpdate

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register")
async def register_user(user_data: SUserRegister):
    existing_user = await UserDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    hashed_password = get_password_hash(user_data.password)
    user = await UserDAO.add(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role_id=2,
    )

    return {"message": "User registered"}


@router.post("/login")
async def login_user(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token({"sub": str(user.id), "role": user.role.name})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}


@router.post("/refresh")
async def refresh_tokens(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
):
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id = int(payload.get("sub"))
        user = await UserDAO.find_one_or_none(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        new_access_token = create_access_token(
            {"sub": str(user.id), "role": user.role.name}
        )
        response.set_cookie("access_token", new_access_token, httponly=True)
        return {"access_token": new_access_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@router.get("/profile")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/profile")
async def update_profile(
    user_data: SUserUpdate,
    current_user: User = Depends(get_current_user),
):
    updated_user = await UserDAO.update(
        user_id=current_user.id, **user_data.dict(exclude_unset=True)
    )
    return {"message": "Profile updated"}


@router.delete("/profile")
async def delete_profile(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    await UserDAO.update(user_id=current_user.id, is_active=False)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Account deactivated"}


@router.get("/admin/users")
async def admin_list_users(
    admin: User = Depends(check_permission("manage_users")),
):
    users = await UserDAO.find_all()
    return users
