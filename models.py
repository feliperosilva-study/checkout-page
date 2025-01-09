from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Scores(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)

    image = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    composer = db.Column(db.String(100), nullable=False)
    edition = db.Column(db.String(100), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Float, nullable=False)