import datetime
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Image Upload Configuration
UPLOAD_FOLDER = 'static/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exist

db = SQLAlchemy(app)

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

@app.route('/travel_stories')
def travel_stories():
    category = request.args.get('category', 'all')  # Get category from query parameter
    if category == 'all':
        blogs = Blog.query.order_by(Blog.date_published.desc()).all()
    else:
        blogs = Blog.query.filter_by(category=category).order_by(Blog.date_published.desc()).all()
    return render_template('travel_stories.html', blogs=blogs, category=category)

    # blogs = Blog.query.order_by(Blog.date_published.desc()).all()  # Fetch blogs ordered by date
    # return render_template('travel_stories.html', blogs=blogs)

@app.route('/blog/<int:blog_id>')
def view_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)  # Fetch blog by ID
    return render_template('view_blog.html', blog=blog)

@app.route('/create_blog', methods=['GET', 'POST'])
def create_blog():
    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')

        if title and content:
            image_filename = None  

            if image:
                image_filename = os.path.join(UPLOAD_FOLDER, image.filename)
                image.save(image_filename)  # Save the image to the upload folder

            # Save to Database
            new_blog = Blog(category=category, title=title, content=content if category == 'blog' else '', image_url="/"+image_filename if image_filename else None)
            db.session.add(new_blog)
            db.session.commit()

            return redirect(url_for('travel_stories'))

    return render_template('create_blog.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=True)
