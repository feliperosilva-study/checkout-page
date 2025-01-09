from flask import Flask, render_template, url_for, redirect, flash
from models import db, Scores
import json
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/products.db'
app.secret_key = 'my_checkout_page'

db.init_app(app)

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            existing_score = Scores.query.filter_by(title=item['title']).first()
            if not existing_score:
                score = Scores(**item)
                db.session.add(score)
        db.session.commit()

def initialize_data():
    with app.app_context():
        load_json_data("data/seed_data.json")

initialize_data()

@app.route('/')
def home():
    scores = Scores.query.all()

    return render_template('index.html', scores=scores)

@app.route('/checkout/<int:id>')
def checkout(id):

    score = Scores.query.get(id)

    return render_template('checkout.html', score=score)


if __name__ == '__main__':
    app.run(debug=True)