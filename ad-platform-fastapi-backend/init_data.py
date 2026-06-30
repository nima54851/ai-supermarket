from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from auth import get_password_hash
from datetime import datetime, timedelta

def init_database():
    """初始化数据库和测试数据"""
    # 创建所有表
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已有数据
        user_count = db.query(models.User).count()
        
        if user_count == 0:
            print("初始化数据库数据...")
            
            # 创建测试用户
            test_users = [
                {
                    "email": "admin@adplatform.com",
                    "username": "admin",
                    "password_hash": get_password_hash("Admin@123"),
                    "full_name": "系统管理员",
                    "role": "superadmin",
                    "email_verified": True
                },
                {
                    "email": "user1@example.com",
                    "username": "user1",
                    "password_hash": get_password_hash("User@123"),
                    "full_name": "张三",
                    "role": "user",
                    "email_verified": True
                },
                {
                    "email": "user2@example.com",
                    "username": "user2",
                    "password_hash": get_password_hash("User@123"),
                    "full_name": "李四",
                    "role": "user",
                    "email_verified": True
                }
            ]
            
            for user_data in test_users:
                user = models.User(**user_data)
                db.add(user)
            
            db.commit()
            print("✓ 用户数据创建完成")
            
            # 创建会员套餐
            membership_plans = [
                {
                    "name": "基础版",
                    "description": "适合个人用户和小型项目",
                    "price": 19.99,
                    "currency": "USD",
                    "duration_days": 30,
                    "features": ["5个广告位", "基础数据分析", "邮件支持"],
                    "is_active": True,
                    "sort_order": 1
                },
                {
                    "name": "专业版",
                    "description": "适合中小企业",
                    "price": 49.99,
                    "currency": "USD",
                    "duration_days": 30,
                    "features": ["20个广告位", "高级数据分析", "API访问", "优先支持"],
                    "is_active": True,
                    "sort_order": 2
                },
                {
                    "name": "企业版",
                    "description": "适合大型企业和机构",
                    "price": 199.99,
                    "currency": "USD",
                    "duration_days": 30,
                    "features": ["无限广告位", "完整数据分析", "定制API", "专属客服", "白标签解决方案"],
                    "is_active": True,
                    "sort_order": 3
                }
            ]
            
            for plan_data in membership_plans:
                plan = models.MembershipPlan(**plan_data)
                db.add(plan)
            
            db.commit()
            print("✓ 会员套餐创建完成")
            
            # 创建测试广告
            users = db.query(models.User).all()
            plans = db.query(models.MembershipPlan).all()
            
            if users and plans:
                # 为用户1创建广告
                test_ads = [
                    {
                        "user_id": users[1].id,  # user1
                        "title": "夏季促销活动",
                        "description": "夏季商品大促销，限时抢购",
                        "content": "夏季服装、鞋子、配饰全场5折起！",
                        "media_urls": ["https://example.com/ad1.jpg"],
                        "category": "电商",
                        "target_url": "https://example.com/summer-sale",
                        "budget": 500.0,
                        "status": "active",
                        "impressions": 1250,
                        "clicks": 85,
                        "ctr": 6.8
                    },
                    {
                        "user_id": users[1].id,
                        "title": "新产品发布",
                        "description": "全新智能手表发布",
                        "content": "功能强大的智能手表，支持健康监测和支付功能",
                        "media_urls": ["https://example.com/ad2.jpg"],
                        "category": "科技",
                        "target_url": "https://example.com/smartwatch",
                        "budget": 1000.0,
                        "status": "active",
                        "impressions": 3200,
                        "clicks": 240,
                        "ctr": 7.5
                    }
                ]
                
                for ad_data in test_ads:
                    ad = models.Ad(**ad_data)
                    db.add(ad)
                
                db.commit()
                print("✓ 测试广告创建完成")
                
                # 创建测试订单
                test_orders = [
                    {
                        "user_id": users[1].id,
                        "plan_id": plans[0].id,  # 基础版
                        "amount": plans[0].price,
                        "status": "paid",
                        "payment_method": "paypal",
                        "payment_id": "PAY-123456789",
                        "payment_at": datetime.now() - timedelta(days=5)
                    },
                    {
                        "user_id": users[2].id,
                        "plan_id": plans[1].id,  # 专业版
                        "amount": plans[1].price,
                        "status": "pending",
                        "payment_method": "stripe"
                    }
                ]
                
                for order_data in test_orders:
                    order = models.Order(**order_data)
                    db.add(order)
                
                db.commit()
                print("✓ 测试订单创建完成")
                
                # 创建测试订阅
                test_subscriptions = [
                    {
                        "user_id": users[1].id,
                        "plan_id": plans[0].id,
                        "start_date": datetime.now() - timedelta(days=30),
                        "end_date": datetime.now() + timedelta(days=30),
                        "is_active": True,
                        "auto_renew": True
                    }
                ]
                
                for sub_data in test_subscriptions:
                    subscription = models.Subscription(**sub_data)
                    db.add(subscription)
                
                db.commit()
                print("✓ 测试订阅创建完成")
                
                # 创建测试统计数据
                import random
                from datetime import date, timedelta
                
                for i in range(7):
                    stat_date = date.today() - timedelta(days=i)
                    stat = models.Statistic(
                        date=stat_date.strftime("%Y-%m-%d"),
                        user_count=random.randint(100, 200),
                        order_count=random.randint(10, 50),
                        revenue=random.uniform(500, 2000),
                        ad_impressions=random.randint(1000, 5000),
                        ad_clicks=random.randint(50, 300),
                        ctr=random.uniform(3, 8)
                    )
                    db.add(stat)
                
                db.commit()
                print("✓ 测试统计数据创建完成")
            
            print("✅ 数据库初始化完成！")
        else:
            print("数据库已有数据，跳过初始化")
            
    except Exception as e:
        db.rollback()
        print(f"数据库初始化失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()