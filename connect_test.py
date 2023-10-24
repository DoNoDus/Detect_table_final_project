import pandas as pd 
from sqlalchemy import create_engine

host = 'localhost'
username = 'postgres'
password = 'password'
port = 5432
db_name = 'test_db'
engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db_name}')
df = pd.read_csv('iris.csv')
df.to_sql("test_iris", con=engine)