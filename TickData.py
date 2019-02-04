import pandas as pd
from datetime import datetime
import numpy as np
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
Base = declarative_base()



class TickData:
    @classmethod
    def initialize(cls):
        cls.price = []
        cls.size = []
        cls.dt = []
        cls.connex = None
        cls.connect_to_db()
        cls.engine = None

    @classmethod
    def read_data_from_db(cls, from_dt, end_dt):
        #sql = 'select * from tick where datetime between datetime('2018-1-1') and datetime('2018-1-10');'
        with sqlite3.connect('tick.db') as con:
            print(con.columns)
            cur = con.cursor()
            return cur.execute('select * from tick where size = 0.05')


    @classmethod
    def read_data_csv(cls):
        i = 0
        for chunk in pd.read_csv("tick.csv", chunksize=10000, header=None):
            dt = chunk.iloc[:, :1].applymap(datetime.fromtimestamp)
            price = chunk.iloc[:, 1:2]
            size = chunk.iloc[:, 2:3]
            con = pd.concat([dt, price, size], axis=1)
            con.columns = ['datetime', 'price', 'size']
            con.to_sql('tick', cls.engine, if_exists="replace", index=False)
            i = i+1
            print('DB insert '+str(i*10000))
        print('db insertion was completed')

    @classmethod
    def connect_to_db(cls):
        engine = create_engine('sqlite:///tick.db', echo=False)
        if not database_exists(engine.url):
            create_database(engine.url)
        #cls.connex = engine.connect()
        cls.engine = engine

    @classmethod
    def create_table(cls):
        #connex = sqlite3.connect("tick.db")  # Opens file if exists, else creates file
        cur = cls.connex.cursor()
        sql = "CREATE TABLE tick (datetime TEXT, price REAL, size REAL)"
        cur.execute(sql)
        cls.connex.commit()
        #cls.connex.close()



class Tick(Base):
    __tablename__ = 'ticks'
    datetime = Column(DateTime)
    price = Column(Float)
    size = Column(Float)

    def __repr__(self):
        return "<tick(datetime='%s', price='%s', size='%s')>" % (self.datetime, self.price, self.size)


if __name__ == '__main__':
    #TickData.initialize()
    #TickData.create_table()
    #TickData.read_data()

    #Base.metadata.create_all(engine)
    #Base.metadata.create_all(engine)
    #TickData.connect_to_db()
    d = TickData.read_data_from_db('2018-1-1', '2018-1-10')
    print(d)
    #TickData.read_data_csv()


