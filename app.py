from flask import Flask
from extensions import db, migrate
from routes import main
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(main)
    
    with app.app_context():
        wipe_database()
    
    return app

def wipe_database():
    db.drop_all()
    db.create_all()
    seed_data()  # Optional: Add any initial seed data if necessary

def seed_data():
    # Add any seed data you want to initialize in the database
    pass

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
