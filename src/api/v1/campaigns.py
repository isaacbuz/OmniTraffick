"""Campaign API endpoints with Taxonomy Engine integration."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.api.deps import get_db
from src.models.campaign import Campaign
from src.models.brand import Brand
from src.models.market import Market
from src.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from src.services.taxonomy_engine import TaxonomyEngine

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignResponse, status_code=201)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """
    Create a new campaign with auto-generated taxonomy name.
    
    The campaign name is generated using the Taxonomy Engine:
    [BrandCode]_[MarketCode]_[ChannelPlatform]_[Year]_[CampaignName]
    """
    # Validate brand exists
    brand = db.query(Brand).filter(Brand.id == campaign.brand_id).first()
    if not brand:
        raise HTTPException(status_code=422, detail="Invalid brand_id: brand does not exist")

    # Validate market exists
    market = db.query(Market).filter(Market.id == campaign.market_id).first()
    if not market:
        raise HTTPException(status_code=422, detail="Invalid market_id: market does not exist")

    # Generate campaign name using Taxonomy Engine
    # For Phase 1, we'll use a placeholder channel (will be derived from tickets in Phase 2)
    try:
        taxonomy_name = TaxonomyEngine.generate_campaign_name(
            brand_code=brand.internal_code,
            market_code=market.code,
            channel_platform="MULTI",  # Placeholder for multi-channel campaigns
            campaign_name=campaign.campaign_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check if campaign name already exists
    existing = db.query(Campaign).filter(Campaign.name == taxonomy_name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Campaign with name '{taxonomy_name}' already exists"
        )

    # Create campaign
    db_campaign = Campaign(
        name=taxonomy_name,
        brand_id=campaign.brand_id,
        market_id=campaign.market_id,
        budget=campaign.budget,
        status=campaign.status,
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


@router.get("/", response_model=list[CampaignResponse])
def list_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all campaigns."""
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: UUID, db: Session = Depends(get_db)):
    """Get a campaign by ID."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(campaign_id: UUID, campaign_update: CampaignUpdate, db: Session = Depends(get_db)):
    """Update a campaign (budget and status only)."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = campaign_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(campaign, key, value)

    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=204)
def delete_campaign(campaign_id: UUID, db: Session = Depends(get_db)):
    """Delete a campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(campaign)
    db.commit()
    return None
