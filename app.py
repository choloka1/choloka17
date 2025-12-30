import os
import random
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from os import urandom
from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import request, jsonify
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
from os import urandom
from flask import Flask,send_file
from flask_sqlalchemy import SQLAlchemy

# -------------------- CONFIG --------------------
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "sdf8#2kdn!9slq3j"  # შეიძლება იყოს ციფრებიც, ასოებიც, სიმბოლოებიც


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20))
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='seller', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    desc = db.Column(db.Text)
    img = db.Column(db.String(300))
    category = db.Column(db.String(50))
    is_approved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    region = db.Column(db.String(100), nullable=False)
    yield_per_sqm = db.Column(db.Float, nullable=False)
    market_price_per_kg = db.Column(db.Float, nullable=False)
    cost_seedlings = db.Column(db.Float, nullable=False)
    cost_labor = db.Column(db.Float, nullable=False)
    cost_fertilizer = db.Column(db.Float, nullable=False)
    cost_water = db.Column(db.Float, nullable=False)
    cost_pest = db.Column(db.Float, nullable=False)
    cost_maintenance = db.Column(db.Float, nullable=False)


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    type = db.Column(db.String(10))  # expense / income
    amount = db.Column(db.Float)
    description = db.Column(db.String(100))


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)

class CarouselImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(300), nullable=False)
    order = db.Column(db.Integer, default=0) # თანმიმდევრობისთვის

# -------------------- INIT --------------------

def send_email_thread(subject, body, to_email):
    def send():
        sender_email = "shota.cholokava17@gmail.com"
        password = "vgdc lvtc iozy jwni"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, to_email, msg.as_string())
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
    Thread(target=send).start()

with app.app_context():
    db.create_all()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            flash("გთხოვთ გაიარეთ ავტორიზაცია", "warning")
            return redirect(url_for("login"))

        user = User.query.get(user_id)
        if not user or not user.is_admin:
            flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე", "danger")
            return redirect(url_for("home"))

        return f(*args, **kwargs)
    return decorated_function


with app.app_context():
    db.create_all()

#@app.route('/admin/users')
#def admin_users():
   # if not session.get('is_admin'):
       # flash("შენ არ გაქვს წვდომა ამ გვერდზე", "danger")
        #return redirect(url_for('login'))

    #users = User.query.all()  # ყველა მომხმარებლის წამოღება DB-დან
    #return render_template('admin_users.html', users=users)

#

@app.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    if not session.get('is_admin'):
        return 2 # აკრძალულია არადმინისთვის

    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    flash('ვიდეო წაიშალა', 'success')
    return redirect(url_for('a'))  # თუ ესაა შენი ვიდეოების გვერდი


@app.route('/product_video')
def a():
    fruits = Video.query.filter_by(category="ხილი").all()
    vegetables = Video.query.filter_by(category="ბოსტნეული").all()
    tools = Video.query.filter_by(category="ხელსაწყოები").all()
    return render_template('sasargeblo.html', fruits=fruits, vegetables=vegetables, tools=tools)





@app.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    if not session.get('is_admin'):
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე", "danger")
        return redirect(url_for('profile'))


    if request.method == 'POST':
        try:
            new_crop = Crop(
                name=request.form['name'],
                region=request.form['region'],
                yield_per_sqm=float(request.form['yield_per_sqm']),
                market_price_per_kg=float(request.form['market_price']),
                cost_seedlings=float(request.form['cost_seedlings']),
                cost_labor=float(request.form['cost_labor']),
                cost_fertilizer=float(request.form['cost_fertilizer']),
                cost_water=float(request.form['cost_water']),
                cost_pest=float(request.form['cost_pest']),
                cost_maintenance=float(request.form['cost_maintenance'])
            )
            db.session.add(new_crop)
            db.session.commit()
            flash("კულტურა წარმატებით დაემატა", "success")
        except Exception as e:
            flash(f"შეცდომა: {e}", "danger")

    return render_template('add_crop.html')

@app.route("/add/panel")
def admin_panel():
    def add_crop():
        if not session.get('is_admin'):
            flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე", "danger")
            return redirect(url_for('profile'))
    return render_template("admin_dashboard.html")


@app.route('/admin/crops')
def admin_crops():
    if not session.get('is_admin'):
        flash("არ გაქვთ წვდომა", "danger")
        return redirect(url_for('profile'))

    crops_list = Crop.query.all()
    return render_template('admin_crops.html', crops=crops_list)

@app.route('/manage_posts', methods=['GET', 'POST'])
def manage_posts():
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        image = request.files.get('image')
        image_url = ''
        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            image_url = f"/static/uploads/{filename}"

        new_post = Post(title=title, content=content, image_url=image_url)
        db.session.add(new_post)
        db.session.commit()
        flash('პოსტი წარმატებით აიტვირთა!')
        return redirect(url_for('manage_posts'))

    return render_template('manage_posts.html')

from sqlalchemy import or_
@app.route("/post")
def post_list():
    # ვიღებთ საძიებო სიტყვას
    query = request.args.get('q', '').strip()

    if query:
        # ვიყენებთ or_ ფუნქციას და ilike-ს (უფრო მოქნილი ძებნისთვის)
        posts = Post.query.filter(
            or_(
                Post.title.ilike(f"%{query}%"),
                Post.content.ilike(f"%{query}%")
            )
        ).order_by(Post.created_at.desc()).all()
    else:
        # თუ ძებნა ცარიელია, ვაჩვენებთ ყველა პოსტს
        posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template("post_list.html", posts=posts, search_query=query)

@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post_detail.html", post=post)


from flask import request


@app.route("/post")
def post_list1():
    # ვიღებთ საძიებო სიტყვას URL-იდან (მაგ: /post?q=ვაშლი)
    query = request.args.get('q', '')

    if query:
        # ვფილტრავთ პოსტებს: ან სათაური შეიცავს სიტყვას, ან შინაარსი
        posts = Post.query.filter(
            db.or_(
                Post.title.contains(query),
                Post.content.contains(query)
            )
        ).order_by(Post.created_at.desc()).all()
    else:
        # თუ ძებნა არ არის, ვაჩვენებთ ყველა პოსტს
        posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template("post_list.html", posts=posts, search_query=query)



@app.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if not session.get('is_admin'):
        flash("⛔ მხოლოდ ადმინს აქვს წვდომა.")
        return redirect(url_for('post_list'))

    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']

        image = request.files.get('image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            post.image_url = f"/static/uploads/{filename}"

        try:
            db.session.commit()
            flash("✅ პოსტი წარმატებით განახლდა.")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ შეცდომა: {e}")

        return redirect(url_for('post_list'))

    return render_template('edit_post.html', post=post)


@app.route('/post/delete/<int:post_id>')
def delete_post(post_id):
    if not session.get('is_admin'):
        flash("⛔ მხოლოდ ადმინს აქვს წვდომა.")
        return redirect(url_for('post_list'))

    post = db.session.merge(Post.query.get_or_404(post_id))  # სწორი სესიაში დაბრუნება
    db.session.delete(post)
    db.session.commit()
    flash('🗑️ პოსტი წაიშალა.')
    return redirect(url_for('post_list'))


@app.route("/rare", endpoint='rare_page')
def rare():
    return render_template("info pet and.html")







@app.route('/very1', methods=['GET', 'POST'], endpoint='index')
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("გთხოვთ შეიყვანოთ ელფოსტა", "error")
            return redirect(url_for('index'))

        verification_code = random.randint(100001, 999999)
        session['verification_code'] = verification_code
        session['email'] = email

        subject = "ვერიფიკაციის კოდი"
        body = f"თქვენი ვერიფიკაციის კოდია: {verification_code}"

        sender_email = "shota.cholokava17@gmail.com"
        password = "vgdc lvtc iozy jwni"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, email, msg.as_string())
            flash("ვერიფიკაციის კოდი გაიგზავნა ელფოსტაზე", "success")
            return redirect(url_for('verify1'))
        except Exception as e:
            flash(f"შეცდომა გაგზავნისას: {e}", "error")
            return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/verify1')
def verify1():
    return render_template('verify.html')

@app.route('/verify', methods=['POST'])
def verify():
    code = request.form.get('code')
    try:
        if int(code) == session.get('verification_code'):
            user_data = session.get('registration_data')
            if user_data:
                new_user = User(
                    name=user_data['name'],
                    surname=user_data['surname'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    state=user_data['state'],
                    city=user_data['city']
                )
                db.session.add(new_user)
                db.session.commit()
                session.pop('registration_data', None)
                session.pop('verification_code', None)
                flash("რეგისტრაცია დასრულდა!", "success")
                return redirect(url_for('login'))
            else:
                flash("მონაცემები არ მოიძებნა", "error")
        else:
            flash("არასწორი ვერიფიკაციის კოდი", "error")
    except ValueError:
        flash("კოდი უნდა იყოს რიცხვი", "error")
    return render_template('verify.html')
    


@app.route('/paroli', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            new_password = str(random.randint(100000, 999999))
            hashed_password = generate_password_hash(new_password)
            user.password_hash = hashed_password
            db.session.commit()

            subject = "ახალი პაროლი"
            body = f"თქვენი ახალი პაროლია: {new_password}"
            send_email_thread(subject, body, email)

            flash("ახალი პაროლი გაიგზავნა ელფოსტაზე", "success")
        else:
            flash("ელფოსტა არ არის რეგისტრირებული", "danger")

    return render_template('forgot.html')
    

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("გთხოვთ გაიარეთ ავტორიზაცია", "warning")
        return redirect(url_for('login', next=request.path))

    user = User.query.get(user_id)
    if not user:
        flash("მომხმარებელი ვერ მოიძებნა", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        state = request.form.get('state')
        city = request.form.get('city')
        zip_code = request.form.get('zip_code')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # აუცილებელია რეგიონის შერჩევა
        if not state:
            flash("გთხოვ, აირჩიე რეგიონი", "danger")
            return redirect(url_for('profile'))

        # ვამოწმებთ პაროლს თუ შეიყვანა
        if new_password:
            if new_password != confirm_password:
                flash("პაროლები არ ემთხვევა", "danger")
                return redirect(url_for('profile'))
            user.password_hash = generate_password_hash(new_password)

        admin_code = request.form.get('admin_code')
        if admin_code == 'mindori1232':
            session['is_admin'] = True
            user.is_admin = True
            flash("თქვენ გახდით ადმინისტრატორი!", "success")


        # პროფილის სხვა ველების განახლება
        user.name = name
        user.surname = surname
        user.state = state
        user.city = city
        user.zip_code = zip_code

        db.session.commit()
        session['state'] = user.state

        flash("პროფილი წარმატებით განახლდა", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.name
            session['state'] = user.state
            session['is_admin'] = user.is_admin
            return redirect(url_for('home'))
        else:
            flash("არასწორი ელფოსტა ან პაროლი", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("შედი ან დარეგისტრირდი რათა ისარგებლო ყველა ფუნქციით", "info")
    return redirect(url_for('login'))



@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    result = None
    state = session.get('state')

    if not state:
        flash("გთხოვთ დალოგინდით ან დარეგისტრირდეთ", "warning")
        return redirect(url_for('login', next=request.path))

    allowed_crops = Crop.query.filter_by(region=state).all()
    crops_dict = {
        crop.name: {
            "yield_per_sqm": crop.yield_per_sqm,
            "market_price_per_kg": crop.market_price_per_kg,
            "costs": {
                "ნერგების ფასი": crop.cost_seedlings,
                "შრომა": crop.cost_labor,
                "სასუქი": crop.cost_fertilizer,
                "წყალი": crop.cost_water,
                "მავნებლების კონტროლი": crop.cost_pest,
                "მოვლა და პატრონობა": crop.cost_maintenance
            }
        } for crop in allowed_crops
    }

    if request.method == 'POST':
        try:
            length = float(request.form.get('length') or 0)
            width = float(request.form.get('width') or 0)
            area = float(request.form.get('area') or 0)
            crop_name = request.form.get('crop')

            if crop_name not in crops_dict:
                flash("გთხოვთ აირჩიოთ რეგიონისთვის შესაბამისი კულტურა", "error")
                return redirect(url_for('analyze'))

            total_area = length * width if length and width else area
            crop_data = crops_dict[crop_name]
            yield_total = total_area * crop_data['yield_per_sqm']
            income = yield_total * crop_data['market_price_per_kg']
            cost_details = {k: v * total_area for k, v in crop_data['costs'].items()}
            total_costs = sum(cost_details.values())
            profit = income - total_costs

            result = {
                'area': round(total_area, 2),
                'yield': round(yield_total, 2),
                'income': round(income, 2),
                'costs': round(total_costs, 2),
                'profit': round(profit, 2),
                'cost_details': {k: round(v, 2) for k, v in cost_details.items()}
            }

        except Exception as e:
            flash(f"შეცდომა: {e}", "error")

    return render_template('analyze.html', crops=crops_dict, result=result)


comments = []
comment_counter = 1
@app.route('/forum', methods=['GET', 'POST'])
def forum():
    global comment_counter

    success = False
    if request.method == 'POST':
        username = request.form['username']
        text = request.form['comment']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        comments.append({
            'id': comment_counter,
            'username': username,
            'text': text,
            'timestamp': timestamp,
            'reply': None
        })
        comment_counter += 1
        success = True

    is_admin = session.get('is_admin', False)
    return render_template('forum.html', comments=comments, success=success, is_admin=is_admin)

@app.route('/admin/edit_crop/<int:crop_id>', methods=['GET', 'POST'])
@admin_required
def edit_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)

    if request.method == 'POST':
        try:
            crop.name = request.form['name']
            crop.region = request.form['region']
            crop.yield_per_sqm = float(request.form['yield_per_sqm'])
            crop.market_price_per_kg = float(request.form['market_price'])
            crop.cost_seedlings = float(request.form['cost_seedlings'])
            crop.cost_labor = float(request.form['cost_labor'])
            crop.cost_fertilizer = float(request.form['cost_fertilizer'])
            crop.cost_water = float(request.form['cost_water'])
            crop.cost_pest = float(request.form['cost_pest'])
            crop.cost_maintenance = float(request.form['cost_maintenance'])

            db.session.commit()
            flash("კულტურა განახლდა", "success")
            return redirect(url_for('admin_crops'))
        except Exception as e:
            flash(f"შეცდომა: {e}", "danger")

    return render_template('edit_crop.html', crop=crop)

@app.route('/admin/delete_crop/<int:crop_id>', methods=['POST'])
@admin_required
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    db.session.delete(crop)
    db.session.commit()
    flash("კულტურა წაიშალა", "info")
    return redirect(url_for('admin_crops'))




@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403
    global comments
    comments = [c for c in comments if c['id'] != comment_id]
    return redirect(url_for('forum'))

@app.route('/reply_comment/<int:comment_id>', methods=['POST'])
def reply_comment(comment_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403
    reply_text = request.form.get('reply_text')
    for comment in comments:
        if comment['id'] == comment_id:
            comment['reply'] = reply_text
            break
    return redirect(url_for('forum'))



@app.route("/rare", endpoint='rare')
def rare():
    return render_template("info pet and.html")


@app.route("/lesse", endpoint='lesse')
def lesse():
    return render_template("online.html")
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        state = request.form.get('state')
        city = request.form.get('city')

        if User.query.filter_by(email=email).first():
            flash("ელფოსტა უკვე რეგისტრირებულია", "danger")
            return render_template('register form.html')

        if password != confirm_password:
            flash("პაროლები არ ემთხვევა", "danger")
            return render_template('register form.html')

        hashed_password = generate_password_hash(password)

        verification_code = random.randint(100001, 999999)
        session['verification_code'] = verification_code
        session['registration_data'] = {
            'name': name,
            'surname': surname,
            'email': email,
            'password_hash': hashed_password,
            'state': state,
            'city': city
        }

        # ელფოსტის გაგზავნა thread-ში
        subject = "ვერიფიკაციის კოდი"
        body = f"თქვენი ვერიფიკაციის კოდია: {verification_code}"
        send_email_thread(subject, body, email)

        flash("ვერიფიკაციის კოდი გაიგზავნა ელფოსტაზე", "success")
        return redirect(url_for('verify1'))

    return render_template('register form.html')

   


@app.route('/archevani', endpoint='archevani')
def page():
    return render_template('data.html')


@app.route('/about', endpoint='about')
def about():
    return render_template('about.html')




@app.route('/')
@app.route('/home')
@app.route('/form1')
def home(): # სახელი შევცვალეთ 'home'-ზე, რომ login-მა იპოვოს
    # 1. ყველა პოსტი ბლოგის სექციისთვის
    all_posts = Post.query.order_by(Post.created_at.desc()).all()

    # 2. ბოლო 5 პოსტი "Insights" (ქვედა) სექციისთვის
    # ეს ცვლადი აუცილებელია ახალი HTML-ისთვის
    latest = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    # 3. კარუსელის სურათები (რომელიც ბაზაში გიჩანთ - image_ee6ca2.png)
    images = CarouselImage.query.order_by(CarouselImage.order).all()

    # აუცილებელია სამივე ცვლადის გადაწოდება HTML-სთვის
    return render_template("form1.html",
                           posts=all_posts,
                           latest_posts=latest,
                           carousel_imgs=images)

@app.route('/agroshop')
def agroshop():
    return render_template('agroshop.html')

##################################### <=========================> #############################################
# --- 1. კატეგორიის გვერდი (აჩვენებს მხოლოდ დადასტურებულ პროდუქტებს) ---
@app.route('/category/<name>')
def category_page(name):
    # ბაზიდან ვიღებთ მხოლოდ იმ პროდუქტებს, რომლებიც ამ კატეგორიისაა და ადმინმა დაადასტურა
    products = Product.query.filter_by(category=name, is_approved=True).all()

    # გადავცემთ კატეგორიის სახელსაც, რომ გვერდზე სათაურად დავაწეროთ
    return render_template('category_products.html', products=products, category_name=name)
# --- 2. პროდუქტის დეტალური გვერდი ---
@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_details.html', product=product)


# --- 3. პროდუქტის ატვირთვა (მომხმარებლისთვის) ---
@app.route('/upload', methods=['GET', 'POST'])
def upload_product():
    if not session.get('user_id'):
        flash("პროდუქტის ასატვირთად გაიარეთ ავტორიზაცია", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        category = request.form.get('category')
        img = request.form.get('img')
        desc = request.form.get('desc')

        if name and price:
            new_product = Product(
                name=name,
                price=float(price),
                category=category,
                img=img,
                desc=desc,
                is_approved=False,  # ადმინმა უნდა დაადასტუროს
                user_id=session.get('user_id')
            )
            db.session.add(new_product)
            db.session.commit()
            flash('პროდუქტი გაიგზავნა ადმინთან დასადასტურებლად!', 'success')
            return redirect(url_for('home'))

    return render_template('upload_prod.html')

@app.route('/export_analysis_excel', methods=['POST'])
def export_analysis_excel():
    # ვიღებთ მონაცემებს ფორმიდან
    area = request.form.get('area')
    crop = request.form.get('crop')
    yield_kg = request.form.get('yield')
    income = request.form.get('income')
    costs = request.form.get('costs')
    profit = request.form.get('profit')

    # მონაცემების მომზადება Excel-ისთვის
    data = {
        "პარამეტრი": ["კულტურა", "ფართობი (მ²)", "მოსავალი (კგ)", "შემოსავალი (₾)", "ჯამური ხარჯი (₾)", "წმინდა მოგება (₾)"],
        "მნიშვნელობა": [crop, area, yield_kg, income, costs, profit]
    }

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analysis_Report')

    output.seek(0)
    return send_file(output,
                     download_name=f"Agro_Analysis_{crop}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                     as_attachment=True)


# --- 4. კალათის ჩვენება და დაჯამება ---
@app.route('/cart')
def show_cart():
    cart = session.get('cart', [])
    items = []
    total_sum = 0

    for entry in cart:
        product = Product.query.get(entry['id'])
        if product:
            items.append({'product': product, 'weight': entry['weight']})
            total_sum += product.price * entry['weight']

    return render_template('cart.html', items=items, total_sum=total_sum)


# --- 5. კალათაში დამატება (წონის გათვალისწინებით) ---
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    weight = float(request.form.get('weight', 1))

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    cart.append({'id': product_id, 'weight': weight})
    session['cart'] = cart
    session.modified = True

    flash('პროდუქტი დაემატა კალათაში!', 'success')
    return redirect(url_for('show_cart'))


# --- 6. კალათიდან წაშლა ---
@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('show_cart'))


# --- 7. ადმინ პანელი: მომლოდინე პროდუქტები ---
@app.route('/admin/products')
@admin_required
def admin_products():
    if not session.get('is_admin'):
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე!", "danger")
        return redirect(url_for('login'))

    pending_products = Product.query.filter_by(is_approved=False).all()
    return render_template('admin_products.html', products=pending_products)


# --- 8. ადმინ პანელი: დადასტურება ---
@app.route('/admin/approve_product/<int:product_id>')
@admin_required
def approve_product(product_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403

    product = Product.query.get_or_404(product_id)
    product.is_approved = True
    db.session.commit()

    flash(f"პროდუქტი '{product.name}' გამოქვეყნდა!", "success")
    return redirect(url_for('admin_products'))


# --- 9. ადმინ პანელი: უარყოფა (წაშლა) ---
@app.route('/admin/reject_product/<int:product_id>')
@admin_required
def reject_product(product_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    flash("პროდუქტი უარყოფილია.", "info")
    return redirect(url_for('admin_products'))


@app.route('/delete_product_catalog/<int:product_id>')
def delete_product_catalog(product_id):
    # ვამოწმებთ, არის თუ არა მომხმარებელი ადმინი
    if not session.get('is_admin'):
        flash("წვდომა აკრძალულია!", "danger")
        return redirect(url_for('index'))

    product = Product.query.get_or_404(product_id)
    category_to_return = product.category  # ვიმახსოვრებთ კატეგორიას რედირექტისთვის

    db.session.delete(product)
    db.session.commit()

    flash(f"პროდუქტი '{product.name}' წარმატებით წაიშალა.", "info")
    return redirect(url_for('category_page', name=category_to_return))
####ადმმინის გვერდი მომხმარებლის წაშლა და დამატება
@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        flash("წვდომა აკრძალულია!", "danger")
        return redirect(url_for('login'))

    # ყველა მომხმარებლის წამოღება
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=all_users)


@app.route('/admin/toggle_admin/<int:user_id>')
def toggle_admin(user_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    # უსაფრთხოება: საკუთარ თავს ადმინს ვერ ჩამოართმევ
    if user.id == session.get('user_id'):
        flash("საკუთარ სტატუსს ვერ შეცვლით!", "warning")
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = "ადმინად" if user.is_admin else "მომხმარებლად"
        flash(f"{user.name} გადაკეთდა {status}.", "success")

    return redirect(url_for('admin_users'))


@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    if user.id == session.get('user_id'):
        flash("საკუთარ თავს ვერ წაშლით!", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"მომხმარებელი {user.email} წაიშალა.", "info")

    return redirect(url_for('admin_users'))

def send_feedback_email(receiver_email, product_name, status, feedback):
    # შენი SMTP კონფიგურაცია
    sender_email = "shota.cholokava17@gmail.com"
    password = "vgdc lvtc iozy jwni"

    subject = f"სიახლე თქვენი პროდუქტის შესახებ: {product_name}"

    status_ka = "დადასტურდა" if status == "approve" else "არ დადასტურდა"

    body = f"""
    მოგესალმებით,

    თქვენი პროდუქტი '{product_name}' ადმინისტრაციის მიერ {status_ka}.

    ადმინისტრატორის კომენტარი:
    {feedback if feedback else 'კომენტარი არ გაკეთებულა.'}

    მადლობა, რომ იყენებთ AgroShop-ს!
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")


@app.route('/admin/process_product/<int:product_id>', methods=['POST'])
def process_product(product_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403

    product = Product.query.get_or_404(product_id)
    status = request.form.get('status')  # approve ან reject
    feedback = request.form.get('feedback')  # textarea-ს ტექსტი

    seller_email = product.seller.email if product.seller else None
    product_name = product.name

    if status == 'approve':
        product.is_approved = True
        db.session.commit()
        flash("პროდუქტი დადასტურდა", "success")
    else:
        db.session.delete(product)
        db.session.commit()
        flash("პროდუქტი წაიშალა", "info")

    # იმეილის გაგზავნა
    if seller_email:
        send_feedback_email(seller_email, product_name, status, feedback)

    return redirect(url_for('admin_products'))





@app.route('/admin/export_users')
@admin_required
def export_users():
    users = User.query.all()

    # მონაცემების მომზადება
    data = []
    for user in users:
        data.append({
            "სახელი": user.name,
            "გვარი": user.surname,
            "ელფოსტა": user.email,
            "ქალაქი": user.city,
            "რეგიონი": user.state,
            "რეგისტრაციის თარიღი": user.created_at.strftime('%Y-%m-%d')
        })

    # Pandas-ის გამოყენებით ექსელის შექმნა
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')

    output.seek(0)

    return send_file(output,
                     download_name=f"users_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                     as_attachment=True)


@app.route('/admin/carousel', methods=['GET', 'POST'])
@admin_required
def manage_carousel():
    if request.method == 'POST':
        file = request.files.get('carousel_img')
        order = request.form.get('order', 0)

        if file and file.filename:
            filename = secure_filename(file.filename)
            # ვამატებთ დროს ფაილის სახელს, რომ დუბლიკატები არ მოხდეს
            filename = f"{datetime.now().timestamp()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_img = CarouselImage(image_url=f"/static/uploads/{filename}", order=int(order))
            db.session.add(new_img)
            db.session.commit()
            flash("ფოტო წარმატებით დაემატა კარუსელს!", "success")
            return redirect(url_for('manage_carousel'))

    images = CarouselImage.query.order_by(CarouselImage.order).all()
    return render_template('manage_carousel.html', images=images)


@app.route('/admin/carousel/delete/<int:id>')
@admin_required
def delete_carousel_image(id):
    img = CarouselImage.query.get_or_404(id)
    # ფიზიკური ფაილის წაშლა სერვერიდან (სურვილისამებრ)
    try:
        os.remove(os.path.join(os.getcwd(), img.image_url.strip('/')))
    except:
        pass

    db.session.delete(img)
    db.session.commit()
    flash("ფოტო წაიშალა კარუსელიდან.", "info")
    return redirect(url_for('manage_carousel'))
if __name__ == '__main__':
    app.run(debug=True)

