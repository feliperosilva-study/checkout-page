from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from models import Scores

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///.../database/products.db'
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    scores = Scores.query.all()

    return render_template('index.html', scores=scores)

@app.route('/checkout/<int:id>')
def checkout(id):

    id = Scores.query.get(id)

    return render_template('checkout.html')


if __name__ == '__main__':
    app.run(debug=True)