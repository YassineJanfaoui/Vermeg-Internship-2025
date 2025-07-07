import os
import logging
from flask import Flask
from extensions import db, login_manager
from services import cancer_service, chatbot_service
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlalchemy
from sqlalchemy import exc

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "mysql+mysqlconnector://root:@localhost:3306/internship_vermeg"
)
app.config['MODEL_DIR'] = os.path.join(app.root_path, 'models')
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
}

def verify_db_connection():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db.session.execute(sqlalchemy.text("SELECT 1"))
            db.session.commit()
            app.logger.info("✅ Database connection verified successfully")
            return True
        except exc.SQLAlchemyError as e:
            app.logger.error(f"❌ Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return False
            time.sleep(1)
            
# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
cancer_service.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

   

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    if not verify_db_connection():
        app.logger.error("Failed to connect to database after multiple attempts")
    import models
    db.create_all()

import routes