from pydantic import BaseModel


class UserSearch(BaseModel):
    user_host: str
    user_request: str
