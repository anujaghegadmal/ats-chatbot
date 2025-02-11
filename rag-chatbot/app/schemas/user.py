from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    user_name: str
    user_password: str

class UserInDB(User):
    hashed_password: str