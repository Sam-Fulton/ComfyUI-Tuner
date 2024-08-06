from .home import home_bp

def register_blueprints(app):
    app.register_blueprint(home_bp)