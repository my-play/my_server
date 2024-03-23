from flask import Flask, render_template, request, redirect
import requests
import csv
import os

app = Flask(__name__)


@app.route('/')
def home():
    return "Hello, welcome to the Bitcoin value checker!"


@app.route('/bitcoin_value')
def bitcoin_value():
    # Fetch the current Bitcoin value data
    url = "https://blockchain.info/ticker"
    response = requests.get(url)
    data = response.json()

    # Extract the Bitcoin price in USD
    price_usd = data['USD']['last']  # Assuming you want the last known price

    # Check if Bitcoin price < 60000
    mood = "😞" if price_usd < 60000 else "😊"
    # Display the price and the mood on a webpage
    return f"The current Bitcoin price in USD is: ${price_usd} {mood}"

@app.route('/add_data', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        # Extract data from form
        date = request.form['date']
        time = request.form['time']
        price = request.form['price']

        # Define CSV file path
        csv_file = 'bitcoin_data.csv'

        # Check if file exists to write headers
        file_exists = os.path.isfile(csv_file)

        # Open the CSV file and append the data
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Date', 'Time', 'Price'])  # Write headers if file doesn't exist
            writer.writerow([date, time, price])  # Write data

        return redirect('/')
    else:
        # Render the form template
        return render_template('add_data.html')


if __name__ == '__main__':
    app.run(debug=True)
