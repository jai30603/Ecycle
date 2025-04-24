import os
import tempfile
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Admin, Ewaste, Schedule, Reward, Redemption
from utils import get_ewaste_news, calculate_carbon_footprint
from api import classify_image
from forms import LoginForm, RegisterForm, ScheduleForm, AdminLoginForm, RewardForm

@app.route('/')
def index():
    # Get latest news for the homepage
    news = get_ewaste_news()
    return render_template('index.html', news=news)

# Learning page with educational content about e-waste
@app.route('/learn')
def learn():
    return render_template('learn.html')

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please use a different one.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['eco_points'] = user.eco_points  # Store eco points in session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

# User logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('eco_points', None)  # Clear eco_points from session
    session.pop('admin_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# User dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # If user doesn't exist for some reason (maybe was deleted), redirect to login
    if not user:
        flash('User account not found. Please login again.', 'danger')
        session.pop('user_id', None)  # Clear the session
        session.pop('username', None)
        session.pop('eco_points', None)
        return redirect(url_for('login'))
    
    # Store eco points in session for display in navbar
    session['eco_points'] = user.eco_points
    
    # Get user's scheduled pickups
    pickups = Schedule.query.filter_by(user_id=user_id).all()
    
    # Get the latest news
    news = get_ewaste_news()
    
    # Get user's e-waste items and calculate statistics
    ewaste_items = Ewaste.query.filter_by(user_id=user_id).all()
    total_items = len(ewaste_items)
    total_carbon_saved = user.carbon_saved
    
    # Get completed pickups
    completed_pickups = Schedule.query.filter_by(user_id=user_id, status='Collected').count()
    
    # Get recent rewards
    recent_redemptions = Redemption.query.filter_by(user_id=user_id).order_by(Redemption.redeemed_at.desc()).limit(3).all()
    
    return render_template('dashboard.html', 
                          user=user, 
                          pickups=pickups, 
                          news=news, 
                          total_items=total_items,
                          total_carbon_saved=total_carbon_saved,
                          completed_pickups=completed_pickups,
                          recent_redemptions=recent_redemptions)

# Schedule new pickup (form)
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'user_id' not in session:
        flash('Please login to schedule a pickup.', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # If user doesn't exist for some reason (maybe was deleted), redirect to login
    if not user:
        flash('User account not found. Please login again.', 'danger')
        session.pop('user_id', None)  # Clear the session
        session.pop('username', None)
        session.pop('eco_points', None)
        return redirect(url_for('login'))
    
    # Store eco points in session for display in navbar
    session['eco_points'] = user.eco_points
    
    form = ScheduleForm()
    if form.validate_on_submit():
        ewaste_type = form.ewaste_type.data
        model = form.model.data
        ram = form.ram.data
        condition = form.condition.data
        pickup_date = form.pickup_date.data
        pickup_address = form.pickup_address.data
        
        # Calculate estimated price and eco points based on ewaste details
        # Comprehensive price map for all e-waste types
        price_map = {
            # High value items
            'Desktop-PC': 150,
            'Laptop': 120,
            'Server': 200,
            'PlayStation-5': 100,
            'Xbox-Series-X': 100,
            
            # Medium-high value items
            'Smartphone': 70,
            'Tablet': 80,
            'Flat-Panel-TV': 90,
            'Flat-Panel-Monitor': 70,
            'Digital-Oscilloscope': 150,
            'Printer': 60,
            'Air-Conditioner': 80,
            'Refrigerator': 70,
            'Washing-Machine': 70,
            'Dishwasher': 70,
            
            # Medium value items
            'CRT-Monitor': 50,
            'CRT-TV': 40,
            'Microwave': 50,
            'Coffee-Machine': 40,
            'Projector': 60,
            'Router': 40,
            'Network-Switch': 45,
            'Oven': 50,
            'Boiler': 40,
            'PCB': 30,
            'Electric-Guitar': 50,
            'Electronic-Keyboard': 55,
            'Drone': 60,
            'Electric-Bicycle': 90,
            'Cooled-Dispenser': 45,
            
            # Lower value items
            'Battery': 20,
            'Headphone': 25,
            'Computer-Keyboard': 20,
            'Computer-Mouse': 15,
            'Smart-Watch': 35,
            'Camera': 40,
            'Soldering-Iron': 25,
            'Bar-Phone': 20,
            'Hair-Dryer': 20,
            'Calculator': 15,
            'LED-Bulb': 10,
            'Flashlight': 15,
            'USB-Flash-Drive': 15,
            'HDD': 25,
            'SSD': 30,
            'Vacuum-Cleaner': 35,
            'Speaker': 30,
            'Toaster': 25,
            
            # Default for any other items
            'Other': 30
        }
        
        condition_multiplier = {
            'Excellent': 1.5,
            'Good': 1.2,
            'Fair': 1.0,
            'Poor': 0.8
        }
        
        base_price = price_map.get(ewaste_type, 30)
        estimated_price = int(base_price * condition_multiplier.get(condition, 1.0))
        eco_points = estimated_price // 10  # 1 eco point for every $10 of estimated value
        
        # Create new e-waste entry
        new_ewaste = Ewaste(
            user_id=user_id,
            ewaste_type=ewaste_type,
            model=model,
            ram=ram,
            condition=condition,
            estimated_price=estimated_price,
            eco_points=eco_points
        )
        
        db.session.add(new_ewaste)
        db.session.flush()  # Get the new_ewaste.id without committing
        
        # Create new schedule entry
        new_schedule = Schedule(
            user_id=user_id,
            ewaste_id=new_ewaste.id,
            pickup_date=pickup_date,
            pickup_address=pickup_address,
            status='Pending'
        )
        
        db.session.add(new_schedule)
        
        # Update user's eco points
        user = User.query.get(user_id)
        user.eco_points += eco_points
        # Update eco_points in session too
        session['eco_points'] = user.eco_points
        
        # Calculate carbon savings
        carbon_saved = calculate_carbon_footprint(ewaste_type)
        user.carbon_saved += carbon_saved
        
        db.session.commit()
        
        flash(f'Pickup scheduled successfully! You earned {eco_points} eco points and saved {carbon_saved} kg of CO2!', 'success')
        return redirect(url_for('history'))
    
    return render_template('schedule.html', form=form)

# Upload image for classification
@app.route('/classify', methods=['POST'])
def classify():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the uploaded file to a temporary location with the original filename
    original_filename = secure_filename(file.filename)
    _, temp_path = tempfile.mkstemp(suffix=f'_{original_filename}')
    
    try:
        # Save the image and print debug info
        file.save(temp_path)
        print(f"Processing image: {original_filename}, saved at: {temp_path}")
        
        # Classify the image using Roboflow API or mock function
        result = classify_image(temp_path)
        
        # Process the classification result
        detected_items = result.get('predictions', [])
        
        if not detected_items:
            if os.path.exists(temp_path):
                os.unlink(temp_path)  # Clean up on error
            return jsonify({'error': 'No e-waste detected in the image'}), 400
        
        # Get the item with highest confidence
        best_match = max(detected_items, key=lambda x: x.get('confidence', 0))
        
        # Debug the prediction result
        print(f"Classification result: {best_match.get('class', 'Unknown')} with confidence {best_match.get('confidence', 0):.2f}")
        
        # Create a comprehensive mapping from lowercase to proper case format
        class_to_type = {
            'air-conditioner': 'Air-Conditioner',
            'bar-phone': 'Bar-Phone',
            'battery': 'Battery',
            'blood-pressure-monitor': 'Blood-Pressure-Monitor',
            'boiler': 'Boiler',
            'crt-monitor': 'CRT-Monitor',
            'crt-tv': 'CRT-TV',
            'calculator': 'Calculator',
            'camera': 'Camera',
            'ceiling-fan': 'Ceiling-Fan',
            'christmas-lights': 'Christmas-Lights',
            'clothes-iron': 'Clothes-Iron',
            'coffee-machine': 'Coffee-Machine',
            'compact-fluorescent-lamps': 'Compact-Fluorescent-Lamps',
            'computer-keyboard': 'Computer-Keyboard',
            'computer-mouse': 'Computer-Mouse',
            'cooled-dispenser': 'Cooled-Dispenser',
            'cooling-display': 'Cooling-Display',
            'dehumidifier': 'Dehumidifier',
            'desktop-pc': 'Desktop-PC',
            'desktop': 'Desktop-PC',
            'digital-oscilloscope': 'Digital-Oscilloscope',
            'dishwasher': 'Dishwasher',
            'drone': 'Drone',
            'electric-bicycle': 'Electric-Bicycle',
            'electric-guitar': 'Electric-Guitar',
            'electrocardiograph-machine': 'Electrocardiograph-Machine',
            'electronic-keyboard': 'Electronic-Keyboard',
            'exhaust-fan': 'Exhaust-Fan',
            'flashlight': 'Flashlight',
            'flat-panel-monitor': 'Flat-Panel-Monitor',
            'flat-panel-tv': 'Flat-Panel-TV',
            'monitor': 'Flat-Panel-Monitor',
            'tv': 'Flat-Panel-TV',
            'floor-fan': 'Floor-Fan',
            'freezer': 'Freezer',
            'glucose-meter': 'Glucose-Meter',
            'hdd': 'HDD',
            'hard disk': 'HDD',
            'hair-dryer': 'Hair-Dryer',
            'headphone': 'Headphone',
            'led-bulb': 'LED-Bulb',
            'laptop': 'Laptop',
            'microwave': 'Microwave',
            'music-player': 'Music-Player',
            'neon-sign': 'Neon-Sign',
            'network-switch': 'Network-Switch',
            'non-cooled-dispenser': 'Non-Cooled-Dispenser',
            'oven': 'Oven',
            'pcb': 'PCB',
            'patient-monitoring-system': 'Patient-Monitoring-System',
            'photovoltaic-panel': 'Photovoltaic-Panel',
            'playstation-5': 'PlayStation-5',
            'ps5': 'PlayStation-5',
            'power-adapter': 'Power-Adapter',
            'printer': 'Printer',
            'projector': 'Projector',
            'pulse-oximeter': 'Pulse-Oximeter',
            'range-hood': 'Range-Hood',
            'refrigerator': 'Refrigerator',
            'rotary-mower': 'Rotary-Mower',
            'router': 'Router',
            'ssd': 'SSD',
            'server': 'Server',
            'smart-watch': 'Smart-Watch',
            'smartphone': 'Smartphone',
            'mobile': 'Smartphone',
            'phone': 'Smartphone',
            'cell phone': 'Smartphone',
            'smoke-detector': 'Smoke-Detector',
            'soldering-iron': 'Soldering-Iron',
            'speaker': 'Speaker',
            'stove': 'Stove',
            'straight-tube-fluorescent-lamp': 'Straight-Tube-Fluorescent-Lamp',
            'street-lamp': 'Street-Lamp',
            'tv-remote-control': 'TV-Remote-Control',
            'remote': 'TV-Remote-Control',
            'table-lamp': 'Table-Lamp',
            'tablet': 'Tablet',
            'telephone-set': 'Telephone-Set',
            'toaster': 'Toaster',
            'tumble-dryer': 'Tumble-Dryer',
            'dryer': 'Tumble-Dryer',
            'usb-flash-drive': 'USB-Flash-Drive',
            'usb': 'USB-Flash-Drive',
            'vacuum-cleaner': 'Vacuum-Cleaner',
            'washing-machine': 'Washing-Machine',
            'washer': 'Washing-Machine',
            'xbox-series-x': 'Xbox-Series-X',
            'xbox': 'Xbox-Series-X'
        }
        
        # Extract the class name and standardize it
        detected_class = best_match.get('class', '')
        # Convert to lowercase for case-insensitive matching
        detected_class_lower = detected_class.lower()
        # Use the mapping if available, otherwise use the original class with proper capitalization
        ewaste_type = class_to_type.get(detected_class_lower, detected_class)
        confidence = best_match.get('confidence', 0) * 100
        
        # Recycling information for each e-waste type
        recycling_info = {
            'Battery': "Batteries contain hazardous materials like lead, cadmium, and mercury that can contaminate soil and water. They should be recycled at designated collection points. The metals can be extracted and reused in new batteries, reducing the need for mining raw materials.",
            
            'Smartphone': "Smartphones contain valuable materials like gold, silver, copper, and rare earth elements. These can be recovered during recycling. The circuit boards and components are processed to extract metals, while plastics are recycled separately. Always remove personal data before recycling.",
            
            'Laptop': "Laptops contain precious metals in their circuit boards, recyclable aluminum in their cases, and lithium in their batteries. Professional recyclers disassemble them to separate valuable components. The battery should be removed and recycled separately due to its hazardous materials.",
            
            'Desktop-PC': "Desktop computers contain recoverable materials like aluminum, copper, gold, and silver. Their large size means more materials can be reclaimed. The hard drives should be properly wiped or physically destroyed to protect personal data before recycling.",
            
            'Flat-Panel-Monitor': "Flat panel monitors contain mercury in their backlights and valuable metals in their circuit boards. They should be recycled at e-waste facilities equipped to handle them. The glass, plastic, and metal components are separated and processed individually.",
            
            'CRT-Monitor': "CRT monitors contain lead and phosphors that require special handling. They should never be thrown in regular trash as they can release toxic substances. Specialized recyclers safely break down these monitors and contain the harmful materials.",
        }
        
        # Get default recycling info if specific type not found
        default_info = "This e-waste item contains various materials that can be recovered through proper recycling. Always ensure it is disposed of through certified e-waste recycling facilities to prevent environmental contamination and recover valuable resources."
        info = recycling_info.get(ewaste_type, default_info)
        
        os.unlink(temp_path)  # Delete the temporary file
        
        return jsonify({
            'success': True,
            'ewaste_type': ewaste_type,
            'confidence': confidence,
            'recycling_info': info
        })
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)  # Clean up on error
        return jsonify({'error': str(e)}), 500

# View pickup history
@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('Please login to view your history.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get all pickups for the user, order by most recent first
    pickups = Schedule.query.filter_by(user_id=user_id).order_by(Schedule.pickup_date.desc()).all()
    
    return render_template('history.html', user=user, pickups=pickups)

# View and redeem rewards
@app.route('/rewards')
def rewards():
    if 'user_id' not in session:
        flash('Please login to view rewards.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get all active rewards
    available_rewards = Reward.query.filter_by(active=True).order_by(Reward.points_required).all()
    
    # Get user's redemptions
    redemptions = Redemption.query.filter_by(user_id=user_id).order_by(Redemption.redeemed_at.desc()).all()
    
    return render_template('rewards.html', user=user, rewards=available_rewards, redemptions=redemptions)

# Redeem a reward
@app.route('/redeem/<int:reward_id>', methods=['POST'])
def redeem_reward(reward_id):
    if 'user_id' not in session:
        flash('Please login to redeem rewards.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    reward = Reward.query.get_or_404(reward_id)
    
    # Check if reward is active and in stock
    if not reward.active:
        flash('This reward is no longer available.', 'danger')
        return redirect(url_for('rewards'))
    
    if reward.stock <= 0:
        flash('This reward is out of stock.', 'danger')
        return redirect(url_for('rewards'))
    
    # Check if user has enough points
    if user.eco_points < reward.points_required:
        flash(f'You need {reward.points_required - user.eco_points} more eco points for this reward.', 'danger')
        return redirect(url_for('rewards'))
    
    # Process redemption
    redemption = Redemption(
        user_id=user_id,
        reward_id=reward_id,
        points_spent=reward.points_required,
        status='Pending'
    )
    
    # Deduct points and update stock
    user.eco_points -= reward.points_required
    reward.stock -= 1
    
    db.session.add(redemption)
    db.session.commit()
    
    # Update session eco points
    session['eco_points'] = user.eco_points
    
    flash(f'You have successfully redeemed the {reward.name}!', 'success')
    return redirect(url_for('rewards'))

# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    
    return render_template('admin/login.html', form=form)

# Admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Please login as admin to access the dashboard.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get total users, e-waste items, pending pickups
    total_users = User.query.count()
    total_ewaste = Ewaste.query.count()
    pending_pickups = Schedule.query.filter_by(status='Pending').count()
    completed_pickups = Schedule.query.filter_by(status='Collected').count()
    
    # Get recent user registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Get upcoming pickups
    upcoming_pickups = Schedule.query.filter_by(status='Pending').order_by(Schedule.pickup_date).limit(5).all()
    
    # Get recent redemptions
    recent_redemptions = Redemption.query.order_by(Redemption.redeemed_at.desc()).limit(5).all()
    
    # Get e-waste statistics
    from sqlalchemy import func
    ewaste_stats_query = db.session.query(
        Ewaste.ewaste_type.label('type'),
        func.count(Ewaste.id).label('count')
    ).group_by(Ewaste.ewaste_type).order_by(func.count(Ewaste.id).desc()).limit(5).all()
    
    ewaste_stats = [{'type': item.type, 'count': item.count} for item in ewaste_stats_query] if ewaste_stats_query else []
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users,
                          total_ewaste=total_ewaste,
                          pending_pickups=pending_pickups,
                          completed_pickups=completed_pickups,
                          recent_users=recent_users,
                          upcoming_pickups=upcoming_pickups,
                          recent_redemptions=recent_redemptions,
                          ewaste_stats=ewaste_stats)

# Admin user management
@app.route('/admin/users')
def admin_users():
    if 'admin_id' not in session:
        flash('Please login as admin to access user management.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get filter parameters
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'username')
    order = request.args.get('order', 'asc')
    
    # Base query
    query = User.query
    
    # Apply search filter
    if search:
        query = query.filter(db.or_(
            User.username.ilike(f'%{search}%'),
            User.email.ilike(f'%{search}%')
        ))
    
    # Apply sorting
    if sort_by == 'username':
        query = query.order_by(User.username.asc() if order == 'asc' else User.username.desc())
    elif sort_by == 'date':
        query = query.order_by(User.created_at.asc() if order == 'asc' else User.created_at.desc())
    elif sort_by == 'points':
        query = query.order_by(User.eco_points.asc() if order == 'asc' else User.eco_points.desc())
    
    # Execute query
    users = query.all()
    
    # Calculate statistics
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_users_count = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    if users:
        avg_eco_points = sum(user.eco_points for user in users) / len(users)
        total_carbon_saved = sum(user.carbon_saved for user in users)
    else:
        avg_eco_points = 0
        total_carbon_saved = 0
    
    return render_template('admin/users.html', 
                          users=users,
                          new_users_count=new_users_count,
                          avg_eco_points=avg_eco_points,
                          total_carbon_saved=total_carbon_saved)

# Admin view user details
@app.route('/admin/users/<int:user_id>')
def admin_user_details(user_id):
    if 'admin_id' not in session:
        flash('Please login as admin to access user details.', 'warning')
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    ewaste_items = Ewaste.query.filter_by(user_id=user_id).all()
    pickups = Schedule.query.filter_by(user_id=user_id).all()
    redemptions = Redemption.query.filter_by(user_id=user_id).all()
    
    return render_template('admin/user_details.html', 
                          user=user, 
                          ewaste_items=ewaste_items, 
                          pickups=pickups,
                          redemptions=redemptions)

# Admin update user (eco points, reset password, delete account)
@app.route('/admin/users/<int:user_id>/update', methods=['POST'])
def admin_update_user(user_id):
    if 'admin_id' not in session:
        flash('Please login as admin to update user details.', 'warning')
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    
    if action == 'update_points':
        try:
            new_points = int(request.form.get('eco_points', 0))
            update_reason = request.form.get('update_reason', 'Admin adjustment')
            
            # Record the change
            change = new_points - user.eco_points
            if change != 0:
                adjustment_type = "increase" if change > 0 else "decrease"
                user.eco_points = new_points
                db.session.commit()
                flash(f'User eco points {adjustment_type}d by {abs(change)} points. Reason: {update_reason}', 'success')
            else:
                flash('No change in eco points.', 'info')
        except ValueError:
            flash('Invalid eco points value.', 'danger')
            
    elif action == 'reset_password':
        # Generate a random temporary password
        import random
        import string
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        user.set_password(temp_password)
        db.session.commit()
        flash(f'Password reset successful. Temporary password: {temp_password}', 'success')
        
    elif action == 'delete_user':
        # First delete all associated records
        Redemption.query.filter_by(user_id=user_id).delete()
        Schedule.query.filter_by(user_id=user_id).delete()
        Ewaste.query.filter_by(user_id=user_id).delete()
        
        # Then delete the user
        db.session.delete(user)
        db.session.commit()
        flash('User account and all associated data deleted permanently.', 'success')
        return redirect(url_for('admin_users'))
    
    return redirect(url_for('admin_user_details', user_id=user.id))

# Admin pickup management
@app.route('/admin/pickups')
def admin_pickups():
    if 'admin_id' not in session:
        flash('Please login as admin to access pickup management.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    date_range = request.args.get('date_range', 'all')
    search = request.args.get('search', '')
    
    # Base query
    query = Schedule.query
    
    # Apply filters
    if status_filter:
        query = query.filter(Schedule.status == status_filter)
        
    if date_range:
        today = datetime.now().date()
        if date_range == 'today':
            query = query.filter(db.func.date(Schedule.pickup_date) == today)
        elif date_range == 'week':
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            query = query.filter(db.func.date(Schedule.pickup_date).between(week_start, week_end))
        elif date_range == 'month':
            query = query.filter(db.extract('year', Schedule.pickup_date) == today.year,
                               db.extract('month', Schedule.pickup_date) == today.month)
    
    if search:
        query = query.join(User).join(Ewaste).filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                Ewaste.ewaste_type.ilike(f'%{search}%')
            )
        )
    
    # Execute query with ordered results
    pickups = query.order_by(Schedule.pickup_date).all()
    
    # Get counts for stats
    pending_count = Schedule.query.filter_by(status='Pending').count()
    collected_count = Schedule.query.filter_by(status='Collected').count()
    today_count = Schedule.query.filter(db.func.date(Schedule.pickup_date) == datetime.now().date()).count()
    
    return render_template('admin/pickups.html', 
                          pickups=pickups,
                          pending_count=pending_count,
                          collected_count=collected_count,
                          today_count=today_count,
                          today=datetime.now().date())

# Admin update pickup status
@app.route('/admin/pickups/<int:pickup_id>/update', methods=['POST'])
def admin_update_pickup(pickup_id):
    if 'admin_id' not in session:
        flash('Please login as admin to update pickup status.', 'warning')
        return redirect(url_for('admin_login'))
    
    pickup = Schedule.query.get_or_404(pickup_id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Collected']:
        pickup.status = new_status
        pickup.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Pickup status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
    
    return redirect(url_for('admin_pickups'))

# Admin e-waste inventory
@app.route('/admin/inventory')
def admin_inventory():
    if 'admin_id' not in session:
        flash('Please login as admin to access inventory.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get filter parameters
    ewaste_type_filter = request.args.get('ewaste_type', '')
    condition_filter = request.args.get('condition', '')
    search = request.args.get('search', '')
    
    # Base query
    query = Ewaste.query.join(User)
    
    # Apply filters
    if ewaste_type_filter:
        query = query.filter(Ewaste.ewaste_type == ewaste_type_filter)
        
    if condition_filter:
        query = query.filter(Ewaste.condition == condition_filter)
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                Ewaste.model.ilike(f'%{search}%')
            )
        )
    
    # Execute query
    ewaste_items = query.all()
    
    # Calculate totals for stats
    total_value = sum(item.estimated_price or 0 for item in ewaste_items)
    total_eco_points = sum(item.eco_points or 0 for item in ewaste_items)
    
    # Calculate carbon saved (using utility function)
    carbon_saved = 0
    for item in ewaste_items:
        carbon_saved += calculate_carbon_footprint(item.ewaste_type)
    
    # Get unique e-waste types for filter dropdown
    ewaste_types = db.session.query(Ewaste.ewaste_type).distinct().order_by(Ewaste.ewaste_type).all()
    ewaste_types = [t[0] for t in ewaste_types]
    
    # Prepare data for charts
    type_data = {}
    for item in ewaste_items:
        if item.ewaste_type in type_data:
            type_data[item.ewaste_type] += 1
        else:
            type_data[item.ewaste_type] = 1
    
    # If we have too many types, group the less common ones as "Other"
    if len(type_data) > 6:
        sorted_types = sorted(type_data.items(), key=lambda x: x[1], reverse=True)
        top_types = dict(sorted_types[:5])
        other_count = sum(count for _, count in sorted_types[5:])
        top_types['Other'] = other_count
        type_data = top_types
    
    type_labels = list(type_data.keys())
    type_counts = list(type_data.values())
    
    # Condition breakdown
    condition_counts = [0, 0, 0, 0]  # Excellent, Good, Fair, Poor
    for item in ewaste_items:
        if item.condition == 'Excellent':
            condition_counts[0] += 1
        elif item.condition == 'Good':
            condition_counts[1] += 1
        elif item.condition == 'Fair':
            condition_counts[2] += 1
        elif item.condition == 'Poor':
            condition_counts[3] += 1
    
    return render_template('admin/inventory.html', 
                          ewaste_items=ewaste_items,
                          total_value=total_value,
                          total_eco_points=total_eco_points,
                          carbon_saved=carbon_saved,
                          ewaste_types=ewaste_types,
                          type_labels=type_labels,
                          type_counts=type_counts,
                          condition_counts=condition_counts)

# Admin rewards management
@app.route('/admin/rewards', methods=['GET', 'POST'])
def admin_rewards():
    if 'admin_id' not in session:
        flash('Please login as admin to access rewards management.', 'warning')
        return redirect(url_for('admin_login'))
    
    form = RewardForm()
    if form.validate_on_submit():
        reward = Reward(
            name=form.name.data,
            description=form.description.data,
            points_required=form.points_required.data,
            reward_type=form.reward_type.data,
            stock=form.stock.data,
            active=True
        )
        
        db.session.add(reward)
        db.session.commit()
        flash('New reward added successfully!', 'success')
        return redirect(url_for('admin_rewards'))
    
    rewards = Reward.query.all()
    return render_template('admin/rewards.html', rewards=rewards, form=form)

# Admin update reward
@app.route('/admin/rewards/<int:reward_id>/update', methods=['POST'])
def admin_update_reward(reward_id):
    if 'admin_id' not in session:
        flash('Please login as admin to update rewards.', 'warning')
        return redirect(url_for('admin_login'))
    
    reward = Reward.query.get_or_404(reward_id)
    action = request.form.get('action')
    
    if action == 'toggle_active':
        reward.active = not reward.active
        db.session.commit()
        status = 'activated' if reward.active else 'deactivated'
        flash(f'Reward {status} successfully.', 'success')
    elif action == 'update_stock':
        new_stock = request.form.get('stock')
        try:
            reward.stock = int(new_stock)
            db.session.commit()
            flash('Stock updated successfully.', 'success')
        except ValueError:
            flash('Invalid stock value.', 'danger')
    
    return redirect(url_for('admin_rewards'))

# Admin redemption management
@app.route('/admin/redemptions')
def admin_redemptions():
    if 'admin_id' not in session:
        flash('Please login as admin to access redemption management.', 'warning')
        return redirect(url_for('admin_login'))
    
    redemptions = Redemption.query.join(User).join(Reward).order_by(Redemption.redeemed_at.desc()).all()
    return render_template('admin/redemptions.html', redemptions=redemptions)

# Admin update redemption status
@app.route('/admin/redemptions/<int:redemption_id>/update', methods=['POST'])
def admin_update_redemption(redemption_id):
    if 'admin_id' not in session:
        flash('Please login as admin to update redemption status.', 'warning')
        return redirect(url_for('admin_login'))
    
    redemption = Redemption.query.get_or_404(redemption_id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Processed', 'Delivered']:
        redemption.status = new_status
        db.session.commit()
        flash(f'Redemption status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
    
    return redirect(url_for('admin_redemptions'))

# Create admin user (called at startup)
def create_admin():
    # Check if admin exists
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(username='admin')
        admin.set_password('admin123')  # Default password
        db.session.add(admin)
        db.session.commit()
        app.logger.info('Admin user created')
