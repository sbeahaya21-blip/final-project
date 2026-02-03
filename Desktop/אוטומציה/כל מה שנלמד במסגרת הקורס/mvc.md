# The Models-Views-Controllers pattern in Fast API

In web development, we often use a structure called **Model–View–Controller (MVC)**:

- **Model**: The part that deals with the data (e.g., database tables).
- **View**: The part that shows the data (e.g., HTML pages or JSON responses).
- **Controller**: The part that handles user input (e.g., HTTP requests), and connects everything.

When building APIs, the **View** is the JSON response returned to the client. The View represents how data is presented to the consumer of your API.

In our Invoice Parser app, we write something like:

```python
@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    
    # ... process document with OCI AI ...
    
    result = {
        "confidence": "...",
        "data": "...",
        "dataConfidence": "..."
    }

    save_inv_extraction(result)

    return result
```


Here, your API endpoint:

1. Receives the request,
2. Talks directly to the database,
3. Returns the result.

This might seem simple, but it mixes everything together, which makes it error prone, hard to maintain, and difficult to test. 

## Introducing SQLAchemy

To solve this, we use **SQLAlchemy**, a powerful library that helps us work with databases in a cleaner way.

#### Modeling the data

In SQLAlchemy, you write **Python classes** instead of **SQL tables**:

```python
# models.py

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# All models inherit from this base class
Base = declarative_base()


class Invoice(Base):
    """
    Model for invoices table
    
    This replaces: CREATE TABLE invoices (...)
    """
    __tablename__ = 'invoices'
    
    InvoiceId = Column(String, primary_key=True)
    VendorName = Column(String)
    InvoiceDate = Column(String)
    BillingAddressRecipient = Column(String)
    ShippingAddress = Column(String)
    SubTotal = Column(Float)
    ShippingCost = Column(Float)
    InvoiceTotal = Column(Float)
    
    # Relationships
    confidences = relationship("Confidence", back_populates="invoice")
    items = relationship("Item", back_populates="invoice")


class Confidence(Base):
    __tablename__ = 'confidences'
    
    InvoiceId = Column(String, ForeignKey('invoices.InvoiceId'), primary_key=True)
    VendorName = Column(Float)
    InvoiceDate = Column(Float)
    BillingAddressRecipient = Column(Float)
    ShippingAddress = Column(Float)
    SubTotal = Column(Float)
    ShippingCost = Column(Float)
    InvoiceTotal = Column(Float)
    
    invoice = relationship("Invoice", back_populates="confidences")


class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    InvoiceId = Column(String, ForeignKey('invoices.InvoiceId'))
    Description = Column(String)
    Name = Column(String)
    Quantity = Column(Float)
    UnitPrice = Column(Float)
    Amount = Column(Float)
    
    invoice = relationship("Invoice", back_populates="items")
```

- **Model** → A Python class that represents a database table
- **Class Attribute** → Database Column  
- **Class Instance** → Database Row

#### Database connection 

To manage database connections and sessions, we create a separate file called `db.py`:

```python
# db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./invoices.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed when working with SQLite in FastAPI
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```


#### Database operations

Now, instead the following `INSERT` statement:

```python
cursor.execute("""
    INSERT OR REPLACE INTO invoices 
    (InvoiceId, VendorName, InvoiceDate, BillingAddressRecipient, 
     ShippingAddress, SubTotal, ShippingCost, InvoiceTotal)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (invoice_id, vendor_name, invoice_date, ...))
```

We can do:

```python
from db import get_db
from models import Invoice

db = get_db()

def save_invoice(data: dict):   
    # Create a new Invoice instance
    invoice = Invoice(
        InvoiceId=data.get("InvoiceId"),
        VendorName=data.get("VendorName"),
        InvoiceDate=data.get("InvoiceDate"),
        BillingAddressRecipient=data.get("BillingAddressRecipient"),
        ShippingAddress=data.get("ShippingAddress"),
        SubTotal=data.get("SubTotal"),
        ShippingCost=data.get("ShippingCost"),
        InvoiceTotal=data.get("InvoiceTotal")
    )
    
    # Add the instance to the session and commit
    db.add(invoice)
    db.commit()
```

To query the database, instead of using raw SQL like this:

```python
result = conn.execute("SELECT * FROM invoices WHERE InvoiceId = ?", (invoice_id,)).fetchone()
```

We do: 

```python
from db import get_db
from models import Invoice

db = get_db()

def get_invoice_by_id(invoice_id: str):
    result = db.query(Invoice).filter_by(InvoiceId=invoice_id).first()
    return result
```

#### FastAPI integration 

Here is how we can integrate SQLAlchemy with FastAPI to handle the `GET /invoice/{invoice_id}` endpoint:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Invoice

def query_invoice_by_id(db: Session, invoice_id: str):
    result = db.query(Invoice).filter_by(InvoiceId=invoice_id).first()
    return result

@app.get("/invoice/{invoice_id}")
def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    invoice = query_invoice_by_id(db, invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return {
        "InvoiceId": invoice.InvoiceId,
        "VendorName": invoice.VendorName,
        "InvoiceDate": invoice.InvoiceDate,
        "InvoiceTotal": invoice.InvoiceTotal
    }
```


This way, we separate the data structure (model) from the logic (controller), making it cleaner and easier to manage.

There are many benefits to this approach:

- We work with Python classes instead raw SQL strings
- DB connections is done automatically  
- IDE autocomplete and type safety


## Database agnostic code

Right now, your code is hardcoded to use SQLite. But what if you want to use PostgreSQL in production, and SQLite for local development/testing?

We can make our app **database agnostic**, meaning it can work with any supported database, as long as we provide the right connection string.

```python
# db.py


import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite")

if DB_BACKEND == "postgres":
    DATABASE_URL = "postgresql://user:pass@localhost/db"
else:
    DATABASE_URL = "sqlite:///./invoices.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

# Exercises 

### :pencil2: Model-View-Controller structure

Implement the Model-View-Controller structure in your FastAPI application, follow these steps:


- Install SQLAlchemy and add it to your `requirements.txt`:
  ```bash
  pip install sqlalchemy
  ```
- In `models.py` create model classes (`Invoice`, `Confidence`, `Item`). 
- Use the provided `db.py` file to connect to the database.
- Create `queries.py` file to handle database operations (`get_invoice_by_id()`, `save_inv_extraction()`, etc.).
- Make sure to remove any existing raw SQL queries from your FastAPI app, including `init_db()`.
- Update your tests to use the new model-view-controller structure.