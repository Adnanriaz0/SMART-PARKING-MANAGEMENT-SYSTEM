from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, Admin, Owner, Package, PurchaseRequest, City, Region, SubRegion, Slot, Booking
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@login_manager.user_loader
def load_user(user_id):
    from flask import session
    if session.get('user_type') == 'admin':
        return Admin.query.get(int(user_id))
    return Owner.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Owner):
            flash('You need to be logged in as owner to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        admin = Admin.query.filter_by(email=email).first()
        if admin and admin.check_password(password):
            login_user(admin)
            from flask import session
            session['user_type'] = 'admin'
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
@admin_required
def admin_logout():
    from flask import session
    session.pop('user_type', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_owners = Owner.query.count()
    total_slots = Slot.query.count()
    active_bookings = Booking.query.filter_by(status='active').count()
    pending_requests = PurchaseRequest.query.filter_by(status='pending').count()
    return render_template('admin/dashboard.html', total_owners=total_owners, total_slots=total_slots, active_bookings=active_bookings, pending_requests=pending_requests)

@app.route('/admin/bank-details', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_bank_details():
    if request.method == 'POST':
        current_user.bank_name = request.form.get('bank_name')
        current_user.account_title = request.form.get('account_title')
        current_user.account_number = request.form.get('account_number')
        db.session.commit()
        flash('Bank details updated successfully!', 'success')
        return redirect(url_for('admin_bank_details'))
    return render_template('admin/bank_details.html')

@app.route('/admin/packages', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_packages():
    if request.method == 'POST':
        name = request.form.get('name')
        duration_months = int(request.form.get('duration_months'))
        price = float(request.form.get('price'))
        description = request.form.get('description')
        package = Package(name=name, duration_months=duration_months, price=price, description=description)
        db.session.add(package)
        db.session.commit()
        flash('Package created successfully!', 'success')
        return redirect(url_for('admin_packages'))
    packages = Package.query.order_by(Package.created_at.desc()).all()
    return render_template('admin/packages.html', packages=packages)

@app.route('/admin/packages/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_package(id):
    package = Package.query.get_or_404(id)
    db.session.delete(package)
    db.session.commit()
    flash('Package deleted successfully!', 'success')
    return redirect(url_for('admin_packages'))

@app.route('/admin/locations')
@login_required
@admin_required
def admin_locations():
    cities = City.query.order_by(City.name).all()
    return render_template('admin/locations.html', cities=cities)

@app.route('/admin/locations/city/add', methods=['POST'])
@login_required
@admin_required
def admin_add_city():
    name = request.form.get('name')
    if City.query.filter_by(name=name).first():
        flash('City already exists!', 'danger')
    else:
        city = City(name=name)
        db.session.add(city)
        db.session.commit()
        flash(f'City "{name}" added successfully!', 'success')
    return redirect(url_for('admin_locations'))

@app.route('/admin/locations/city/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_city(id):
    city = City.query.get_or_404(id)
    db.session.delete(city)
    db.session.commit()
    flash('City deleted successfully!', 'success')
    return redirect(url_for('admin_locations'))

@app.route('/admin/locations/region/add', methods=['POST'])
@login_required
@admin_required
def admin_add_region():
    name = request.form.get('name')
    city_id = request.form.get('city_id')
    region = Region(name=name, city_id=city_id)
    db.session.add(region)
    db.session.commit()
    flash(f'Region "{name}" added successfully!', 'success')
    return redirect(url_for('admin_locations'))

@app.route('/admin/locations/region/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_region(id):
    region = Region.query.get_or_404(id)
    db.session.delete(region)
    db.session.commit()
    flash('Region deleted successfully!', 'success')
    return redirect(url_for('admin_locations'))

@app.route('/admin/locations/subregion/add', methods=['POST'])
@login_required
@admin_required
def admin_add_subregion():
    name = request.form.get('name')
    region_id = request.form.get('region_id')
    subregion = SubRegion(name=name, region_id=region_id)
    subregion.generate_gate_token()
    db.session.add(subregion)
    db.session.commit()
    flash(f'SubRegion "{name}" added with gate token: {subregion.gate_device_token}', 'success')
    return redirect(url_for('admin_locations'))

@app.route('/admin/locations/subregion/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_subregion(id):
    subregion = SubRegion.query.get_or_404(id)
    db.session.delete(subregion)
    db.session.commit()
    flash('SubRegion deleted successfully!', 'success')
    return redirect(url_for('admin_locations'))

@app.route('/admin/locations/slot/add', methods=['POST'])
@login_required
@admin_required
def admin_add_slot():
    name = request.form.get('name')
    subregion_id = request.form.get('subregion_id')
    slot = Slot(name=name, subregion_id=subregion_id)
    slot.generate_device_token()
    db.session.add(slot)
    db.session.commit()
    flash(f'Slot "{name}" added with device token: {slot.device_token}', 'success')
    return redirect(url_for('admin_locations'))

@app.route('/admin/locations/slot/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_slot(id):
    slot = Slot.query.get_or_404(id)
    db.session.delete(slot)
    db.session.commit()
    flash('Slot deleted successfully!', 'success')
    return redirect(url_for('admin_locations'))

@app.route('/admin/requests')
@login_required
@admin_required
def admin_requests():
    pending_requests = PurchaseRequest.query.filter_by(status='pending').order_by(PurchaseRequest.created_at.desc()).all()
    approved_requests = PurchaseRequest.query.filter_by(status='approved').order_by(PurchaseRequest.processed_at.desc()).all()
    rejected_requests = PurchaseRequest.query.filter_by(status='rejected').order_by(PurchaseRequest.processed_at.desc()).all()
    return render_template('admin/requests.html', pending_requests=pending_requests, approved_requests=approved_requests, rejected_requests=rejected_requests)

@app.route('/admin/requests/approve/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_approve_request(id):
    purchase_request = PurchaseRequest.query.get_or_404(id)
    rfid_card = request.form.get('rfid_card')
    if not rfid_card:
        flash('RFID card number is required!', 'danger')
        return redirect(url_for('admin_requests'))
    existing = Owner.query.filter_by(rfid_card=rfid_card).first()
    if existing:
        flash('This RFID card is already assigned to another owner!', 'danger')
        return redirect(url_for('admin_requests'))
    owner = purchase_request.owner
    owner.package_id = purchase_request.package_id
    owner.package_active = True
    owner.rfid_card = rfid_card
    owner.package_start_date = datetime.utcnow()
    owner.package_end_date = datetime.utcnow() + timedelta(days=purchase_request.package.duration_months * 30)
    purchase_request.status = 'approved'
    purchase_request.processed_at = datetime.utcnow()
    db.session.commit()
    flash(f'Request approved! RFID card {rfid_card} assigned to {owner.name}', 'success')
    return redirect(url_for('admin_requests'))

@app.route('/admin/requests/reject/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_reject_request(id):
    purchase_request = PurchaseRequest.query.get_or_404(id)
    purchase_request.status = 'rejected'
    purchase_request.processed_at = datetime.utcnow()
    db.session.commit()
    flash('Request rejected.', 'info')
    return redirect(url_for('admin_requests'))

@app.route('/owner/register', methods=['GET', 'POST'])
def owner_register():
    if current_user.is_authenticated and isinstance(current_user, Owner):
        return redirect(url_for('owner_dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        car_number = request.form.get('car_number')
        email = request.form.get('email')
        password = request.form.get('password')
        terms = request.form.get('terms')
        if not terms:
            flash('You must agree to the terms and conditions', 'danger')
            return redirect(url_for('owner_register'))
        if Owner.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('owner_register'))
        owner = Owner(name=name, phone=phone, car_number=car_number, email=email)
        owner.set_password(password)
        db.session.add(owner)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('owner_login'))
    return render_template('owner/register.html')

@app.route('/owner/login', methods=['GET', 'POST'])
def owner_login():
    if current_user.is_authenticated and isinstance(current_user, Owner):
        return redirect(url_for('owner_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        owner = Owner.query.filter_by(email=email).first()
        if owner and owner.check_password(password):
            login_user(owner)
            from flask import session
            session['user_type'] = 'owner'
            flash('Login successful!', 'success')
            return redirect(url_for('owner_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('owner/login.html')

@app.route('/owner/logout')
@login_required
@owner_required
def owner_logout():
    from flask import session
    session.pop('user_type', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/owner/dashboard')
@login_required
@owner_required
def owner_dashboard():
    return render_template('owner/dashboard.html')

@app.route('/owner/packages')
@login_required
@owner_required
def owner_packages():
    packages = Package.query.filter_by(active=True).all()
    admin = Admin.query.first()
    return render_template('owner/packages.html', packages=packages, admin_bank=admin)

@app.route('/owner/purchase-package', methods=['POST'])
@login_required
@owner_required
def owner_purchase_package():
    package_id = request.form.get('package_id')
    payment_proof = request.files.get('payment_proof')
    pending = PurchaseRequest.query.filter_by(owner_id=current_user.id, status='pending').first()
    if pending:
        flash('You already have a pending purchase request!', 'warning')
        return redirect(url_for('owner_packages'))
    filename = None
    if payment_proof and allowed_file(payment_proof.filename):
        filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{payment_proof.filename}")
        payment_proof.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    purchase_request = PurchaseRequest(owner_id=current_user.id, package_id=package_id, payment_proof=filename)
    db.session.add(purchase_request)
    db.session.commit()
    flash('Purchase request submitted successfully! Wait for admin approval.', 'success')
    return redirect(url_for('owner_packages'))

@app.route('/owner/book-slot', methods=['GET', 'POST'])
@login_required
@owner_required
def owner_book_slot():
    if request.method == 'POST':
        slot_id = request.form.get('slot_id')
        if not current_user.package_active:
            flash('You need an active package to book slots!', 'danger')
            return redirect(url_for('owner_packages'))
        slot = Slot.query.get_or_404(slot_id)
        if slot.status != 'available':
            flash('This slot is not available!', 'danger')
            return redirect(url_for('owner_book_slot'))
        booking = Booking(owner_id=current_user.id, slot_id=slot_id)
        slot.status = 'booked'
        db.session.add(booking)
        db.session.commit()
        flash(f'Slot "{slot.name}" booked successfully!', 'success')
        return redirect(url_for('owner_book_slot'))
    cities = City.query.order_by(City.name).all()
    selected_city = None
    selected_region = None
    selected_subregion = None
    available_slots = []
    city_id = request.args.get('city_id')
    region_id = request.args.get('region_id')
    subregion_id = request.args.get('subregion_id')
    if city_id:
        selected_city = City.query.get(int(city_id))
    if region_id:
        selected_region = Region.query.get(int(region_id))
    if subregion_id:
        selected_subregion = SubRegion.query.get(int(subregion_id))
        available_slots = Slot.query.filter_by(subregion_id=subregion_id, status='available').all()
    return render_template('owner/book_slot.html', cities=cities, selected_city=selected_city, selected_region=selected_region, selected_subregion=selected_subregion, available_slots=available_slots)

@app.route('/owner/booking/cancel/<int:id>', methods=['POST'])
@login_required
@owner_required
def owner_cancel_booking(id):
    booking = Booking.query.get_or_404(id)
    if booking.owner_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('owner_book_slot'))
    booking.slot.status = 'available'
    booking.status = 'cancelled'
    db.session.commit()
    flash('Booking cancelled successfully!', 'info')
    return redirect(url_for('owner_book_slot'))

@app.route('/api/device/check_entry', methods=['POST'])
def api_check_entry():
    try:
        device_token = request.headers.get('Device-Token')
        if not device_token:
            return jsonify({'allow': False, 'message': 'Device token missing'}), 401
        slot = Slot.query.filter_by(device_token=device_token).first()
        if not slot:
            return jsonify({'allow': False, 'message': 'Invalid device token'}), 404
        data = request.get_json()
        card_value = data.get('value', '').upper()
        if not card_value:
            return jsonify({'allow': False, 'message': 'No card detected'}), 400
        owner = Owner.query.filter_by(rfid_card=card_value).first()
        if not owner:
            return jsonify({'allow': False, 'message': 'RFID card not registered'}), 200
        if not owner.package_active:
            return jsonify({'allow': False, 'message': 'Package not active'}), 200
        if owner.package_end_date and owner.package_end_date < datetime.utcnow():
            owner.package_active = False
            db.session.commit()
            return jsonify({'allow': False, 'message': 'Package expired'}), 200
        booking = Booking.query.filter_by(owner_id=owner.id, slot_id=slot.id, status='active').first()
        if not booking:
            return jsonify({'allow': False, 'message': 'Slot not booked by this user'}), 200
        is_exit = (slot.status == 'occupied')
        if is_exit:
            booking.status = 'completed'
            slot.status = 'available'
            db.session.commit()
            return jsonify({'allow': True, 'action': 'exit', 'message': f'Goodbye {owner.name}! Slot is now available.', 'owner': owner.name, 'car_number': owner.car_number}), 200
        else:
            slot.status = 'occupied'
            db.session.commit()
            return jsonify({'allow': True, 'action': 'entry', 'message': f'Welcome {owner.name}! Parking slot occupied.', 'owner': owner.name, 'car_number': owner.car_number}), 200
    except Exception as e:
        return jsonify({'allow': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/device/status', methods=['POST'])
def api_device_status():
    try:
        device_token = request.headers.get('Device-Token')
        if not device_token:
            return jsonify({'success': False, 'message': 'Device token missing'}), 401
        slot = Slot.query.filter_by(device_token=device_token).first()
        if not slot:
            return jsonify({'success': False, 'message': 'Invalid device token'}), 404
        data = request.get_json()
        status = data.get('status', 'available')
        if slot.status != 'booked':
            slot.status = status
            db.session.commit()
        return jsonify({'success': True, 'current_status': slot.status}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/device/check_plate', methods=['POST'])
def api_check_plate():
    try:
        gate_token = request.headers.get('Device-Token')
        if not gate_token:
            return jsonify({'allow': False, 'message': 'Gate token missing'}), 401
        subregion = SubRegion.query.filter_by(gate_device_token=gate_token).first()
        if not subregion:
            return jsonify({'allow': False, 'message': 'Invalid gate token'}), 404
        image_data = request.data
        if not image_data or len(image_data) == 0:
            return jsonify({'allow': False, 'message': 'No image data received'}), 400
        print(f"\n{'='*60}")
        print(f"Gate: {subregion.region.city.name} → {subregion.region.name} → {subregion.name}")
        print(f"Received image: {len(image_data)} bytes")
        detected_plate = None
        try:
            import easyocr
            import numpy as np
            import cv2
            import re
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return jsonify({'allow': False, 'message': 'Invalid image data'}), 400
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.bilateralFilter(gray, 11, 17, 17)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            reader = easyocr.Reader(['en'], gpu=False)
            all_results = []
            all_results.extend(reader.readtext(img))
            all_results.extend(reader.readtext(gray))
            all_results.extend(reader.readtext(thresh))
            print(f"Total OCR results: {len(all_results)}")
            plate_patterns = [r'^[A-Z]{2,4}[-\s]?\d{3,4}$', r'^[A-Z]{2,3}\d{3,4}$', r'^\d{3,4}[-\s]?[A-Z]{2,4}$']
            candidates = []
            for (bbox, text, confidence) in all_results:
                original_text = text
                text = text.upper()
                text = re.sub(r'[^A-Z0-9\-\s]', '', text)
                text = text.replace(' ', '').replace('-', '')
                if not (5 <= len(text) <= 8):
                    continue
                has_letters = bool(re.search(r'[A-Z]', text))
                has_numbers = bool(re.search(r'\d', text))
                if not (has_letters and has_numbers):
                    continue
                matches_pattern = any(re.match(p, text) for p in plate_patterns)
                score = confidence
                if matches_pattern:
                    score += 0.3
                y_center = (bbox[0][1] + bbox[2][1]) / 2
                img_height = img.shape[0]
                if 0.3 < (y_center / img_height) < 0.7:
                    score += 0.1
                candidates.append({'text': text, 'original': original_text, 'confidence': confidence, 'score': score})
                print(f"Candidate: {text} (confidence: {confidence:.2f}, score: {score:.2f})")
            candidates.sort(key=lambda x: x['score'], reverse=True)
            if candidates:
                detected_plate = candidates[0]['text']
                print(f"✓ Best: {detected_plate} (score: {candidates[0]['score']:.2f})")
        except ImportError:
            try:
                from PIL import Image
                import pytesseract
                import io
                image = Image.open(io.BytesIO(image_data))
                custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
                text = pytesseract.image_to_string(image, config=custom_config).strip().upper().replace(' ', '').replace('\n', '')
                if 5 <= len(text) <= 8:
                    detected_plate = text
            except:
                return jsonify({'allow': False, 'message': 'OCR not configured'}), 500
        except Exception as e:
            print(f"OCR Error: {e}")
            return jsonify({'allow': False, 'message': f'OCR failed: {str(e)}'}), 500
        if not detected_plate:
            return jsonify({'allow': False, 'message': 'No license plate detected'}), 200
        print(f"Final: {detected_plate}")
        owner = Owner.query.filter_by(car_number=detected_plate).first()
        if not owner:
            normalized = detected_plate.replace('-', '')
            for o in Owner.query.all():
                if o.car_number.replace('-', '').upper() == normalized:
                    owner = o
                    break
        if not owner:
            return jsonify({'allow': False, 'message': 'Vehicle not registered', 'plate': detected_plate}), 200
        if not owner.package_active:
            return jsonify({'allow': False, 'message': 'Package not active', 'plate': detected_plate, 'owner': owner.name}), 200
        if owner.package_end_date and owner.package_end_date < datetime.utcnow():
            owner.package_active = False
            db.session.commit()
            return jsonify({'allow': False, 'message': 'Package expired', 'plate': detected_plate, 'owner': owner.name}), 200
        has_booking = False
        booked_slot = None
        for slot in subregion.slots:
            booking = Booking.query.filter_by(owner_id=owner.id, slot_id=slot.id, status='active').first()
            if booking:
                has_booking = True
                booked_slot = slot.name
                break
        if not has_booking:
            return jsonify({'allow': False, 'message': 'No active booking', 'plate': detected_plate, 'owner': owner.name}), 200
        print(f"✓ ACCESS GRANTED for {owner.name}\n{'='*60}\n")
        return jsonify({'allow': True, 'message': f'Welcome {owner.name}!', 'plate': detected_plate, 'owner': owner.name, 'car_number': owner.car_number, 'subregion': subregion.name, 'slot': booked_slot}), 200
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'allow': False, 'message': f'Server error: {str(e)}'}), 500

def init_db():
    with app.app_context():
        db.create_all()
        admin = Admin.query.filter_by(email=app.config['DEFAULT_ADMIN_EMAIL']).first()
        if not admin:
            admin = Admin(email=app.config['DEFAULT_ADMIN_EMAIL'])
            admin.set_password(app.config['DEFAULT_ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            print(f"Default admin created: {app.config['DEFAULT_ADMIN_EMAIL']}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)