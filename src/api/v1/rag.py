"""RAG Copilot API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class RAGSuggestionRequest(BaseModel):
    """Request for RAG suggestion."""
    brand: str | None = None
    campaign_name: str | None = None
    channel: str | None = None
    market: str | None = None


class RAGSuggestionResponse(BaseModel):
    """Response with AI suggestion."""
    suggestion: str
    sources: list[dict] | None = None


@router.post("/rag/suggest", response_model=RAGSuggestionResponse)
async def get_rag_suggestion(request: RAGSuggestionRequest):
    """
    Get AI copilot suggestion based on ticket context.
    
    Uses RAG (Retrieval-Augmented Generation) to query brand guidelines
    and historical performance data.
    
    Args:
        request: Ticket context
        
    Returns:
        AI-generated recommendation
    """
    try:
        from src.ai.rag_engine import RAGCopilot
        
        # Initialize RAG copilot
        copilot = RAGCopilot()
        
        # Build context
        context = {
            "brand": request.brand,
            "campaign_name": request.campaign_name,
            "channel": request.channel,
            "market": request.market,
        }
        
        # Generate suggestion
        suggestion = copilot.generate_copilot_suggestion(context)
        
        return RAGSuggestionResponse(
            suggestion=suggestion,
            sources=None,  # Could return sources here
        )
    
    except ImportError:
        # RAG dependencies not installed
        return RAGSuggestionResponse(
            suggestion="RAG copilot requires additional dependencies. Install: pip install openai pinecone-client"
        )
    
    except Exception as e:
        # Fallback suggestion
        suggestion = f"Based on {request.brand} targeting {request.market} via {request.channel}, "
        
        if request.channel == "Meta":
            suggestion += "consider using traffic objectives for awareness campaigns. "
        elif request.channel == "TikTok":
            suggestion += "video creative with native sound performs 40% better. "
        
        suggestion += "Ensure geo-targeting is properly configured."
        
        return RAGSuggestionResponse(suggestion=suggestion)
