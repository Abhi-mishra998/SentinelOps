from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from . import Base

class Incident(Base):
    __tablename__ = "incidents"

    id              = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp       = Column(DateTime, default=datetime.utcnow, index=True)
    cluster_id      = Column(String, nullable=False, index=True)
    namespace       = Column(String, nullable=False)
    pod_name        = Column(String, nullable=False)
    incident_type   = Column(String, nullable=False, index=True)
    root_cause      = Column(String)
    confidence      = Column(String)   # high / medium / low
    status          = Column(String, default="open", index=True)
    resolution_time = Column(Integer)  # seconds — MTTR metric
    ai_used         = Column(Boolean, default=False)
    recommended_action = Column(String)
    
    actions = relationship("RemediationAction", back_populates="incident", cascade="all, delete-orphan")
