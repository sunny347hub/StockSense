CREATE DATABASE IF NOT EXISTS stocksense;

USE stocksense;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE warehouses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
        ON DELETE CASCADE
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    category_id INT,
    unit VARCHAR(50) NOT NULL,
    initial_stock DECIMAL(12,2) DEFAULT 0,
    reorder_level DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
        ON DELETE SET NULL
);

CREATE TABLE stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity DECIMAL(12,2) DEFAULT 0,
    UNIQUE(product_id, location_id),
    FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id)
        ON DELETE CASCADE
);

CREATE TABLE receipts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier VARCHAR(150) NOT NULL,
    status ENUM('Draft', 'Waiting', 'Ready', 'Done', 'Canceled')
        DEFAULT 'Draft',
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE TABLE receipt_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receipt_id INT NOT NULL,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (receipt_id) REFERENCES receipts(id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id)
        ON DELETE CASCADE
);

CREATE TABLE deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer VARCHAR(150) NOT NULL,
    status ENUM('Draft', 'Waiting', 'Ready', 'Done', 'Canceled')
        DEFAULT 'Draft',
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE TABLE delivery_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    delivery_id INT NOT NULL,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (delivery_id) REFERENCES deliveries(id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id)
        ON DELETE CASCADE
);

CREATE TABLE transfers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_location_id INT NOT NULL,
    destination_location_id INT NOT NULL,
    status ENUM('Draft', 'Waiting', 'Ready', 'Done', 'Canceled')
        DEFAULT 'Draft',
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_location_id) REFERENCES locations(id),
    FOREIGN KEY (destination_location_id) REFERENCES locations(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE TABLE transfer_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transfer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (transfer_id) REFERENCES transfers(id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE CASCADE
);

CREATE TABLE adjustments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    location_id INT NOT NULL,
    old_quantity DECIMAL(12,2) NOT NULL,
    counted_quantity DECIMAL(12,2) NOT NULL,
    difference DECIMAL(12,2) NOT NULL,
    reason VARCHAR(255),
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE TABLE stock_ledger (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    operation_type ENUM(
        'RECEIPT',
        'DELIVERY',
        'TRANSFER',
        'ADJUSTMENT'
    ) NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    source_location_id INT,
    destination_location_id INT,
    reference_id INT,
    performed_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (source_location_id) REFERENCES locations(id)
        ON DELETE SET NULL,
    FOREIGN KEY (destination_location_id) REFERENCES locations(id)
        ON DELETE SET NULL,
    FOREIGN KEY (performed_by) REFERENCES users(id)
        ON DELETE SET NULL
);