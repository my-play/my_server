import sqlite3

from flask import Flask, render_template, redirect, Response, jsonify
from flask_restx import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import requests
import psycopg2
import csv
import os
# from flask_sslify import SSLify
app = Flask(__name__, template_folder='templates')
api = Api(app, version='1.0', title='My Server Doc Swagger', description='My Playground :)')
# sslify = SSLify(app)

SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Bitcoin Value Checker"
    }
)

app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)
add_data_parser = api.parser()
add_data_parser.add_argument('date', type=str, required=True, help='The date of the data')
add_data_parser.add_argument('time', type=str, required=True, help='The time of the data')
add_data_parser.add_argument('price', type=float, required=True, help='The price of Bitcoin')


@app.route('/')
def home():
    return Response(render_template('index.html', mimetype='text/html'))


@api.route('/bitcoin_value')
class BitcoinValue(Resource):
    def get(self):
        url = "https://blockchain.info/ticker"
        response = requests.get(url)
        data = response.json()
        price_usd = data['USD']['last']
        return "Price now: "+str(price_usd)


class AddData(Resource):

    def get(self):
        return Response(render_template('add_data.html', mimetype='text/html'))

    @api.expect(add_data_parser)
    def post(self):
        args = add_data_parser.parse_args()
        date = args['date']
        time = args['time']
        price = args['price']
        csv_file = 'bitcoin_data.csv'
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Date', 'Time', 'Price'])
            writer.writerow([date, time, price])
        self.save_to_database(date, time, price)
        return redirect('/')

    def save_to_database(self, date, time, price):
        db_url = os.environ[
            'DATABASE_URL']

        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS bitcoin_data (
                            id SERIAL PRIMARY KEY,
                            date TEXT,
                            time TEXT,
                            price REAL
                          )''')

        cursor.execute('INSERT INTO bitcoin_data (date, time, price) VALUES (%s, %s, %s)', (date, time, price))
        conn.commit()
        cursor.close()
        conn.close()


api.add_resource(AddData, '/add_data')


@app.route('/get_data', methods=['GET'])
def get_data():
    # Database connection parameters
    db_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute('SELECT id, date, time, price FROM bitcoin_data')
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    data = []
    for row in records:
        data.append({
            'id': row[0],
            'date': row[1],
            'time': row[2],
            'price': row[3]
        })

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
