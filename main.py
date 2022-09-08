import os

from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename

from data import db_session
from data.users import User, Moment


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
try:
    os.mkdir(UPLOAD_FOLDER)
except FileExistsError:
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'inthemoment'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)
# ngrok = run_with_ngrok(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    user_device = request.user_agent.platform
    user_device = 'android'
    return render_template('index.html', user_device=user_device, title='#явмоменте')


@app.route('/search', methods=['GET', 'POST'])
def search():
    user_device = request.user_agent.platform
    user_device = 'android'
    return render_template('search.html', user_device=user_device)


@app.route('/add_moment', methods=['GET', 'POST'])
def add_moment():
    user_device = request.user_agent.platform
    user_device = 'android'
    if request.method == 'POST':
        db_sess = db_session.create_session()
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        moment = Moment(
            image=file.filename,
            description=request.form.get('description'),
        )
        db_sess.add(moment)
        db_sess.commit()
        return redirect('/')
    return render_template('add_moment.html', user_device=user_device)


@app.route('/user_cabinet', methods=['GET', 'POST'])
def user_cabinet():
    user_device = request.user_agent.platform
    user_device = 'android'

    return render_template('user_cabinet.html', user_device=user_device)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_device = request.user_agent.platform
    user_device = 'android'
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id
                                          ).first()
        if user:
            user.city = request.form.get('city')
            user.description = request.form.get('description')
            user.first_name = request.form.get('first_name')
            user.second_name = request.form.get('second_name')
            user.email = request.form.get('email')
            user.username = request.form.get('username')
            db_sess.commit()
            return redirect('/user_cabinet')
    return render_template('edit_profile.html', user_device=user_device)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_device = request.user_agent.platform
    user_device = 'android'

    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect("/user_cabinet")
        return render_template('login.html', message="Wrong login or password")
    return render_template('login.html', user_device=user_device)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    user_device = request.user_agent.platform
    user_device = 'android'

    if request.method == 'POST':
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == request.form.get('email')).first():
            return render_template('registration.html', message="Ты уже зареган")
        elif request.form.get('password') != request.form.get('check_password'):
            return render_template('registration.html', message="Не совпадают")
        else:
            user = User(
                first_name=request.form.get('first_name'),
                second_name=request.form.get('second_name'),
                email=request.form.get('email'),
                username=request.form.get('username'),
            )
            user.set_password(request.form.get('password'))
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
    return render_template('registration.html', user_device=user_device)


if __name__ == "__main__":
    db_session.global_init("db/main.sqlite")
    app.run(debug=True)
