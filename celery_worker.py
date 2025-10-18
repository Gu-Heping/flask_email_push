from app import create_app, celery, make_celery
from app.extensions import db
from app.config import Config

app = create_app()
celery = make_celery(app)





