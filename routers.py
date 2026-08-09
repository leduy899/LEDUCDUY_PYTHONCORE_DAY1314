from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from database import get_db
import models
import schemas
import pydantic

router = APIRouter()

def build_response(status_code: int, message: str, data: Any = None, error: str = None):
    return {
        "statusCode": status_code,
        "error": error,
        "message": message,
        "data": data
    }

@router.get("/products/", response_model=schemas.StandardResponse)
def get_products(category_id: Optional[int] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.ProductModel)
    if category_id:
        query = query.filter(models.ProductModel.category_id == category_id)
    if search:
        query = query.filter(models.ProductModel.name.ilike(f"%{search}%"))
    products = query.all()
    
    data = [schemas.ProductResponse.model_validate(p) for p in products]
    return build_response(200, "Truy vấn danh sách thành công", data)

@router.post("/products/", response_model=schemas.StandardResponse)
def create_product(product: pydantic.ProductCreate, db: Session = Depends(get_db)):
    if db.query(models.ProductModel).filter(models.ProductModel.product_code == product.product_code).first():
        return build_response(400, "Thất bại", error="Mã sản phẩm đã tồn tại")
    
    if not db.query(models.CategoryModel).filter(models.CategoryModel.id == product.category_id).first():
        return build_response(404, "Thất bại", error="Danh mục không tồn tại")

    db_product = models.ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return build_response(201, "Thêm sản phẩm thành công", schemas.ProductResponse.model_validate(db_product))

@router.put("/products/{id}", response_model=schemas.StandardResponse)
def update_product(id: int, product_update: pydantic.ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.ProductModel).filter(models.ProductModel.id == id).first()
    if not db_product:
        return build_response(404, "Thất bại", error="Không tìm thấy sản phẩm")
    
    if product_update.price is not None:
        db_product.price = product_update.price
    if product_update.stock_quantity is not None:
        db_product.stock_quantity = product_update.stock_quantity
        
    db.commit()
    db.refresh(db_product)
    return build_response(200, "Cập nhật thành công", schemas.ProductResponse.model_validate(db_product))

@router.post("/orders/", response_model=schemas.StandardResponse)
def create_order(order: pydantic.OrderCreate, db: Session = Depends(get_db)):
    new_order = models.OrderModel(
        order_code=f"ORD{str(uuid.uuid4())[:6].upper()}",
        customer_name=order.customer_name,
        total_amount=0.0
    )
    db.add(new_order)
    db.flush() # Tạo ID đơn hàng ngay lập tức để link với items
    
    total_amount = 0.0
    for item in order.items:
        db_product = db.query(models.ProductModel).filter(models.ProductModel.id == item.product_id).first()
        if not db_product:
            db.rollback()
            return build_response(400, "Thất bại", error=f"Sản phẩm ID {item.product_id} không tồn tại")
        
        if db_product.stock_quantity < item.quantity:
            db.rollback()
            return build_response(400, "Thất bại", error=f"Sản phẩm {db_product.name} đã hết hàng")
            
        # Trừ tồn kho & Tính tiền
        db_product.stock_quantity -= item.quantity
        total_amount += db_product.price * item.quantity
        
        order_item = models.OrderItemModel(
            order_id=new_order.id,
            product_id=db_product.id,
            quantity=item.quantity,
            unit_price=db_product.price
        )
        db.add(order_item)
        
    new_order.total_amount = total_amount
    db.commit() # Commit Database Transaction
    db.refresh(new_order)
    
    return build_response(201, "Tạo đơn hàng thành công", schemas.OrderResponse.model_validate(new_order))

@router.get("/orders/{id}", response_model=schemas.StandardResponse)
def get_order(id: int, db: Session = Depends(get_db)):
    order = db.query(models.OrderModel).filter(models.OrderModel.id == id).first()
    if not order:
        return build_response(404, "Thất bại", error="Không tìm thấy đơn hàng")
    return build_response(200, "Thành công", schemas.OrderResponse.model_validate(order))

@router.delete("/categories/{id}", response_model=schemas.StandardResponse)
def delete_category(id: int, db: Session = Depends(get_db)):
    category = db.query(models.CategoryModel).filter(models.CategoryModel.id == id).first()
    if not category:
        return build_response(404, "Thất bại", error="Danh mục không tồn tại")
        
    if db.query(models.ProductModel).filter(models.ProductModel.category_id == id).first():
        return build_response(400, "Thất bại", error="Không thể xóa do còn chứa sản phẩm")
        
    db.delete(category)
    db.commit()
    return build_response(200, "Xóa danh mục thành công")
