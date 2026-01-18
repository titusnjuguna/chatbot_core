from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from repositories.users import UserRepository
from services.users import UserService
from schema.users import *
from datetime import timedelta
from jose import JWTError
# from utils.users import create_access_token, create_refresh_token  
from config.auth import verify_password,get_password_hash,create_access_token,verify_token



router = APIRouter()

async def get_user_service(db: AsyncSession = Depends(get_db)):
    userRepo = UserRepository(db)
    return UserService(userRepo)


@router.post(
    "/add/user",
     status_code=status.HTTP_201_CREATED,
)
async def add_user(request: UserCreate, service: UserService = Depends(get_user_service)):
    hashed_password = get_password_hash(request.password)

    new_req = {
        "password":hashed_password,
        "email": request.email
    }
    return await service.create_user(new_req)



@router.post("/login")
async def user_login(
    request: UserLogin,
    service: UserService = Depends(get_user_service)):
    user = await service.get_user_by_email(email=request.email)
    print(user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)

    access_token = create_access_token(email = user.email, expires_delta=access_token_expires)
    # refresh_token = create_refresh_token( 
    #     data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    # )

    return {
        "access_token": access_token,
        "refresh_token": "refresh_token",
        "token_type": "bearer"
    }

    
    
    



