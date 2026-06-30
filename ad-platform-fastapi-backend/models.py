from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    avatar_url = Column(String)
    role = Column(String, default="user")  # user, admin, superadmin
    telegram_id = Column(String, unique=True)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    ads = relationship("Ad", back_populates="owner")
    orders = relationship("Order", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")

class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    duration_days = Column(Integer, nullable=False)
    features = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    subscriptions = relationship("Subscription", back_populates="plan")
    orders = relationship("Order", back_populates="plan")

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=list)
    category = Column(String)
    target_url = Column(String)
    budget = Column(Float, nullable=False)
    spent = Column(Float, default=0.0)
    status = Column(String, default="draft")  # draft, pending, approved, active, paused, completed
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    targeting = Column(JSON, default=dict)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    owner = relationship("User", back_populates="ads")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("membership_plans.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="pending")  # pending, paid, failed, refunded
    payment_method = Column(String)
    payment_id = Column(String)
    invoice_url = Column(String)
    payment_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="orders")
    plan = relationship("MembershipPlan", back_populates="orders")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("membership_plans.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("MembershipPlan", back_populates="subscriptions")

class Statistic(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)  # YYYY-MM-DD格式
    user_count = Column(Integer, default=0)
    order_count = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    ad_impressions = Column(Integer, default=0)
    ad_clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())