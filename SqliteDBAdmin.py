import pandas as pd
import datetime
import os
import numpy as np
import sqlite3
from sqlalchemy import create_engine, schema, Table, and_
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, DATETIME
Base = declarative_base()


class Ticks(Base):
    __tablename__ = 'ticks'
    id = Column('id', Integer, primary_key=True, autoincrement=False)
    datetime = Column('datetime', DATETIME)
    price = Column('price', Float)
    size = Column('size', Float)

    def __repr__(self):
        return 'Ticks(%s, %s, %s, %s)' % (self.id, self.datetime, self.price, self.size)


class SqliteDBAdmin:
    @classmethod
    def initialize(cls):
        cls.engine = create_engine('sqlite:///tick.db', echo=False)

    @classmethod
    def renew_db(cls):
        os.remove('tick.db')
        cls.initialize()

    @classmethod
    def create_table(cls):
        Base.metadata.create_all(bind=cls.engine, checkfirst=True)

    @classmethod
    def read_from_csv(cls):
        cls.renew_db()
        metadata = schema.MetaData(bind=cls.engine, reflect=True)
        table = Table('ticks', metadata, autoload=True)
        Session = sessionmaker(bind=cls.engine)
        session = Session()
        i=0
        with cls.engine.connect() as conn:
            for chunk in pd.read_csv("tick.csv", chunksize=100000, header=None):
                dt = chunk.iloc[:, :1].applymap(datetime.datetime.fromtimestamp)
                price = chunk.iloc[:, 1:2]
                size = chunk.iloc[:, 2:3]
                df = pd.concat([dt, price, size], axis=1)
                df.columns = ['datetime', 'price', 'size']
                dict = df.to_dict(orient='records')
                conn.execute(table.insert(), dict)
                session.commit()
                i+=1
                print('inserted '+str(i*100000))
        session.close()

    @classmethod
    def read_from_sqlite(cls, year_s, month_s, day_s, year_e, month_e, day_e):
        Session = sessionmaker(bind=cls.engine)
        session = Session()
        with cls.engine.connect() as conn:
            res = session.query(Ticks).filter(and_(Ticks.datetime <= datetime.date(year_e, month_e, day_e),
                                                   Ticks.datetime >= datetime.date(year_s, month_s, day_s))).all()
            session.close()
            return res


if __name__ == '__main__':
    SqliteDBAdmin.initialize()
    #SqliteDBAdmin.create_table()
    #SqliteDBAdmin.read_from_csv()
    res = SqliteDBAdmin.read_from_sqlite(2019,1,1,2019,1,10)
    print(res)
