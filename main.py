from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO, emit
from models import db, User, Gallery, MediaItem, Comment
from auth import auth
import os
from datetime import datetime
from PIL import Image
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.register_blueprint(auth, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_file(file, file_type):
    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}_{file.filename}"
    
    if file_type == 'image':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', unique_filename)
        with Image.open(file) as img:
            img.thumbnail((800, 800))
            img.save(file_path)
        return f"photos/{unique_filename}"
    else:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', unique_filename)
        file.save(file_path)
        return f"videos/{unique_filename}"

@app.route('/gallery/create', methods=['POST'])
def create_gallery():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401

    title = request.form.get('title')
    description = request.form.get('description')
    template = request.form.get('template', 'default')
    
    gallery = Gallery(
        title=title,
        description=description,
        template=template,
        user_id=current_user.id
    )
    
    db.session.add(gallery)
    db.session.commit()
    
    photos = request.files.getlist('photos')
    video = request.files.get('video')
    
    for photo in photos:
        if photo and photo.filename:
            filename = save_file(photo, 'image')
            media_item = MediaItem(
                type='photo',
                filename=filename,
                gallery_id=gallery.id
            )
            db.session.add(media_item)
    
    if video and video.filename:
        filename = save_file(video, 'video')
        media_item = MediaItem(
            type='video',
            filename=filename,
            gallery_id=gallery.id
        )
        db.session.add(media_item)
    
    db.session.commit()
    return jsonify({'gallery_id': gallery.id}), 201

@socketio.on('comment')
def handle_comment(data):
    if not current_user.is_authenticated:
        return
    
    comment = Comment(
        content=data['content'],
        user_id=current_user.id,
        gallery_id=data['gallery_id']
    )
    
    db.session.add(comment)
    db.session.commit()
    
    emit('new_comment', {
        'content': comment.content,
        'username': current_user.username,
        'created_at': comment.created_at.isoformat()
    }, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=3000)