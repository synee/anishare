# -*- coding: utf-8 -*-

def get_actions(app):
    from anishare import User, db
    from ani.utils import get_namespace

    @app.route("/about")
    def about():
        pass

    @app.route("/contact")
    def contact():
        pass

    @app.route("/term")
    def term():
        pass

    @app.route("/feedback")
    def feedback():
        pass
