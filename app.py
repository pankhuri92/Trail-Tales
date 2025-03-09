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
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    date_published = db.Column(db.Date, nullable=False, default=datetime.date.today)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/travel_stories')
def travel_stories():
    blogs = Blog.query.order_by(Blog.date_published.desc()).all()  # Fetch blogs ordered by date
    return render_template('travel_stories.html', blogs=blogs)

@app.route('/blog/<int:blog_id>')
def view_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)  # Fetch blog by ID
    return render_template('view_blog.html', blog=blog)

@app.route('/create_blog', methods=['GET', 'POST'])
def create_blog():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')

        if title and content:
            image_filename = None  # Default case if no image is uploaded

            if image:
                image_filename = os.path.join(UPLOAD_FOLDER, image.filename)
                image.save(image_filename)  # Save the image to the upload folder

            # Save to Database
            new_blog = Blog(title=title, content=content, image_url="/"+image_filename)
            db.session.add(new_blog)
            db.session.commit()

            return redirect(url_for('travel_stories'))

    return render_template('create_blog.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=True)
