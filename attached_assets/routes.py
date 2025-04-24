import os
import tempfile
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Admin, Ewaste, Schedule, Reward, Redemption
from utils import get_ewaste_news
from api import classify_image

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
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
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
    
    return render_template('register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['eco_points'] = user.eco_points  # Store eco points in session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

# User logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('eco_points', None)  # Clear eco_points from session
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
        return redirect(url_for('login'))
    
    # Store eco points in session for display in navbar
    session['eco_points'] = user.eco_points
    
    # Get user's scheduled pickups
    pickups = Schedule.query.filter_by(user_id=user_id).all()
    
    # Get the latest news
    news = get_ewaste_news()
    
    return render_template('dashboard.html', user=user, pickups=pickups, news=news)

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
        return redirect(url_for('login'))
    
    # Store eco points in session for display in navbar
    session['eco_points'] = user.eco_points
    
    if request.method == 'POST':
        user_id = session['user_id']
        ewaste_type = request.form.get('ewaste_type')
        model = request.form.get('model')
        ram = request.form.get('ram')
        condition = request.form.get('condition')
        pickup_date = request.form.get('pickup_date')
        pickup_address = request.form.get('pickup_address')
        
        # Calculate estimated price and eco points based on ewaste details
        # This is a simple calculation, can be made more complex
        price_map = {
            'Laptop': 100,
            'Mobile': 50,
            'Desktop': 150,
            'Tablet': 75,
            'Monitor': 60,
            'Printer': 40,
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
        pickup_datetime = datetime.strptime(pickup_date, '%Y-%m-%dT%H:%M')
        new_schedule = Schedule(
            user_id=user_id,
            ewaste_id=new_ewaste.id,
            pickup_date=pickup_datetime,
            pickup_address=pickup_address,
            status='Pending'
        )
        
        db.session.add(new_schedule)
        
        # Update user's eco points
        user = User.query.get(user_id)
        user.eco_points += eco_points
        # Update eco_points in session too
        session['eco_points'] = user.eco_points
        
        # Updated carbon footprint calculation with the new e-waste types
        carbon_savings_map = {
            'Laptop': 10.0,
            'Smartphone': 5.0,
            'Desktop-PC': 15.0,
            'Tablet': 7.0,
            'Flat-Panel-Monitor': 12.0,
            'CRT-Monitor': 14.0,
            'Printer': 8.0,
            'Air-Conditioner': 20.0,
            'Washing-Machine': 18.0,
            'Refrigerator': 25.0,
            'Freezer': 22.0,
            'Microwave': 8.0,
            'Flat-Panel-TV': 15.0,
            'CRT-TV': 17.0,
            'Camera': 4.0,
            'Computer-Keyboard': 2.0,
            'Computer-Mouse': 1.0,
            'Coffee-Machine': 6.0,
            'Dishwasher': 12.0,
            'Vacuum-Cleaner': 7.0,
            'Headphone': 1.5,
            'Smart-Watch': 1.0,
            'Router': 3.0,
            'Projector': 9.0,
            'Speaker': 4.0,
            'LED-Bulb': 0.5,
            'Battery': 2.0,
            'USB-Flash-Drive': 0.5
        }
        
        carbon_saved = carbon_savings_map.get(ewaste_type, 5.0)
        user.carbon_saved += carbon_saved
        
        db.session.commit()
        
        flash(f'Pickup scheduled successfully! You earned {eco_points} eco points and saved {carbon_saved} kg of CO2!', 'success')
        return redirect(url_for('history'))
    
    return render_template('schedule.html')

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
    
    # Save the uploaded file to a temporary location
    _, temp_path = tempfile.mkstemp(suffix='.jpg')
    file.save(temp_path)
    
    try:
        # Classify the image using Roboflow API
        result = classify_image(temp_path)
        
        # Process the classification result
        detected_items = result.get('predictions', [])
        
        if not detected_items:
            return jsonify({'error': 'No e-waste detected in the image'}), 400
        
        # Get the item with highest confidence
        best_match = max(detected_items, key=lambda x: x.get('confidence', 0))
        
        # The new API returns class names that match our e-waste types directly
        # No need for extensive mapping but handle common cases for standardization
        class_to_type = {
            'laptop': 'Laptop',
            'smartphone': 'Smartphone',
            'desktop-pc': 'Desktop-PC',
            'tablet': 'Tablet',
            'monitor': 'Flat-Panel-Monitor',
            'flat-panel-monitor': 'Flat-Panel-Monitor',
            'flat-panel-tv': 'Flat-Panel-TV',
            'printer': 'Printer',
            # New class mappings to standardize format
            'air-conditioner': 'Air-Conditioner',
            'blood-pressure-monitor': 'Blood-Pressure-Monitor',
            'ceiling-fan': 'Ceiling-Fan',
            'clothes-iron': 'Clothes-Iron',
            'coffee-machine': 'Coffee-Machine',
            'computer-keyboard': 'Computer-Keyboard',
            'computer-mouse': 'Computer-Mouse',
            'crt-monitor': 'CRT-Monitor',
            'crt-tv': 'CRT-TV',
            'led-bulb': 'LED-Bulb',
            'vacuum-cleaner': 'Vacuum-Cleaner',
            'washing-machine': 'Washing-Machine',
            'usb-flash-drive': 'USB-Flash-Drive',
            'smart-watch': 'Smart-Watch'
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
            
            'Printer': "Printers contain circuit boards, metals, and plastics that can be recycled. Ink and toner cartridges should be removed and recycled separately. Some manufacturers offer take-back programs for their printers and cartridges.",
            
            'Air-Conditioner': "Air conditioners contain refrigerants that must be properly extracted to prevent release into the atmosphere where they contribute to ozone depletion. They also contain valuable copper and aluminum that can be recovered and reused.",
            
            'Refrigerator': "Refrigerators contain refrigerants and foam insulation that must be properly captured during recycling to prevent greenhouse gas emissions. The metal, glass, and plastic components are separated and recycled. Copper from the coils is particularly valuable.",
            
            'Washing-Machine': "Washing machines contain significant amounts of steel and other metals that are highly recyclable. The motors contain copper that can be recovered. Proper recycling prevents heavy metals from entering landfills and conserves resources.",
            
            'LED-Bulb': "LED bulbs contain small amounts of electronic components and metals that can be recycled. They don't contain mercury like CFL bulbs, making them safer to handle. The aluminum heat sinks are particularly valuable for recycling.",
            
            'Headphone': "Headphones contain small amounts of copper in their wires and rare earth elements in their magnets. The plastic components can also be recycled. Wireless headphones contain lithium batteries that should be properly disposed of.",
            
            'Computer-Keyboard': "Keyboards contain recyclable plastics and small amounts of metals. The circuit boards contain copper and sometimes small amounts of gold in the contacts. Mechanical keyboards with metal components have higher recycling value.",
            
            'Computer-Mouse': "Computer mice contain recyclable plastics, small circuit boards, and copper wiring. Optical and laser mice also contain small optical components that require proper handling. Wireless mice contain batteries that should be recycled separately.",
            
            'Tablet': "Tablets contain valuable materials similar to smartphones, including gold, silver, and rare earth elements. Their batteries are typically integrated and require professional recycling. Always remove personal data before recycling.",
            
            'Freezer': "Freezers, like refrigerators, contain refrigerants that must be properly captured during recycling. The insulation may contain blowing agents that need proper handling. The metal components, primarily steel, are recycled to make new products.",
            
            'Coffee-Machine': "Coffee machines contain recyclable materials like plastic, aluminum, and copper wiring. Some higher-end models contain circuit boards with valuable metals. The heating elements are typically made of recyclable metals like aluminum or copper.",
            
            'Speaker': "Speakers contain valuable copper in their wiring and voice coils, and sometimes rare earth magnets. The cones and housing are typically made of recyclable materials like paper, plastic, or metal that can be separated during recycling.",
            
            'Camera': "Digital cameras contain circuit boards with precious metals, rechargeable batteries that require special handling, and optical glass that can be recycled. The plastic bodies and metal components can be separated and recycled individually.",
            
            'Vacuum-Cleaner': "Vacuum cleaners contain motors with copper windings, plastic components, and metal parts that can all be recycled. The dust bag and filter should be emptied and disposed of separately before recycling the main unit.",
            
            'Microwave': "Microwaves contain significant amounts of steel in their casing and copper in their transformers and wiring. The circuit boards contain valuable metals. The magnetron contains rare earth elements that can be recovered through specialized recycling.",
            
            'Projector': "Projectors contain optical components, circuit boards with precious metals, and high-intensity lamps that may contain mercury (in older models). LED and laser projectors are more environmentally friendly but still require proper e-waste recycling.",
            
            'Router': "Routers contain circuit boards with valuable metals like gold, silver, and copper. The plastic casings can be recycled separately. Always reset to factory settings before recycling to remove personal information and network credentials.",
            
            'Smart-Watch': "Smart watches contain small but concentrated amounts of valuable materials, including lithium batteries, precious metals in circuit boards, and sometimes special display materials. Their small size makes them easy to recycle but easy to lose in waste streams.",
            
            'Dishwasher': "Dishwashers contain significant amounts of steel, copper wiring, motors, and pumps that can be recycled. The control boards contain valuable metals. Proper recycling keeps these materials in circulation and out of landfills.",
            
            'USB-Flash-Drive': "Flash drives contain small circuit boards with valuable metals including gold contacts. Despite their small size, they should still be recycled as e-waste. Always erase personal data before recycling."
        }
        
        # Get recycling information for the detected e-waste type or use a default message
        default_info = "This item contains valuable or hazardous materials that should be properly recycled. Take it to an e-waste collection point or recycling facility to ensure materials are recovered and harmful substances are safely managed."
        recycling_message = recycling_info.get(ewaste_type, default_info)
        
        # Clean up the temporary file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'ewaste_type': ewaste_type,
            'confidence': f"{confidence:.2f}%",
            'recycling_info': recycling_message,
            'details': best_match
        })
    
    except Exception as e:
        # Clean up the temporary file
        os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

# View pickup history
@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('Please login to view your history.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # If user doesn't exist for some reason (maybe was deleted), redirect to login
    if not user:
        flash('User account not found. Please login again.', 'danger')
        session.pop('user_id', None)  # Clear the session
        session.pop('username', None)
        return redirect(url_for('login'))
    
    # Store eco points in session for display in navbar
    session['eco_points'] = user.eco_points
    
    # Get all pickups with related e-waste details
    pickups = db.session.query(Schedule, Ewaste)\
        .join(Ewaste, Schedule.ewaste_id == Ewaste.id)\
        .filter(Schedule.user_id == user_id)\
        .order_by(Schedule.scheduled_at.desc())\
        .all()
    
    return render_template('history.html', user=user, pickups=pickups)

# Admin login
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        admin_code = request.form.get('admin_code')
        
        # Check if admin_code is correct (you might want to store this in environment variable)
        if admin_code != 'ecycle123':  # Set a secure admin code
            flash('Invalid admin registration code', 'danger')
            return render_template('admin/register.html')
            
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('admin/register.html')
            
        # Check if username already exists
        if Admin.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('admin/register.html')
            
        # Create new admin
        new_admin = Admin(username=username)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Admin account created successfully', 'success')
        return redirect(url_for('admin_login'))
        
    return render_template('admin/register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    
    return render_template('admin/login.html')

# Admin logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Admin logged out.', 'success')
    return redirect(url_for('index'))

# Admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Please login as admin to access the dashboard.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Count of pending and collected pickups
    pending_count = Schedule.query.filter_by(status='Pending').count()
    collected_count = Schedule.query.filter_by(status='Collected').count()
    user_count = User.query.count()
    
    # Recent pickups
    recent_pickups = db.session.query(Schedule, User, Ewaste)\
        .join(User, Schedule.user_id == User.id)\
        .join(Ewaste, Schedule.ewaste_id == Ewaste.id)\
        .order_by(Schedule.scheduled_at.desc())\
        .limit(5)\
        .all()
    
    # E-waste statistics
    ewaste_stats = {}
    ewaste_counts = db.session.query(
        Ewaste.ewaste_type,
        db.func.count(Ewaste.id).label('count'),
        db.func.sum(Ewaste.eco_points).label('eco_points')
    ).group_by(Ewaste.ewaste_type).all()
    
    for type_name, count, eco_points in ewaste_counts:
        ewaste_stats[type_name] = {
            'count': count,
            'eco_points': eco_points or 0
        }
    
    # Top users by eco points
    top_users = db.session.query(
        User.id,
        User.username,
        User.eco_points,
        db.func.count(Schedule.id).label('pickup_count')
    ).outerjoin(Schedule, User.id == Schedule.user_id)\
     .group_by(User.id)\
     .order_by(User.eco_points.desc())\
     .limit(5)\
     .all()
    
    return render_template('admin/dashboard.html', 
                           pending_count=pending_count, 
                           collected_count=collected_count,
                           user_count=user_count,
                           recent_pickups=recent_pickups,
                           ewaste_stats=ewaste_stats,
                           top_users=top_users)

# Admin view all pickups
@app.route('/admin/pickups')
def admin_view_pickups():
    if 'admin_id' not in session:
        flash('Please login as admin.', 'warning')
        return redirect(url_for('admin_login'))
    
    status_filter = request.args.get('status', '')
    
    # Base query
    query = db.session.query(Schedule, User, Ewaste)\
        .join(User, Schedule.user_id == User.id)\
        .join(Ewaste, Schedule.ewaste_id == Ewaste.id)
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter(Schedule.status == status_filter)
    
    # Order by scheduled_at descending
    pickups = query.order_by(Schedule.scheduled_at.desc()).all()
    
    return render_template('admin/view_pickups.html', pickups=pickups, status_filter=status_filter)

# Admin update pickup status
@app.route('/admin/update_status', methods=['POST'])
def admin_update_status():
    if 'admin_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
    
    schedule_id = request.form.get('schedule_id')
    new_status = request.form.get('status')
    
    if not schedule_id or not new_status:
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Update the status
        schedule.status = new_status
        schedule.updated_at = datetime.utcnow()
        
        # If status changed to Collected, update timestamp
        if new_status == 'Collected':
            # Additional logic if needed when pickup is collected
            pass
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Status updated to {new_status}'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin manage users
@app.route('/admin/users')
def admin_manage_users():
    if 'admin_id' not in session:
        flash('Please login as admin to manage users.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get all users ordered by username
    users = User.query.order_by(User.username).all()
    
    return render_template('admin/manage_users.html', users=users)

# Admin user detail
@app.route('/admin/users/<int:user_id>')
def admin_user_detail(user_id):
    if 'admin_id' not in session:
        flash('Please login as admin to view user details.', 'warning')
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    
    # Get user's pickups with e-waste details
    pickups = db.session.query(Schedule, Ewaste)\
        .join(Ewaste, Schedule.ewaste_id == Ewaste.id)\
        .filter(Schedule.user_id == user_id)\
        .order_by(Schedule.scheduled_at.desc())\
        .all()
    
    return render_template('admin/user_detail.html', user=user, pickups=pickups)

# Admin update eco points
@app.route('/admin/update_eco_points', methods=['POST'])
def admin_update_eco_points():
    if 'admin_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
    
    user_id = request.form.get('user_id')
    eco_points = request.form.get('eco_points')
    reason = request.form.get('reason')
    
    if not user_id or not eco_points or not reason:
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update the eco points
        user.eco_points = int(eco_points)
        # Update session eco_points if this is the current user
        if 'user_id' in session and int(session['user_id']) == int(user_id):
            session['eco_points'] = user.eco_points
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Eco points updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin add e-waste and schedule pickup
@app.route('/admin/add_ewaste', methods=['GET', 'POST'])
def admin_add_ewaste():
    if 'admin_id' not in session:
        flash('Please login as admin to add e-waste.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get all users for dropdown
    users = User.query.order_by(User.username).all()
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        ewaste_type = request.form.get('ewaste_type')
        model = request.form.get('model')
        ram = request.form.get('ram')
        condition = request.form.get('condition')
        estimated_price = request.form.get('estimated_price')
        eco_points = request.form.get('eco_points')
        pickup_date = request.form.get('pickup_date')
        pickup_address = request.form.get('pickup_address')
        status = request.form.get('status')
        
        # Handle image upload if provided
        image_path = None
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            filename = secure_filename(file.filename)
            # Save to upload folder with timestamp to avoid duplicate names
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            image_path = f"static/uploads/{timestamp}_{filename}"
            
            # Ensure upload folder exists
            os.makedirs('static/uploads', exist_ok=True)
            file.save(image_path)
        
        try:
            # Create new e-waste entry
            new_ewaste = Ewaste(
                user_id=user_id,
                ewaste_type=ewaste_type,
                model=model,
                ram=ram,
                condition=condition,
                estimated_price=estimated_price,
                eco_points=eco_points,
                image_path=image_path
            )
            
            db.session.add(new_ewaste)
            db.session.flush()  # Get the new_ewaste.id without committing
            
            # Create new schedule entry
            pickup_datetime = datetime.strptime(pickup_date, '%Y-%m-%dT%H:%M')
            new_schedule = Schedule(
                user_id=user_id,
                ewaste_id=new_ewaste.id,
                pickup_date=pickup_datetime,
                pickup_address=pickup_address,
                status=status
            )
            
            db.session.add(new_schedule)
            
            # Update user's eco points if status is "Collected"
            if status == 'Collected':
                user = User.query.get(user_id)
                user.eco_points += int(eco_points)
                # Update session eco_points if this is the current user
                if 'user_id' in session and int(session['user_id']) == int(user_id):
                    session['eco_points'] = user.eco_points
                
                # Calculate carbon footprint using the updated carbon savings map
                carbon_savings_map = {
                    'Laptop': 10.0,
                    'Smartphone': 5.0,
                    'Desktop-PC': 15.0,
                    'Tablet': 7.0,
                    'Flat-Panel-Monitor': 12.0,
                    'CRT-Monitor': 14.0,
                    'Printer': 8.0,
                    'Air-Conditioner': 20.0,
                    'Washing-Machine': 18.0,
                    'Refrigerator': 25.0,
                    'Freezer': 22.0,
                    'Microwave': 8.0,
                    'Flat-Panel-TV': 15.0,
                    'CRT-TV': 17.0,
                    'Camera': 4.0,
                    'Computer-Keyboard': 2.0,
                    'Computer-Mouse': 1.0,
                    'Coffee-Machine': 6.0,
                    'Dishwasher': 12.0,
                    'Vacuum-Cleaner': 7.0,
                    'Headphone': 1.5,
                    'Smart-Watch': 1.0,
                    'Router': 3.0,
                    'Projector': 9.0,
                    'Speaker': 4.0,
                    'LED-Bulb': 0.5,
                    'Battery': 2.0,
                    'USB-Flash-Drive': 0.5
                }
                
                carbon_saved = carbon_savings_map.get(ewaste_type, 5.0)
                user.carbon_saved += carbon_saved
            
            db.session.commit()
            
            flash(f'E-waste entry and pickup added successfully!', 'success')
            return redirect(url_for('admin_view_pickups'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding e-waste: {str(e)}', 'danger')
    
    # For GET request, pre-populate user_id if provided in query string
    pre_selected_user_id = request.args.get('user_id')
    
    return render_template('admin/add_ewaste.html', users=users, pre_selected_user_id=pre_selected_user_id)

# Initialize admin user if none exists
def create_admin():
    admin_count = Admin.query.count()
    if admin_count == 0:
        admin = Admin(username='admin')
        admin.set_password('admin123')  # Default password, should be changed
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created.")
        
# Rewards page - display rewards and redemption history
@app.route('/rewards')
def rewards():
    if 'user_id' not in session:
        flash('Please login to access rewards.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # If user doesn't exist for some reason (maybe was deleted), redirect to login
    if not user:
        flash('User account not found. Please login again.', 'danger')
        session.pop('user_id', None)  # Clear the session
        session.pop('username', None)
        return redirect(url_for('login'))
    
    # Get active rewards
    rewards = Reward.query.filter_by(active=True).all()
    
    # Get user's redemption history
    redemptions = Redemption.query.filter_by(user_id=user_id).order_by(Redemption.redeemed_at.desc()).all()
    
    return render_template('rewards.html', 
                           user=user, 
                           rewards=rewards,
                           redemptions=redemptions)

# Redeem a reward
@app.route('/redeem/<int:reward_id>', methods=['POST'])
def redeem_reward(reward_id):
    if 'user_id' not in session:
        flash('Please login to redeem rewards.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # If user doesn't exist for some reason (maybe was deleted), redirect to login
    if not user:
        flash('User account not found. Please login again.', 'danger')
        session.pop('user_id', None)  # Clear the session
        session.pop('username', None)
        return redirect(url_for('login'))
        
    reward = Reward.query.get(reward_id)
    
    if not reward or not reward.active:
        flash('This reward is no longer available.', 'danger')
        return redirect(url_for('rewards'))
    
    # Check if user has enough points
    if user.eco_points < reward.points_required:
        flash('You do not have enough eco points for this reward.', 'danger')
        return redirect(url_for('rewards'))
    
    # Check if reward is in stock
    if reward.stock <= 0:
        flash('This reward is out of stock.', 'danger')
        return redirect(url_for('rewards'))
    
    # Process the redemption
    user.eco_points -= reward.points_required
    # Update eco_points in session too
    session['eco_points'] = user.eco_points
    reward.stock -= 1
    
    # Create redemption record
    redemption = Redemption(
        user_id=user_id,
        reward_id=reward_id,
        points_spent=reward.points_required,
        status='Pending'
    )
    
    db.session.add(redemption)
    db.session.commit()
    
    flash(f'Successfully redeemed {reward.name} for {reward.points_required} eco points!', 'success')
    return redirect(url_for('rewards'))

# Admin routes for managing rewards
@app.route('/admin/rewards')
def admin_manage_rewards():
    if 'admin_id' not in session:
        flash('Please login as admin to manage rewards.', 'warning')
        return redirect(url_for('admin_login'))
    
    rewards = Reward.query.all()
    redemptions = Redemption.query.order_by(Redemption.redeemed_at.desc()).all()
    
    return render_template('admin/rewards.html', rewards=rewards, redemptions=redemptions)

# Add new reward (admin)
@app.route('/admin/rewards/add', methods=['GET', 'POST'])
def admin_add_reward():
    if 'admin_id' not in session:
        flash('Please login as admin to add rewards.', 'warning')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        points_required = request.form.get('points_required')
        reward_type = request.form.get('reward_type')
        stock = request.form.get('stock')
        image_path = request.form.get('image_path', '')
        
        new_reward = Reward(
            name=name,
            description=description,
            points_required=int(points_required),
            reward_type=reward_type,
            stock=int(stock),
            image_path=image_path,
            active=True
        )
        
        db.session.add(new_reward)
        db.session.commit()
        
        flash('New reward added successfully!', 'success')
        return redirect(url_for('admin_manage_rewards'))
    
    return render_template('admin/add_reward.html')

# Update redemption status (admin)
@app.route('/admin/redemption/<int:redemption_id>/update', methods=['POST'])
def admin_update_redemption(redemption_id):
    if 'admin_id' not in session:
        flash('Please login as admin to update redemptions.', 'warning')
        return redirect(url_for('admin_login'))
    
    status = request.form.get('status')
    
    redemption = Redemption.query.get(redemption_id)
    if redemption:
        redemption.status = status
        db.session.commit()
        flash('Redemption status updated successfully!', 'success')
    else:
        flash('Redemption not found.', 'danger')
    
    return redirect(url_for('admin_manage_rewards'))

# Edit reward (admin)
@app.route('/admin/rewards/<int:reward_id>/edit', methods=['POST'])
def admin_edit_reward(reward_id):
    if 'admin_id' not in session:
        flash('Please login as admin to edit rewards.', 'warning')
        return redirect(url_for('admin_login'))
    
    reward = Reward.query.get(reward_id)
    if not reward:
        flash('Reward not found.', 'danger')
        return redirect(url_for('admin_manage_rewards'))
    
    # Update reward details
    reward.name = request.form.get('name')
    reward.description = request.form.get('description')
    reward.points_required = int(request.form.get('points_required'))
    reward.reward_type = request.form.get('reward_type')
    reward.stock = int(request.form.get('stock'))
    reward.image_path = request.form.get('image_path')
    reward.active = 'active' in request.form
    
    db.session.commit()
    flash('Reward updated successfully!', 'success')
    return redirect(url_for('admin_manage_rewards'))

# Delete reward (admin)
@app.route('/admin/rewards/<int:reward_id>/delete', methods=['POST'])
def admin_delete_reward(reward_id):
    if 'admin_id' not in session:
        flash('Please login as admin to delete rewards.', 'warning')
        return redirect(url_for('admin_login'))
    
    reward = Reward.query.get(reward_id)
    if reward:
        # Check if there are any redemptions for this reward
        redemptions = Redemption.query.filter_by(reward_id=reward_id).count()
        if redemptions > 0:
            # Instead of deleting, just mark as inactive
            reward.active = False
            db.session.commit()
            flash('Reward marked as inactive since it has redemption records.', 'warning')
        else:
            # Safe to delete if no redemptions
            db.session.delete(reward)
            db.session.commit()
            flash('Reward deleted successfully!', 'success')
    else:
        flash('Reward not found.', 'danger')
    
    return redirect(url_for('admin_manage_rewards'))
