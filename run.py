# run.py


from app import create_app
from app.extensions import db

app = create_app()

# Ensure model modules are imported so SQLAlchemy is aware of all models
# (importing blueprints/models will register model classes with SQLAlchemy)
from app.email_service import models as email_models
from app.notification import models as notification_models

with app.app_context():
    # Create any missing tables (for development). In production use Flask-Migrate.
    db.create_all()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
