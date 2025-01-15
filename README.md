# Bookstore and Checkout Page Project

## Bacis Sctructure
* Python 3.11.5
* Flask 3.1.0
* Werkzeug 3.1.3

## API for handling payment
* Stripe 11.4.1

## Features
* Homepage will list all products included in a database with all related information (catalog stored in a json file)
* Catalog can be filtered by composer's last name
* Checkout page will display score choosen and user personal information form
* When procced to checkout, personal info will be kept in a metadata and user will be redirected to Stripe payment page
* If payment is successful, user's personal info will be stored in database for creating a costumer log

## Testing payments with Stripe
When redirected to Stripe payment page, there are three credit card numbers for testing purposes:
* 4242424242424242 (Payment succeeds)
* 4000002500003155 (Payment requires authentication)
* 4000000000009995 (Payment is declined)