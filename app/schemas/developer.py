from pydantic import BaseModel

class RequestOTP(BaseModel):
    pass

class VerifyOTP(BaseModel):
    code: str
