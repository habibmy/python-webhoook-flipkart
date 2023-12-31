from flask import Flask, request
from bs4 import BeautifulSoup as bs
import json
import sqlite3

# check if database exists, if not, create it
conn = sqlite3.connect('/data/database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS delivered_orders
                (order_id text, delivered_date text)''')
conn.commit()
conn.close()

def saveToDatabase(deliveredDate, order_ids):
    conn = sqlite3.connect('/data/database.db')
    c = conn.cursor()
    for order_id in order_ids:
        c.execute("INSERT INTO delivered_orders VALUES (?, ?)", (order_id, deliveredDate))
    conn.commit()
    conn.close()


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/delivered_orders', methods=['GET'])
def getDeliveredOrders():
    conn = sqlite3.connect('/data/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM delivered_orders")
    rows = c.fetchall()
    conn.close()
    return json.dumps(rows)

# search by order id return no result found if not found
@app.route('/delivered_orders/<order_id>', methods=['GET'])
def getDeliveredOrder(order_id):
    conn = sqlite3.connect('/data/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM delivered_orders WHERE order_id = ?", (order_id,))
    rows = c.fetchall()
    conn.close()
    # if no result found, return 404
    if len(rows) == 0:
        return 'no result found', 404
    return json.dumps(rows)

@app.route('/webhook', methods=['POST'])
def webhook():
    # get the data from body
    data = request.form['html']
    # parse the data
    soup = bs(data, 'html.parser')
    tr = soup.find_all('tr')
    # if 2 or more rows, then it's a valid order
    order_ids = []
    if len(tr) >= 2:
        # get the order id
        for i in range(1, len(tr)):
            order_ids.append(tr[i].find_all('td')[0].text)
    try:
        deliveredDate = request.form['reply_plain'].split(',')[1].split('a')[0].strip()
    except:
        # if no delivered date, then use today's date
        from datetime import date
        todaysDate = date.today().strftime("%d/%m/%Y")
        deliveredDate = todaysDate

    # return the order id
    if len(order_ids) > 0:
        print('deliveredDate: ' + deliveredDate)
        print('order ids: ' + ', '.join(order_ids))
        # save data to database sqlite3

        saveToDatabase(deliveredDate, order_ids)

        # return json.dumps({'success': ', '.join(order_ids)})
        return json.dumps({'success': ', '.join(order_ids), 'deliveredDate': deliveredDate})
    else:
        # return status code 400 if no order id found
        return 'fail', 400

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)



