from beanie import Document


class User(Document):
    name: str
    email: str
    conversations: list[str] = []

    class Settings:
        name = "users"
