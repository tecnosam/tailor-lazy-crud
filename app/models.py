from datetime import datetime
from typing import (
    List,
    Dict,
    Optional
)

from pydantic import (
    BaseModel,
    Field
)

from uuid import (
    UUID,
    uuid4
)


class LoginForm(BaseModel):

    email: str
    password: str


class OurBase(BaseModel):

    id: UUID = Field(default_factory=lambda: uuid4().hex)

    images: List[Dict[str, str]] = Field(default_factory=lambda: [])


class User(OurBase):

    name: str
    email: str
    password: str
    gender: str


class Product(OurBase):

    tailor_id: str
    name: str
    description: str
    price: float


class Tailor(User):

    bio: str
    experience_level: str
    
    location: str

    cost: float


class Order(OurBase):

    class Tracking(OurBase):

        title: str
        description: str
        date: datetime 
        status: str

    user_id: str
    tailor_id: str

    product_id: Optional[str] = Field(default="")

    price_agreed: float

    due_date: datetime 

    status: str = Field(default="pending")

    tracking: List[Tracking] = Field(default=[])
