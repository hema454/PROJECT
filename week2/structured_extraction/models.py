

from pydantic import BaseModel, EmailStr


class ExtractedContact(BaseModel):
    name: str
    email: EmailStr
    company: str
    urgent: bool