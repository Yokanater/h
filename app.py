from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Workspace, Note

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Removed deprecated before_first_request
# Database tables will be created in the main block

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.password_hash = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    workspaces = current_user.workspaces.all()
    return render_template('dashboard.html', workspaces=workspaces)

@app.route('/workspace/new', methods=['POST'])
@login_required
def new_workspace():
    name = request.form['name']
    description = request.form.get('description', '')
    workspace = Workspace(name=name, description=description, owner=current_user)
    db.session.add(workspace)
    db.session.commit()
    flash('Workspace created!')
    return redirect(url_for('dashboard'))

@app.route('/workspace/<int:id>')
@login_required
def view_workspace(id):
    workspace = Workspace.query.get_or_404(id)
    if workspace.owner != current_user:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    notes = workspace.notes.order_by(Note.timestamp.desc()).all()
    return render_template('workspace.html', workspace=workspace, notes=notes)

@app.route('/workspace/<int:id>/note/new', methods=['POST'])
@login_required
def new_note(id):
    workspace = Workspace.query.get_or_404(id)
    if workspace.owner != current_user:
        return redirect(url_for('dashboard'))
    
    title = request.form['title']
    note_type = request.form['note_type']
    content = request.form.get('content', '')
    media_url = request.form.get('media_url', '')
    
    note = Note(title=title, note_type=note_type, content=content, media_url=media_url, workspace=workspace)
    db.session.add(note)
    db.session.commit()
    flash('Note added!')
    return redirect(url_for('view_workspace', id=id))

@app.route('/note/<int:id>/delete')
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    workspace_id = note.workspace_id
    if note.workspace.owner != current_user:
        return redirect(url_for('dashboard'))
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('view_workspace', id=workspace_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
