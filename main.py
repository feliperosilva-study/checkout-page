from flask import Flask, render_template, url_for, redirect, flash, request
from models import db, Scores
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/products.db'
app.secret_key = 'my_checkout_page'

db.init_app(app)

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            existing_score = Scores.query.filter((Scores.title == item['title']) & (Scores.composer == item['composer'])).first()
            if not existing_score:
                score = Scores(**item)
                db.session.add(score)
        db.session.commit()

def initialize_data():
    with app.app_context():
        load_json_data("data/seed_data.json")

initialize_data()

@app.route('/', methods=['GET', 'POST'])
def home():
    scores = Scores.query.all()

    unique_composer = sorted({score.composer.split()[-1] for score in scores})

    if request.method == 'POST':
        composer = request.form.get('composer')
        last_name = composer.split()[-1]

        if last_name and last_name != 'Filter by Composer' and last_name in unique_composer:
            scores = Scores.query.filter(Scores.composer.like(f'% {last_name}')).all()

        return render_template('index.html', scores=scores, unique_composer=unique_composer)

    return render_template('index.html', scores=scores, unique_composer=unique_composer)

@app.route('/checkout/<int:id>')
def checkout(id):

    score = Scores.query.get(id)

    return render_template('checkout.html', score=score)


if __name__ == '__main__':
    app.run(debug=True)