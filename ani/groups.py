import os
from flask import render_template, request, redirect, url_for
# -*- coding: utf-8 -*-
from werkzeug.utils import secure_filename
from ani import storage
from ani.auth import current_user, require_login
from ani.utils import get_namespace
# ALLOWED_EXTENSIONS
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_actions(app):
    from anishare import Attach, Group, GroupPost, db

    @app.route("/group", methods=['GET'])
    @require_login
    def group_index():
        return render_template('group/index.html', **get_namespace())

    @app.route("/group/create", methods=['GET', 'POST'])
    @require_login
    def group_create():
        if request.method == "POST":
            user = current_user()
            parent_id = request.form.get('parent_id', None)
            name = request.form.get('name')
            group = Group(name=name, creator_id=user.id, parent_id=parent_id)
            db.session.add(group)
            db.session.commit()
            group.join_user(user, role=1)
            return redirect(url_for('group_im', group_id=group.id))
        return render_template("group/create.html", **get_namespace())

    @app.route("/group/join", methods=['POST'])
    @require_login
    def group_join():
        group_id = request.form.get("group_id", None)
        group = Group.query.filter_by(id=group_id).first()
        group.join_user(current_user())
        return redirect(url_for('group_im', group_id=group_id))

    @app.route("/group/<int:group_id>")
    @require_login
    def group_im(group_id):
        return render_template('group/im.html', **get_namespace(group=Group.query.filter_by(id=group_id).first()))

    @app.route("/group/post", methods=['POST'])
    @require_login
    def group_post():
        user = current_user()
        group = Group.query.filter_by(id=request.form.get('group_id')).first()
        attach_upload = request.files.get('attach')
        attach_id = None
        if attach_upload:
            attach = storage.save(attach_upload, app)
            attach.group_id = group.id
            db.session.commit()
            attach_id = attach.id

        post = GroupPost(user_id=user.id, group_id=group.id, attach_id=attach_id, content=request.form.get('content'))
        post.save()
        return redirect(url_for('group_im', group_id=group.id))

    @app.route("/attach/download/<int:attach_id>", methods=['GET'])
    @require_login
    def attach_download(attach_id):
        attach = Attach.query.filter_by(id=attach_id).first()
        attach.download_count = (attach.download_count or 0) + 1
        db.session.commit()
        return redirect(attach.url)
