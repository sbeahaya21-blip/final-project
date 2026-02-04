# Intro to SQL databases

## SQL vs NoSql

SQL and NoSQL are two different types of database management systems, each have its own strengths and weaknesses.

Let's explore the key differences between them:

- **Data Model**:

  SQL databases use a **structured data model** where data is organized into **tables** with **predefined** schemas.
  Each table contains rows and columns, and **relationships** between tables are established through **keys**.

  Let's consider a simple relational database scenario with three tables: invoices, confidences, and items. These tables will demonstrate how relationships are established through keys.

    ```mermaid
    erDiagram
        INVOICES ||--|| CONFIDENCES : has
        INVOICES ||--|{ ITEMS : contains
        
        INVOICES {
            string InvoiceId PK
            string VendorName
            string InvoiceDate
            string BillingAddressRecipient
            string ShippingAddress
            real SubTotal
            real ShippingCost
            real InvoiceTotal
        }
        
        CONFIDENCES {
            string InvoiceId PK
            real VendorName
            real InvoiceDate
            real BillingAddressRecipient
            real ShippingAddress
            real SubTotal
            real ShippingCost
            real InvoiceTotal
        }
        
        ITEMS {
            int id PK
            string InvoiceId FK
            string Description
            string Name
            real Quantity
            real UnitPrice
            real Amount
        }
    ```   

  On the other side, NoSQL databases use a more flexible data model that allows for storing **unstructured** or semi-structured data.
  They can include various data structures like key-value pairs, documents, columns, and graphs.

  Example given:

    ```json
    {
        "_id": ObjectId("5f4dbdbb8cc835a3b4cf979e"),
        "InvoiceId": "INV-2024-001",
        "VendorName": "Acme Corporation",
        "InvoiceDate": "2024-01-15",
        "BillingAddressRecipient": "John Doe, 123 Main St",
        "ShippingAddress": "456 Oak Ave",
        "SubTotal": 1250.00,
        "ShippingCost": 50.00,
        "InvoiceTotal": 1300.00,
        "items": [
            {
                "Description": "Premium Widget",
                "Name": "Widget-A",
                "Quantity": 10,
                "UnitPrice": 100.00,
                "Amount": 1000.00
            },
            {
                "Description": "Standard Gadget",
                "Name": "Gadget-B",
                "Quantity": 5,
                "UnitPrice": 50.00,
                "Amount": 250.00
            }
        ],
        "confidences": {
            "VendorName": 0.98
        }
    ```

- **Scalability**

  In general, SQL databases can scale **vertically**, meaning you can increase the load on a server by migrating to a larger server that adds more CPU, RAM or SSD capability.

  ![][aws_vertical]

  For example, if our YOLO prediction service gets popular and receives thousands of image uploads per day, we might need to upgrade our server to handle more prediction sessions and detection objects stored in our SQL database.

  **Horizontal** scaling involves adding more nodes to the database cluster to distribute the load and increase the overall capacity of the system, it's very hard to achieve horizontal scaling in relational databases.

  ![][horizontal]

  NoSQL databases are designed for horizontal scalability, allowing them to distribute data across multiple servers or nodes.
  This makes them well-suited for handling large amounts of data and high traffic. For our invoice parsing service, this means we could easily add more servers to store millions of invoice documents as our user base grows.

- **Data consistency, data availability and partition tolerance (CAP)**:

  SQL databases prioritize **consistency** and **partition tolerance**. They adhere to [ACID (Atomicity, Consistency, Isolation, Durability)](https://en.wikipedia.org/wiki/ACID) properties.
  This ensures that data remains accurate and reliable but can sometimes affect availability during failures.

  For our invoice parsing service, this means that when we save an invoice and its line items, either **all** the data is saved correctly, or **none** of it is saved. This prevents incomplete invoices from being stored.

  NoSQL databases often prioritize **availability** and **partition tolerance**.  
  This might result in eventual consistency, where data might be slightly outdated but the system remains available.

  In our invoice parsing service context, this means users can always upload invoices and get them parsed even if some servers are down, but they might occasionally see slightly outdated invoice history until all servers sync up.

  There is no distributed database in the world (and there will never be such one) that can both be 100% consistent, highly available, and durable (can recover from disk failure).
  This statement was proved in 1998 and referred to as the [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem).

  ![][aws_cap]

  In real life, both SQL and NoSql databases achieve very good levels of consistency, high availability and durability.


## SQLite

We'll practice on a lightweight SQL database named SQLite, which is used in our invoice parsing service.

SQLite comes built-in with Python, so no installation is needed! We'll use simple Python code to interact with the database.

## SQL 

SQL (Structured Query Language) is a standard programming language used to manage and manipulate relational databases.

Let's practice it a bit using Python...

### The `SELECT` statement

1. Show the InvoiceId and VendorName of all invoices:

```python
import sqlite3

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

cursor.execute("SELECT InvoiceId, VendorName FROM invoices")
results = cursor.fetchall()
for row in results:
    print(row)

conn.close()
```

2. Use a `WHERE` clause to show all columns of invoice with `InvoiceId` of `INV-2024-001`.
   Note that strings should be in 'single quotes'.

```python
import sqlite3

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM invoices WHERE InvoiceId = 'INV-2024-001'")
results = cursor.fetchall()
for row in results:
    print(row)

conn.close()
```

3. Find the total count and average amount of all items in a specific invoice:

```python
import sqlite3

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*), AVG(Amount) FROM items WHERE InvoiceId = 'INV-2024-001'")
result = cursor.fetchone()
print(f"Count: {result[0]}, Average: {result[1]}")

conn.close()
```

2. `ORDER BY` permits us to see the result of a `SELECT` in any particular order. We may indicate `ASC` or `DESC` for ascending (smallest first, largest last) or descending order.

   Find invoices with a total greater than 1000, ordered by total in descending order

```python
import sqlite3

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT InvoiceId, VendorName, InvoiceTotal
    FROM invoices
    WHERE InvoiceTotal > 1000
    ORDER BY InvoiceTotal DESC
""")
results = cursor.fetchall()
for row in results:
    print(row)

conn.close()
```ults = cursor.fetchall()
for row in results:
    print(row)

conn.close()
```

5. Find high-value invoices from a specific vendor:

```python
import sqlite3

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT InvoiceId, InvoiceTotal
    FROM invoices
    WHERE VendorName = 'Acme Corporation' AND InvoiceTotal >= 1000
""")
results = cursor.fetchall()
for row in results:
    print(row)

conn.close()
```

### Aggregates

1. The functions `SUM`, `COUNT`, `MAX` and `AVG` are "aggregates", each may be applied to a numeric attribute resulting in a single row being returned by the query. (Very useful when used with the `GROUP BY` clause.)

### `JOIN` queries 

`JOIN` allows you to use data from two or more tables.

Let's say we want a table of all line items, but with the vendor name and invoice date in each row: 

```python
import sqlite3

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT items.*, invoices.VendorName, invoices.InvoiceDate
    FROM items
    JOIN invoices ON items.InvoiceId = invoices.InvoiceId
""")
results = cursor.fetchall()
for row in results:
    print(row)

conn.close()
```

The JOIN query basically does the following:

1. Go to the `items` table.
2. In each row, take the `InvoiceId` and search the corresponding row in `invoices` table. 
3. Display everything in joint table.


# Exercises 

### :pencil2: Practice queries

- Show items with `Name` that includes the word `Widget`. 
- An extraction is considered "reliable" if the confidence is greater than 0.9. Find all invoices with reliable VendorName extraction (`JOIN` with confidences table).
- Find the item with the highest Amount in the dataset (`ORDER BY`, `LIMIT`).
- Count the number of items in each invoice (`COUNT`, `GROUP BY`).
- Find all invoices that have at least one item (`JOIN`).
- Find the invoice ID and vendor name for all items with UnitPrice > 100 (`JOIN`).


[aws_vertical]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_vertical.png
[horizontal]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_horizontal.png
[aws_cap]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_cap.png