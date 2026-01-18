from sqlalchemy.ext.asyncio import AsyncSession
from schema.users import UserCreate
from models.users import User
from sqlalchemy import select,update,delete


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def create_user(self,user:dict):
        db_user = User(
            email = user.get("email"),
            password = user.get("password"),
            name = user.get("name")


        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def get_user_by_email(self,email):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    def get_user(self, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchone()

    def close(self):
        self.connection.close()