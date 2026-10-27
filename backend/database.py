from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'environment.db')

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class SensorReading(Base):
    __tablename__ = 'sensor_readings'
    id = Column(Integer, primary_key=True)
    temp = Column(Float)
    hum = Column(Float)
    aqi = Column(Float)
    prediction = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    explanation = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)


def save_reading(temp, hum, aqi, prediction=None, confidence=None, explanation=None):
    session = Session()
    reading = SensorReading(
        temp=temp, hum=hum, aqi=aqi,
        prediction=prediction, confidence=confidence,
        explanation=explanation
    )
    session.add(reading)
    session.commit()
    session.close()


def get_latest(n=1):
    session = Session()
    rows = (session.query(SensorReading)
            .order_by(SensorReading.timestamp.desc())
            .limit(n).all())
    session.close()
    return rows


def get_history(n=50):
    session = Session()
    rows = (session.query(SensorReading)
            .order_by(SensorReading.timestamp.desc())
            .limit(n).all())
    session.close()
    return list(reversed(rows))


def get_readings_since(since):
    session = Session()
    rows = (session.query(SensorReading)
        .filter(SensorReading.timestamp >= since)
        .order_by(SensorReading.timestamp.asc()).all())
    session.close()
    return rows