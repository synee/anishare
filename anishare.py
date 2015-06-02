import datetime
import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask.ext.auth import Auth
from flask.ext.sqlalchemy import SQLAlchemy
from ani import groups as ani_groups, auth as ani_auth
from ani.utils import get_namespace

BASE_DIR = os.path.dirname(__file__)
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/development.db' % BASE_DIR
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'upload')
db = SQLAlchemy(app)
auth = Auth(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(32), unique=True, index=True)
    username = db.Column(db.String(16), unique=True, index=True)
    password = db.Column(db.String(16))
    active = db.Column(db.Boolean, default=False, index=True)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now, index=True)

    nickname = db.Column(db.String(32), index=True)
    avatar = db.Column(db.String(128))

    @property
    def my_groups(self):
        return Group.query.filter(Group.id.in_([gu.group_id for gu in GroupUser.query.filter_by(user_id=self.id)]))

    def __init__(self, username, email, password):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return self.nickname or self.username


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)
    name = db.Column(db.String(32), index=True)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    # 访问限制: 0: 公开; 1: 私有
    access_limit = db.Column(db.SmallInteger, default=0)
    # 成员总数
    member_count = db.Column(db.Integer, default=0)
    # 使用空间大小
    attach_size_use = db.Column(db.Integer, default=0)
    # 使用空间限制
    attach_size_limit = db.Column(db.Integer, default=0)

    def join_user(self, user, role=0):
        group_user = self.contain_user(user)
        if not self.contain_user(user):
            group_user = GroupUser(user_id=user.id, group_id=self.id, role=role)
            db.session.add(group_user)
            db.session.commit()
        return group_user

    def remove_user(self):
        raise NotImplementedError()

    def contain_user(self, user):
        return GroupUser.query.filter_by(user_id=user.id, group_id=self.id).first()

    def get_attachs(self, date_right=None, date_left=None, limit=100):
        if not date_right:
            date_right = datetime.datetime.now()
        f = [Attach.date_created < date_right, ]
        if date_left:
            f.append(Attach.date_created > date_left)

        return Attach.query.filter(*f).filter_by(group_id=self.id).order_by(Attach.date_created)[:limit]

    def get_posts(self, date_right=None, date_left=None, limit=100):
        if not date_right:
            date_right = datetime.datetime.now()
        f = [GroupPost.date_created < date_right, ]
        if date_left:
            f.append(GroupPost.date_created > date_left)

        return GroupPost.query.filter(*f).filter_by(group_id=self.id).order_by(GroupPost.date_created)[:limit]

    def members(self):
        raise NotImplementedError()

    def __init__(self, name, creator_id, parent_id):
        self.name = name
        self.creator_id = creator_id
        self.parent_id = parent_id

    def __repr__(self):
        return '<Group %r>' % self.name


class GroupUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)
    role = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, group_id, role=0):
        self.user_id = user_id
        self.group_id = group_id
        self.role = role

    def __repr__(self):
        return '<GroupUser %r>' % self.name


class GroupInvite(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(32), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)
    token = db.Column(db.String(128))
    feedback = db.Column(db.SmallInteger, default=0)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now)


class Attach(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True, index=True)

    url = db.Column(db.String(256))
    name = db.Column(db.String(128))
    size = db.Column(db.Integer)
    hash = db.Column(db.String(128), index=True)
    mime_type = db.Column(db.String(128))
    extension = db.Column(db.String(32))

    download_count = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, url, name, size, hash, mime_type, extension):
        self.user_id = user_id
        self.url = url
        self.name = name
        self.size = size
        self.hash = hash
        self.mime_type = mime_type
        self.extension = extension

    @property
    def user(self):
        return User.query.filter_by(id=self.user_id).first()

    @property
    def template(self):
        return "attach/_%s.html" % self.mime_type.split("/")[0]

        # __table_args__ = (
        #     db.UniqueConstraint('user_id', 'hash', name='unique_user_attach'),
        # )


class GroupPost(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False, index=True)
    attach_id = db.Column(db.Integer, db.ForeignKey('attach.id'), nullable=True, index=True)

    content = db.Column(db.String(256))
    date_created = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, group_id, attach_id=None, content=None):
        self.user_id = user_id
        self.group_id = group_id
        self.attach_id = attach_id
        self.content = content

    @property
    def user(self):
        return User.query.filter_by(id=self.user_id).first()

    @property
    def attach(self):
        return Attach.query.filter_by(id=self.attach_id).first()

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
        return self


db.create_all()

ani_groups.get_actions(app=app)
ani_auth.get_actions(app=app)


@app.route('/')
@ani_auth.require_login
def index():
    return render_template('index.html', **get_namespace())


if __name__ == '__main__':
    app.run(debug=True)
