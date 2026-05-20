from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker
import time

engine = create_engine('sqlite:///../data/crowdsense.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
Base = declarative_base()

class AnalyticsRecord(Base):
    __tablename__ = 'analytics'
    id             = Column(Integer, primary_key=True)
    timestamp      = Column(Float,  default=time.time)
    total_people   = Column(Integer)
    total_vehicles = Column(Integer)
    density_level  = Column(String)
    density_score  = Column(Integer)

Base.metadata.create_all(engine)

def save_record(metrics: dict):
    with Session() as s:
        s.add(AnalyticsRecord(**{k: metrics[k] for k in
            ['total_people','total_vehicles','density_level','density_score']}))
        s.commit()

def get_recent(limit=200):
    with Session() as s:
        rows = s.query(AnalyticsRecord).order_by(
            AnalyticsRecord.timestamp.desc()).limit(limit).all()
        return [{'timestamp': r.timestamp, 'total_people': r.total_people,
                 'density_level': r.density_level} for r in rows]
