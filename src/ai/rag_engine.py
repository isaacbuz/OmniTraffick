"""RAG Copilot for brand guidelines and historical campaign analysis."""
import os
from typing import List, Dict, Any
from pathlib import Path

try:
    import openai
    from pinecone import Pinecone
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


class RAGCopilot:
    """
    Retrieval-Augmented Generation Copilot.
    
    Ingests brand guidelines PDFs and historical campaign data into vector DB.
    Provides intelligent recommendations based on semantic search.
    """
    
    def __init__(self, pinecone_api_key: str | None = None, openai_api_key: str | None = None):
        """Initialize RAG copilot."""
        if not DEPS_AVAILABLE:
            raise ImportError("RAG dependencies not installed. Run: pip install openai pinecone-client")
        
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.pinecone_api_key or not self.openai_api_key:
            raise ValueError("PINECONE_API_KEY and OPENAI_API_KEY must be set")
        
        # Initialize clients
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Index name
        self.index_name = "omnitraffick-guidelines"
        
    def ingest_document(self, file_path: Path, metadata: Dict[str, Any]) -> None:
        """
        Ingest a document into the vector database.
        
        Args:
            file_path: Path to PDF or text file
            metadata: Additional metadata (brand, category, etc.)
        """
        # Read file
        with open(file_path, "r") as f:
            content = f.read()
        
        # Split into chunks (simple chunking - can be improved with LangChain)
        chunks = self._chunk_text(content, chunk_size=500)
        
        # Generate embeddings
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk)
            vector_id = f"{file_path.stem}_{i}"
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    **metadata,
                    "chunk": i,
                    "text": chunk,
                    "file": str(file_path),
                }
            })
        
        # Upsert to Pinecone
        index = self.pc.Index(self.index_name)
        index.upsert(vectors=vectors)
        
    def query_recommendations(self, ticket_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query RAG for recommendations based on ticket context.
        
        Args:
            ticket_context: Dict with brand, campaign_name, channel, etc.
            
        Returns:
            List of recommendations with reasoning
        """
        # Build query
        query_text = f"""
        Brand: {ticket_context.get('brand')}
        Campaign: {ticket_context.get('campaign_name')}
        Channel: {ticket_context.get('channel')}
        
        What best practices should be followed?
        """
        
        # Get embedding
        query_embedding = self._get_embedding(query_text)
        
        # Search Pinecone
        index = self.pc.Index(self.index_name)
        results = index.query(
            vector=query_embedding,
            top_k=5,
            include_metadata=True
        )
        
        # Format recommendations
        recommendations = []
        for match in results.matches:
            recommendations.append({
                "score": match.score,
                "text": match.metadata.get("text"),
                "source": match.metadata.get("file"),
                "brand": match.metadata.get("brand"),
            })
        
        return recommendations
    
    def generate_copilot_suggestion(self, ticket_context: Dict[str, Any]) -> str:
        """
        Generate AI copilot suggestion using GPT-4 + RAG context.
        
        Args:
            ticket_context: Ticket details
            
        Returns:
            Natural language suggestion
        """
        # Get RAG context
        recommendations = self.query_recommendations(ticket_context)
        
        # Build context
        context_text = "\n\n".join([
            f"- {rec['text']} (Source: {rec['source']}, Relevance: {rec['score']:.2f})"
            for rec in recommendations
        ])
        
        # Generate with GPT-4
        prompt = f"""
You are an expert AdOps copilot. Based on brand guidelines and historical performance data, provide a recommendation for this campaign:

Campaign Context:
- Brand: {ticket_context.get('brand')}
- Campaign: {ticket_context.get('campaign_name')}
- Channel: {ticket_context.get('channel')}
- Target Market: {ticket_context.get('market')}

Relevant Guidelines:
{context_text}

Provide a concise recommendation (1-2 sentences) focusing on:
1. Channel suitability
2. Any potential issues or optimizations
3. Historical performance insights

Recommendation:
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert AdOps strategist."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3,
        )
        
        return response.choices[0].message.content
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text."""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
