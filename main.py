from flask import Flask, render_template, url_for, redirect, flash, request
from models import db, Scores, Purchase
import json

import stripe
from dotenv import load_dotenv
import os

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/products.db'
app.secret_key = 'my_checkout_page'

db.init_app(app)

# Helper function: loads the JSON file and add data to the database, if not existing
def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            existing_score = Scores.query.filter((Scores.title == item['title']) & (Scores.composer == item['composer'])).first()
            if not existing_score:
                score = Scores(**item) # unpacking the dictionary and transforming it in a Score instance
                db.session.add(score)
        db.session.commit()

# Main Function: Prepares app and initialize database
def initialize_data():
    with app.app_context():
        db.create_all()
        load_json_data("data/seed_data.json")

# Starts the process
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

@app.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    address = request.form.get('address')
    postcode = request.form.get('postcode')
    quantity = int(request.form.get('quantity'))
    product_id = request.form.get('product_id')

    score = Scores.query.get(product_id)

    image_url = url_for('static', filename=score.image, _external=True)

    score_name = score.title
    total_price = int(score.price * 100) #price in cents

    
    # Create Stripe's checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'images': [image_url], #The images should be in an array/list, need to use []
                            'name': score_name,
                        },
                        'unit_amount': total_price,
                    },
                    'quantity': quantity,
                },
            ],
            mode='payment',
            success_url='http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}', #session_id required for sending successful purchases to database
            cancel_url='http://localhost:5000/cancel',
            metadata={
                'fullname': fullname,
                'email': email,
                'address': address,
                'postcode': postcode,
                'product_id': product_id,
                'quantity': quantity,
            }
        )

    except Exception as e:
        return str(e), 400

    # Redirects the user to the Stripe checkout page using a GET request (HTTP 303) after form submission.
    # The 303 status ensures that the user is redirected without resubmitting the form data.
    return redirect(checkout_session.url, code=303)

@app.route('/success', methods=['GET'])
def success():
    session_id = request.args.get('session_id')  # Get the session_id from the URL
    if not session_id:
        return "Session ID is missing", 400

    try:
        # Retrieve the checkout session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        # Check the payment status
        if checkout_session.payment_status == 'paid':
            # Extract metadata to process further
            fullname = checkout_session.metadata['fullname']
            email = checkout_session.metadata['email']
            address = checkout_session.metadata['address']
            postcode = checkout_session.metadata['postcode']
            product_id = checkout_session.metadata['product_id']
            quantity = checkout_session.metadata['quantity']

            new_purchase = Purchase(
                fullname=fullname,
                email=email,
                address=address,
                postcode=postcode,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(new_purchase)
            db.session.commit()

            return render_template('success.html', buyer=fullname)
        else:
            return "Payment not completed or failed", 400
    except Exception as e:
        return f"An error occurred: {str(e)}", 500 # HTTP 500 Internal Server Error

@app.route('/cancel')
def cancel():    
    return render_template('cancel.html')


if __name__ == '__main__':
    app.run(debug=True)