# -*- coding: utf-8 -*-
import datetime
import os
from qiniu import Auth, put_file
import base64

bucket_name = 'freshway'
qiniu_inst = Auth("cSlEbes-zd-cr0xbIgzXrnKA7l5FoQL3IPWxPgM6", "3rjQYp-5Qbc8nL-cP9o3qfRUCrWH9WX18em4iih0")


def qiniu_url(key):
    return "http://%s/%s" % ("7xiq4g.com1.z0.glb.clouddn.com", key)


def save(file_upload, app):
    from .auth import current_user
    from anishare import Attach, db

    relative_dir = "%s/%s" % (datetime.datetime.now().strftime("%Y/%m/%d"),
                              base64.b64encode(os.urandom(24)).decode(encoding='UTF-8'))
    filename = file_upload.filename
    tmp_dir = os.path.join(app.config['UPLOAD_FOLDER'], relative_dir)
    tmp_path = os.path.join(tmp_dir, filename)
    os.makedirs(tmp_dir)
    file_upload.save(tmp_path)

    key = "upload/%s/%s" % (relative_dir, filename)
    token = qiniu_inst.upload_token(bucket_name, key=key)
    ret, info = put_file(token, key, tmp_path, mime_type=file_upload.mimetype)
    attach = Attach(user_id=current_user().id, url=qiniu_url(key), name=filename, size=os.path.getsize(tmp_path),
                    hash=ret['hash'], mime_type=file_upload.mimetype, extension=filename.rsplit('.').pop())
    db.session.add(attach)
    db.session.commit()
    return attach
