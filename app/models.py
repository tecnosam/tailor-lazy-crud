from datetime import datetime
from typing import (
    List,
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

    id: UUID = Field(default=uuid4)


class User(BaseModel):

    name: str
    email: str
    password: str
    gender: str


class Product(OurBase):

    tailor_id: int
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

    user_id: UUID
    tailor_id: UUID

    product_id: Optional[UUID]

    price_agreed: float

    due_date: datetime 

    status: str

    tracking: List[Tracking]
