import sqlite3

# create table if not exists delivered_orders

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS delivered_orders
                (order_id text, delivered_date text)''')    
conn.commit()
conn.close()

