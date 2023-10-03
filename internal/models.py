from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import (
    Boolean, 
    Column, 
    ForeignKey, 
    Integer, 
    String ,
    DateTime, 
    func,
    LargeBinary
    )



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Integer, unique=True , index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_customer = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    products = relationship("Product", back_populates="user")
    profile =relationship("Profile", back_populates="user")
    orders = relationship("Order", back_populates="users")
    payments = relationship("Payment", back_populates="users")
    
    
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(LargeBinary)
    address = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="profile")
    
    
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    products = relationship("Product" , back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Integer, index=True)
    stock =Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    user = relationship("User", back_populates="products")
    orders = relationship("Order", back_populates="products")
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage" , back_populates="product")
    
class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    image = Column(LargeBinary)
    product =relationship("Product" , back_populates="images")
    
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    total_price = Column(Integer, index=True)
    is_payed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    users = relationship("User", back_populates="orders")
    products = relationship("Product", back_populates="orders")
    payments =relationship("Payment" , back_populates="orders")
    
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    type_of_payment = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    
    users =relationship("User" , back_populates="payments")
    orders =relationship("Order" , back_populates="payments")
