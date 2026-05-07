from pydantic import BaseModel
from typing import Optional, List, Dict

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class User(BaseModel):
    username: str
    role: str

class UserInDB(User):
    hashed_password: str

class EvaluationResult(BaseModel):
    filename: str
    turnover: Optional[str] = None
    iso_certification: Optional[bool] = None
    past_experience: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    status: str
    
class AuditLogEntry(BaseModel):
    timestamp: str
    user: str
    action: str
    filename: str
    status: str
    details: Dict
