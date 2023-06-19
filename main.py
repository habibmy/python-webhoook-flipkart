from flask import Flask, request
from bs4 import BeautifulSoup as bs
import json
import sqlite3


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

def saveToDatabase(deliveredDate, order_ids):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for order_id in order_ids:
        c.execute("INSERT INTO orders VALUES (?, ?)", (order_id, deliveredDate))
    conn.commit()
    conn.close()

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



