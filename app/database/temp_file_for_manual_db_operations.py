from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URI

Base = declarative_base()


class TestTable(Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)


# Replace '/absolute/path/to/' with the actual path to the directory where you want the database file.
# DATABASE_PATH = '/Users/vitaliy_lobanov/Documents/_develop/u-social-network/dd_test_u_bot_simple/test.db'
# DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine)

# Add a test entry
session = SessionLocal()
test_entry = TestTable(name='Test Name')
session.add(test_entry)
session.commit()
session.close()

print('Table created and entry added.')
