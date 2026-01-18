from repositories.users import UserRepository

class UserService:
    def __init__(self, user_repository:UserRepository):
        self.user_repository = user_repository


    def get_user_by_email(self, email):
        return self.user_repository.get_user_by_email(email)

    async def create_user(self, user_data):
        email=user_data.get("email")
        
        user_exist = await self.user_repository.get_user_by_email(email=email)
        if user_exist:
            return 'user Already Exist'
        user = await self.user_repository.create_user(user_data)
        return user

    def update_user(self, user_id, user_data):
        return self.user_repository.update(user_id, user_data)

    def delete_user(self, user_id):
        return self.user_repository.delete(user_id)