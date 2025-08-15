from pydantic import BaseModel


class AddResponse(BaseModel):
    id: int
