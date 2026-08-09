from pydantic import BaseModel, Field
from typing import List, Optional

class ProductCreate(BaseModel):
    product_code: str = Field(..., min_length=4, max_length=10)
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    category_id: int

class ProductUpdate(BaseModel):
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    customer_name: str
    items: List[OrderItemCreate] = Field(..., min_length=1)
