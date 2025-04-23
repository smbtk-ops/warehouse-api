from fastapi import FastAPI, HTTPException, Body, Depends
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from items.models import *
from database import *


class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None

    class Config:
        from_attributes = True


class OrderItem(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: Literal["в процессе", "отправлен", "доставлен"]

    class Config:
        from_attributes = True


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/products")
def create_product(item: Item, db: Session = Depends(get_db)):
    products = Products(
        name=item.name,
        description=item.description,
        price=item.price,
        quantity=item.quantity,
    )
    db.add(products)
    db.commit()
    return {"message": "Product created", "item": item}


@app.get("/products")
def read_items(db: Session = Depends(get_db)) -> list[Item]:
    rows = db.query(Products).all()

    items = []
    for row in rows:
        # print(row.__dict__)
        item = Item(
            name=row.name,
            description=row.description,
            price=row.price,
            quantity=row.quantity,
        )
        items.append(item)

    return items


@app.get("/products/{product_id}", response_model=Item)
def read_product(product_id: int, db: Session = Depends(get_db)) -> Item:
    stmt = select(Products).where(Products.id == product_id)
    row = db.execute(stmt).scalar_one_or_none()

    if row:
        return Item(
            name=row.name,
            description=row.description,
            price=row.price,
            quantity=row.quantity,
        )
    else:
        raise HTTPException(status_code=404, detail="Product not found")


# @app.get("/products/{product_id}", response_model=Item)
# def read_product(product_id: int) -> Item:
#     con = sqlite3.connect("warehouse.db")
#     cursor = con.cursor()
#
#     cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
#     row = cursor.fetchone()
#     con.close()
#
#     if row:
#         return Item(
#             name=row[1],
#             description=row[2],
#             price=row[3],
#             quantity=row[4],
#         )
#     else:
#         raise HTTPException(status_code=404, detail="Product not found")
#

# @app.put("/products/{product_id}", response_model=Item)
# def update_product(product_id: int, item: Item):
#     con = sqlite3.connect("warehouse.db")
#     cursor = con.cursor()
#     cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
#     row = cursor.fetchone()
#     if not row:
#         con.close()
#         raise HTTPException(status_code=404, detail="Product not found")
#     # print(cursor.rowcount, "before")
#
#     current = {
#         "name": row[1],
#         "description": row[2],
#         "price": row[3],
#         "quantity": row[4],
#     }
#
#     updated = {
#         "name": item.name or current["name"],
#         "description": item.description or current["description"],
#         "price": item.price or current["price"],
#         "quantity": item.quantity or current["quantity"],
#     }
#
#     cursor.execute("""UPDATE products
#                    SET name=?, description=?, price=?, quantity=?
#                    WHERE id=?""",
#                    (updated["name"], updated["description"], updated["price"], updated["quantity"], product_id))
#     # print(cursor.rowcount, "after")
#     if cursor.rowcount == -1:
#         con.close()
#         raise HTTPException(status_code=404, detail="Product not found")
#     con.commit()
#     con.close()
#     return item
#
#
# @app.delete("/products/{product_id}")
# def delete_product(product_id: int):
#     con = sqlite3.connect("warehouse.db")
#     cursor = con.cursor()
#     cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
#     row = cursor.fetchone()
#     if not row:
#         con.close()
#         raise HTTPException(status_code=404, detail="Product not found")
#     cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
#     con.commit()
#     con.close()
#     return {"message": "Product deleted"}
#
#
# @app.post("/orders")
# def create_order(items: list[OrderItem]):
#     con = sqlite3.connect("warehouse.db")
#     cursor = con.cursor()
#     for item in items:
#         cursor.execute("SELECT quantity FROM products WHERE id = ?", (item.product_id,))
#         row = cursor.fetchone()
#         print(row[0])
#         if not row:
#             con.close()
#             raise HTTPException(status_code=400, detail=f"Product ID {item.product_id} not found")
#         if row[0] < item.quantity:
#             con.close()
#             raise HTTPException(status_code=400, detail=f"Not enough quantity for product ID {item.product_id}")
#
#     created_at = datetime.utcnow().isoformat()
#     status = "в процессе"
#     cursor.execute("INSERT INTO orders (created_at, status) VALUES (?, ?)", (created_at, status))
#     order_id = cursor.lastrowid
#     for item in items:
#         cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
#                        (order_id, item.product_id, item.quantity))
#         cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?",
#                        (item.quantity, item.product_id))
#     con.commit()
#     con.close()
#     return {"message": "Order created", "order_id": order_id}
#
#
# @app.get("/orders")
# def get_orders():
#     con = sqlite3.connect("warehouse.db")
#     cursor = con.cursor()
#     cursor.execute("SELECT id, created_at, status FROM orders")
#     rows = cursor.fetchall()
#     con.close()
#
#     orders = []
#     for row in rows:
#         orders.append({
#             "id": row[0],
#             "created_at": row[1],
#             "status": row[2],
#         })
#
#     return orders
#
#
# @app.get("/orders/{order_id}")
# def get_order(order_id: int):
#     con = sqlite3.connect("warehouse.db")
#     cursor = con.cursor()
#
#     cursor.execute("SELECT id, created_at, status FROM orders WHERE id = ?", (order_id,))
#     order = cursor.fetchone()
#     if not order:
#         con.close()
#         raise HTTPException(status_code=404, detail="Order not found")
#
#     cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = ?", (order_id,))
#     items = cursor.fetchall()
#     con.close()
#
#     return {
#         "id": order[0],
#         "created_at": order[1],
#         "status": order[2],
#         "items": [{"product_id": row[0], "quantity": row[1]} for row in items]
#     }
#
# @app.patch("/orders/{order_id}/status")
# def update_order_status(order_id: int, status_update: OrderStatusUpdate):
#     con = sqlite3.connect("warehouse.db")
#     cursor = con.cursor()
#
#     cursor.execute("SELECT id FROM orders WHERE id = ?", (order_id,))
#     if not cursor.fetchone():
#         con.close()
#         raise HTTPException(status_code=404, detail="Order not found")
#
#     cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status_update.status, order_id))
#     con.commit()
#     con.close()
#     return {"message": "Order status updated", "order_id": order_id, "new_status": status_update.status}
