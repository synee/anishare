# -*- coding: utf-8 -*-
from functools import wraps
from flask import session, url_for, redirect, request, render_template
from ani import storage


def get_actions(app):
    from anishare import User, db
    from ani.utils import get_namespace

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user():
            return redirect(url_for('index'))
        error = None
        if request.method == "POST":
            user = User.query.filter_by(email=request.form['email']).first()
            if not user:
                user = User(username=request.form['email'], email=request.form['email'],
                            password=request.form['password'])
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                error = "邮箱已注册"
        return render_template('register.html', error=error)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user():
            return redirect(url_for('index'))
        error = None
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
            if user:
                session['user_id'] = user.id
                return redirect(url_for('index'))
            else:
                error = "用户名或者密码不正确"
        return render_template('login.html', error=error)

    @app.route('/logout')
    @require_login
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('login'))

    @app.route("/profile", methods=["GET", "POST"])
    @app.route("/profile/<panel>", methods=["GET", "POST"])
    def profile(panel='baseinfo'):

        if request.method == "POST":
            getattr(Profile(), 'update_%s' % panel)()

        def get_nav_class(nav):
            clazz = ''
            if nav == panel:
                clazz += 'active'
            return clazz

        return render_template('profile/index.html', **get_namespace(panel=panel, get_nav_class=get_nav_class))

    class Profile(object):
        def update_baseinfo(self):
            user = current_user()
            attach_upload = request.files.get('avatar')
            if attach_upload:
                attach = storage.save(attach_upload, app)
                user.avatar = attach.url
                db.session.commit()
            user.nickname = request.form.get('nickname', user.nickname)
            db.session.commit()
            return True


def current_user():
    from anishare import User

    return User.query.filter_by(id=session.get('user_id', 0)).first()


def require_login(fn):
    @wraps(fn)
    def dectorator(*args, **kwargs):
        if not current_user():
            return redirect(url_for('login'))
        return fn(*args, **kwargs)

    return dectorator
