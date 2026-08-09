from fastapi import FastAPI
import re
from routers import router as api_router
from database import engine
import models

# Tự động đồng bộ các models để tạo bảng trong Database (MySQL)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce Management API - Rikkei Edu")
app.include_router(api_router)

# ========================================================
# PHẦN 1: PYTHON CORE & THUẬT TOÁN NÂNG CAO (30 Điểm)
# ========================================================

# 1.1 Chuẩn hóa & Validate mã sản phẩm
def clean_and_validate_products(products: list) -> list:
    valid_products = []
    pattern = re.compile(r'^[Pp]\d{3}$')
    
    for p in products:
        code = str(p.get("product_code", "")).strip().upper()
        if pattern.match(code):
            p["product_code"] = code
            valid_products.append(p)
    return valid_products

# 1.2 Thuật toán Tìm kiếm Nhị phân (Binary Search)
def binary_search_product(products: list, target_code: str) -> dict:
    left, right = 0, len(products) - 1
    target = target_code.strip().upper()
    
    while left <= right:
        mid = (left + right) // 2
        current_code = str(products[mid].get("product_code", "")).strip().upper()
        
        if current_code == target:
            return products[mid]
        elif current_code < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return None

# 1.3 Thuật toán Sắp xếp (Merge Sort)
def sort_products_by_price_desc(products: list) -> list:
    if len(products) <= 1:
        return products
        
    mid = len(products) // 2
    left = sort_products_by_price_desc(products[:mid])
    right = sort_products_by_price_desc(products[mid:])
    
    return merge_desc(left, right)

def merge_desc(left: list, right: list) -> list:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i]["price"] >= right[j]["price"]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
            
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# 1.4 Thống kê dữ liệu kinh doanh
def analyze_order_stats(orders: list) -> dict:
    total_revenue = 0
    max_order = None
    max_amount = -1
    
    for order in orders:
        if order.get("status") == "COMPLETED":
            total_revenue += order.get("amount", 0)
            
        if order.get("amount", 0) > max_amount:
            max_amount = order.get("amount", 0)
            max_order = order
            
    return {
        "total_revenue": total_revenue,
        "max_order": max_order
    }
