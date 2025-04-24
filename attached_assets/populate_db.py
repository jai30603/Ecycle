from app import app, db
from models import User, Admin, Ewaste, Schedule, Reward, Redemption
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

# Updated e-waste types based on Roboflow API classes
ewaste_types = [
    'Air-Conditioner', 'Smartphone', 'Battery', 'Blood-Pressure-Monitor', 'Laptop',
    'CRT-Monitor', 'CRT-TV', 'Calculator', 'Camera', 'Ceiling-Fan',
    'Clothes-Iron', 'Coffee-Machine', 'Computer-Keyboard', 'Computer-Mouse',
    'Desktop-PC', 'Dishwasher', 'Drone', 'Flat-Panel-Monitor', 'Flat-Panel-TV',
    'Freezer', 'Headphone', 'LED-Bulb', 'Microwave', 'Music-Player',
    'Printer', 'Projector', 'Router', 'Smart-Watch', 'Speaker',
    'Tablet', 'Toaster', 'Vacuum-Cleaner', 'Washing-Machine', 'USB-Flash-Drive'
]
conditions = ['Excellent', 'Good', 'Fair', 'Poor']
models = ['Model A', 'Model B', 'Model C', 'Model X', 'Model Y', 'Model Z']
ram_options = ['2GB', '4GB', '8GB', '16GB', '32GB']
statuses = ['Pending', 'Collected']

with app.app_context():
    # Clean existing data
    Redemption.query.delete()
    Reward.query.delete()
    Schedule.query.delete()
    Ewaste.query.delete()
    User.query.delete()
    
    # Create test users
    users = []
    for i in range(1, 6):
        user = User(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password_hash=generate_password_hash(f'password{i}'),
            eco_points=random.randint(10, 200),
            carbon_saved=random.uniform(5.0, 50.0)
        )
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    
    # Create ewaste items and schedules
    for user in users:
        # Each user has 3-6 e-waste items to showcase more variety
        for _ in range(random.randint(3, 6)):
            ewaste_type = random.choice(ewaste_types)
            
            # Set appropriate price ranges based on item type
            if ewaste_type in ['Laptop', 'Smartphone', 'Desktop-PC', 'Flat-Panel-TV']:
                price_range = (100, 800)
            elif ewaste_type in ['Air-Conditioner', 'Washing-Machine', 'Dishwasher', 'Freezer']:
                price_range = (80, 500)
            elif ewaste_type in ['Camera', 'Smart-Watch', 'Headphone', 'Projector']:
                price_range = (50, 300)
            else:
                price_range = (20, 200)
                
            # Adjust eco points based on item type
            if ewaste_type in ['Laptop', 'Desktop-PC', 'Flat-Panel-TV']:
                eco_points_range = (30, 80)
            elif ewaste_type in ['Smartphone', 'Tablet', 'Camera']:
                eco_points_range = (20, 50)
            else:
                eco_points_range = (10, 40)
            
            # Create e-waste item
            ewaste = Ewaste(
                user_id=user.id,
                ewaste_type=ewaste_type,
                model=random.choice(models),
                ram=random.choice(ram_options) if ewaste_type in ['Laptop', 'Desktop-PC', 'Tablet'] else None,
                condition=random.choice(conditions),
                estimated_price=random.randint(*price_range),
                eco_points=random.randint(*eco_points_range),
                classification_result='{"predictions": [{"class": "' + ewaste_type + '", "confidence": 0.95}]}'
            )
            db.session.add(ewaste)
            db.session.flush()  # Get the ewaste.id
            
            # Create schedule for pickup
            days_offset = random.randint(-14, 21)  # Past and future dates
            pickup_date = datetime.now() + timedelta(days=days_offset)
            
            schedule = Schedule(
                user_id=user.id,
                ewaste_id=ewaste.id,
                pickup_date=pickup_date,
                pickup_address=f"{random.randint(1, 999)} {random.choice(['Main St', 'Oak Ave', 'Maple Rd', 'Pine Blvd'])}, Apt {random.randint(1, 100)}, {random.choice(['Springfield', 'Riverside', 'Greenwood', 'Fairview'])}, State, Zip",
                status='Collected' if days_offset < 0 else 'Pending'
            )
            db.session.add(schedule)
    
    db.session.commit()
    
    # Create sample rewards
    rewards = [
        {
            'name': 'Refurbished Tablet',
            'description': 'A fully refurbished and sanitized tablet ready for use. Perfect for reading, browsing, or as a backup device.',
            'points_required': 500,
            'reward_type': 'Product',
            'stock': 5,
            'image_path': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'active': True
        },
        {
            'name': 'Wireless Earbuds',
            'description': 'Refurbished wireless earbuds with charging case. Great sound quality and battery life.',
            'points_required': 300,
            'reward_type': 'Product',
            'stock': 10,
            'image_path': 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'active': True
        },
        {
            'name': '20% Off Next Pickup',
            'description': 'Get 20% bonus eco points on your next e-waste pickup. Valid for 3 months.',
            'points_required': 100,
            'reward_type': 'Discount',
            'stock': 50,
            'image_path': '',
            'active': True
        },
        {
            'name': '$25 Electronics Store Gift Card',
            'description': 'A $25 gift card for any participating electronics retailer. Use it towards your next purchase!',
            'points_required': 250,
            'reward_type': 'Coupon',
            'stock': 15,
            'image_path': 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'active': True
        },
        {
            'name': 'Recycled Phone Case',
            'description': 'Stylish phone case made from 100% recycled materials. Available for most popular phone models.',
            'points_required': 150,
            'reward_type': 'Product',
            'stock': 20,
            'image_path': 'https://images.unsplash.com/photo-1622467827417-bbe2237067a9?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'active': True
        },
        {
            'name': 'Free E-waste Pickup',
            'description': 'Get a free premium pickup service for your next e-waste recycling, including assistance with heavy items.',
            'points_required': 200,
            'reward_type': 'Coupon',
            'stock': 8,
            'image_path': '',
            'active': True
        }
    ]
    
    reward_objects = []
    for reward_data in rewards:
        reward = Reward(
            name=reward_data['name'],
            description=reward_data['description'],
            points_required=reward_data['points_required'],
            reward_type=reward_data['reward_type'],
            stock=reward_data['stock'],
            image_path=reward_data['image_path'],
            active=reward_data['active']
        )
        db.session.add(reward)
        reward_objects.append(reward)
    
    db.session.commit()
    
    # Create sample redemptions
    redemption_statuses = ['Pending', 'Processed', 'Delivered']
    
    for user in users[:3]:  # Only some users have redemptions
        # Each user redeems 1-3 rewards
        for _ in range(random.randint(1, 3)):
            reward = random.choice(reward_objects)
            days_ago = random.randint(1, 30)
            
            # Check if user has enough points
            if user.eco_points >= reward.points_required:
                redemption = Redemption(
                    user_id=user.id,
                    reward_id=reward.id,
                    points_spent=reward.points_required,
                    status=random.choice(redemption_statuses),
                    redeemed_at=datetime.now() - timedelta(days=days_ago)
                )
                db.session.add(redemption)
                
                # Deduct points from user
                user.eco_points -= reward.points_required
                
                # Reduce stock
                reward.stock -= 1
    
    db.session.commit()
    
    print("Database populated with sample data!")
    print(f"Users created: {User.query.count()}")
    print(f"E-waste items created: {Ewaste.query.count()}")
    print(f"Schedules created: {Schedule.query.count()}")
    print(f"Rewards created: {Reward.query.count()}")
    print(f"Redemptions created: {Redemption.query.count()}")