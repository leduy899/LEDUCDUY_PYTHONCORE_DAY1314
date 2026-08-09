from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class CategoryBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    product_code: str
    name: str
    price: float
    stock_quantity: int
    category: Optional[CategoryBase] = None
    class Config:
        from_attributes = True

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_code: str
    customer_name: str
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse] = []
    class Config:
        from_attributes = True

class StandardResponse(BaseModel):
    statusCode: int
    error: Optional[str] = None
    message: str
    data: Optional[Any] = None
