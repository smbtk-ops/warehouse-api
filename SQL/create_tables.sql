CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    price REAL,
    quantity INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    created_at TEXT,
    status TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);