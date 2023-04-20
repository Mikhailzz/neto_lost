import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


Base = declarative_base()


class Seeker(Base):
    """
    таблица ищущих
    """
    __tablename__ = 'seeker'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), unique=False)
    last_name = sq.Column(sq.String(length=40), unique=False)


class Lover(Base):
    """
    таблица найденных и выведенных на экран
    """
    __tablename__ = 'lover'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), unique=False)
    last_name = sq.Column(sq.String(length=40), unique=False)
    id_seeker = sq.Column(sq.Integer, sq.ForeignKey("seeker.id"), nullable=False, primary_key=True)

    seeker = relationship(Seeker, backref="Seekers")



def create_tables(engine):
    """
    создание таблицы

    """
    Base.metadata.create_all(engine)

# подключение к базе данных

def create_base_data():



    DSN = 'postgresql://postgres:th2AfrM1n7Dp3@localhost:5432/itog'

    engine = sq.create_engine(DSN)
    create_tables(engine)

    Session = sessionmaker(bind=engine)



    session = Session()
    return session