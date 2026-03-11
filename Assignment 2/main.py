from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is working"}



# Products list
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Monitor", "price": 8999, "category": "Electronics", "in_stock": False},

    # Q1 — Added 3 new products
    {"id": 5, "name": "Laptop Stand", "price": 999, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1599, "category": "Electronics", "in_stock": False}
]

# Home
@app.get("/")
def home():
    return {"message": "Welcome to My E-commerce Store"}

# Get all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

# Q2 — Filter by Category
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered = [
        product for product in products
        if product["category"].lower() == category_name.lower()
    ]

    if not filtered:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": filtered
    }

# Q3 — Show only In-Stock Products
@app.get("/products/instock")
def get_instock_products():
    instock = [product for product in products if product["in_stock"]]

    return {
        "in_stock_products": instock,
        "count": len(instock)
    }

# Q4 — Store Summary
@app.get("/store/summary")
def store_summary():
    total_products = len(products)
    in_stock = len([p for p in products if p["in_stock"]])
    out_of_stock = total_products - in_stock
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "categories": categories
    }

# Q5 — Search Products by Name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    results = [
        product for product in products
        if keyword.lower() in product["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "matched_products": results,
        "count": len(results)
    }
##Assignment 2
## Q1 Filter Products
@app.get("/products/filter")
def filter_products(category: str = None, max_price: int = None, min_price: int = None):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return result
##Question 2:Get Product Price
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}
##Question 3
from pydantic import BaseModel, Field
from typing import Optional
feedback = []
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }
## Question 4 : Product Summary
@app.get("/products/summary")
def product_summary():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }
## Question 5 : Bulk order
from typing import List
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f'{product["name"]} is out of stock'
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }
