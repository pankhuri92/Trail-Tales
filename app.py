import datetime
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key for session security

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Image Upload Configuration
UPLOAD_FOLDER = 'static/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists

db = SQLAlchemy(app)

# Firebase Admin SDK Initialization
cred = credentials.Certificate("we-trail-tales-firebase-adminsdk-fbsvc-b385a2e079.json")  
firebase_admin.initialize_app(cred)

# Firebase REST API Endpoint
FIREBASE_WEB_API_KEY = ""  
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"

# Database Model
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    date_published = db.Column(db.Date, nullable=False, default=datetime.date.today)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

@app.route('/travel_stories')
def travel_stories():
    category = request.args.get('category', 'all')
    if category == 'all':
        blogs = Blog.query.order_by(Blog.date_published.desc()).all()
    else:
        blogs = Blog.query.filter_by(category=category).order_by(Blog.date_published.desc()).all()
    return render_template('travel_stories.html', blogs=blogs, category=category)

@app.route('/blog/<int:blog_id>')
def view_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('view_blog.html', blog=blog)

@app.route('/create_blog', methods=['GET', 'POST'])
def create_blog():
    if "user_id" not in session:
        flash("You must be logged in to create a blog.", "warning")
        return redirect(url_for("login"))

    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')

        image_filename = None  
        if image:
            image_filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_filename)

        new_blog = Blog(
            category=category, 
            title=title, 
            content=content if category == 'blog' else '', 
            image_url="/" + image_filename if image_filename else None
        )
        db.session.add(new_blog)
        db.session.commit()
        flash("Blog created successfully!", "success")
        return redirect(url_for('travel_stories'))

    return render_template('create_blog.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"Login attempt: {email} - {password}")  # Debugging

        try:
            response = requests.post(FIREBASE_AUTH_URL, json={
                "email": email, 
                "password": password, 
                "returnSecureToken": True
            })
            data = response.json()
            
            print(f"Firebase Response: {data}")  # Debugging

            if "idToken" in data:
                user = auth.get_user_by_email(email)
                session["user_id"] = user.uid
                session["id_token"] = data["idToken"]
                flash("Login successful!", "success")
                return redirect(url_for("index"))
            else:
                error_message = data.get("error", {}).get("message", "Invalid email or password!")
                flash(f"Login failed: {error_message}", "danger")
                print(f"Login failed: {error_message}")  # Debugging
        except Exception as e:
            flash(f"Login error: {str(e)}", "danger")
            print(f"Login error: {str(e)}")  # Debugging
    
    return render_template("login.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            user = auth.create_user(email=email, password=password)
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Signup error: {str(e)}", "danger")
    
    return render_template("signup.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=True)
