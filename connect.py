import psycopg2
# import pandas as pd

def begin_connect():
# Connect to the database
    conn = psycopg2.connect(
        host="localhost",
        database="freight_indices_db",
        user="postgres",
        password="password"
    )
    cur = conn.cursor()
    return conn, cur

def end(conn, cur): 
    # Close the cursor and connection
    cur.close()
    conn.close()

def create(table_name):
    conn, cur = begin_connect()
    # freight_indices
    table_name = table_name
    col = 'date DATE, rvs VARCHAR(100), current_week VARCHAR(50), cpr VARCHAR(50), remarks VARCHAR(255)'
    query = f'CREATE TABLE {table_name} ({col});'
    cur.execute(query)
    conn.commit()
    end(conn, cur)

def insert(data): 
    conn, cur = begin_connect()
    for i in range((len(data))):
        date = '2023-03-31'
        query = f"INSERT INTO freight_indices (date, rvs, current_week, cpr, remarks) VALUES('{date}', '{data[i][0]}', '{data[i][1]}', '{data[i][2]}', '{data[i][3]}')"
        cur.execute(query)
        # Commit the changes to the database
        conn.commit()
    end(conn, cur)
    
def get():
    conn, cur = begin_connect()
    query = "SELECT * FROM freight_indices"
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.commit()
    end(conn, cur)
        

