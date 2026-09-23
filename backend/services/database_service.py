import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///marketing_campaign.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

Base = declarative_base()


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    product_name = Column(String(200), nullable=False)
    target_audience = Column(String(300))
    platform = Column(String(100))
    goal = Column(String(100), default="Brand Awareness")
    campaign_content = Column(Text)  # JSON string
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def save_campaign(product_name, target_audience, platform, goal, campaign_content, image_url=None):
    session = SessionLocal()
    try:
        # Convert dictionary to JSON string if needed
        if isinstance(campaign_content, (dict, list)):
            content_str = json.dumps(campaign_content)
        else:
            content_str = str(campaign_content)

        campaign = Campaign(
            product_name=product_name,
            target_audience=target_audience,
            platform=platform,
            goal=goal,
            campaign_content=content_str,
            image_url=image_url
        )

        session.add(campaign)
        session.commit()
        session.refresh(campaign)

        return campaign.id

    finally:
        session.close()


def get_campaigns():
    session = SessionLocal()
    try:
        campaigns = session.query(Campaign).order_by(Campaign.created_at.desc()).all()
        results = []
        for c in campaigns:
            try:
                parsed_content = json.loads(c.campaign_content)
            except Exception:
                parsed_content = c.campaign_content

            results.append({
                "id": c.id,
                "product_name": c.product_name,
                "target_audience": c.target_audience,
                "platform": c.platform,
                "goal": c.goal or "Brand Awareness",
                "campaign_content": parsed_content,
                "image_url": c.image_url,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else None
            })
        return results
    finally:
        session.close()


def get_campaign_by_id(campaign_id):
    session = SessionLocal()
    try:
        campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return None

        try:
            parsed_content = json.loads(campaign.campaign_content)
        except Exception:
            parsed_content = campaign.campaign_content

        return {
            "id": campaign.id,
            "product_name": campaign.product_name,
            "target_audience": campaign.target_audience,
            "platform": campaign.platform,
            "goal": campaign.goal or "Brand Awareness",
            "campaign_content": parsed_content,
            "image_url": campaign.image_url,
            "created_at": campaign.created_at.strftime("%Y-%m-%d %H:%M") if campaign.created_at else None
        }
    finally:
        session.close()


def delete_campaign(campaign_id):
    session = SessionLocal()
    try:
        campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return False

        session.delete(campaign)
        session.commit()
        return True
    finally:
        session.close()


def get_database_stats():
    session = SessionLocal()
    try:
        total = session.query(Campaign).count()
        return {
            "total_campaigns": total
        }
    finally:
        session.close()