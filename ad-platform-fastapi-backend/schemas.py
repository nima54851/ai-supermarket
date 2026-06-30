from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# 基础schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

# 用户相关
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    telegram_id: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    telegram_id: Optional[str] = None
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 会员套餐
class MembershipPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    currency: str = "USD"
    duration_days: int = Field(..., gt=0)
    features: List[str] = []

class MembershipPlanCreate(MembershipPlanBase):
    pass

class MembershipPlanResponse(MembershipPlanBase):
    id: int
    is_active: bool
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True

# 广告相关
class AdStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class AdBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    media_urls: List[str] = []
    category: Optional[str] = None
    target_url: str
    budget: float = Field(..., gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    targeting: Dict[str, Any] = {}

class AdCreate(AdBase):
    pass

class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    media_urls: Optional[List[str]] = None
    category: Optional[str] = None
    target_url: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[AdStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    targeting: Optional[Dict[str, Any]] = None

class AdResponse(AdBase):
    id: int
    user_id: int
    status: str
    spent: float
    impressions: int
    clicks: int
    ctr: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 订单相关
class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class OrderBase(BaseModel):
    plan_id: int
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    payment_method: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: str
    payment_id: Optional[str] = None
    invoice_url: Optional[str] = None
    payment_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 订阅相关
class SubscriptionBase(BaseModel):
    plan_id: int
    auto_renew: bool = True

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 统计相关
class StatisticBase(BaseModel):
    date: str  # YYYY-MM-DD
    user_count: int = 0
    order_count: int = 0
    revenue: float = 0.0
    ad_impressions: int = 0
    ad_clicks: int = 0
    ctr: float = 0.0

class StatisticResponse(StatisticBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 仪表板数据
class DashboardOverview(BaseModel):
    total_users: int
    active_users: int
    total_orders: int
    total_revenue: float
    active_ads: int
    total_impressions: int
    total_clicks: int
    overall_ctr: float

class RevenueTrend(BaseModel):
    date: str
    revenue: float
    orders: int

class UserGrowth(BaseModel):
    date: str
    new_users: int
    total_users: int

# Webhook相关
class PaymentWebhook(BaseModel):
    payment_id: str
    order_id: int
    status: str
    amount: float
    currency: str
    timestamp: datetime
    signature: Optional[str] = None