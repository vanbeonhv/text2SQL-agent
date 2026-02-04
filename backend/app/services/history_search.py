"""Similar question search for few-shot learning."""
from typing import List, Dict, Any, Optional
import Levenshtein
from ..database.history import history_manager


class HistorySearchService:
    """Service for finding similar past queries."""
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity score between two questions.
        
        Uses Levenshtein distance normalized to 0-1 range.
        
        Args:
            query1: First question
            query2: Second question
            
        Returns:
            Similarity score (0.0 to 1.0, higher is more similar)
        """
        # Normalize strings
        q1 = query1.lower().strip()
        q2 = query2.lower().strip()
        
        # Calculate Levenshtein distance
        distance = Levenshtein.distance(q1, q2)
        max_len = max(len(q1), len(q2))
        
        if max_len == 0:
            return 1.0
        
        # Convert to similarity score (0-1)
        similarity = 1.0 - (distance / max_len)
        return similarity
    
    async def find_similar_queries(
        self,
        question: str,
        top_k: int = 5,
        min_similarity: float = 0.3,
        exclude_conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find similar questions from query history.
        
        Args:
            question: Current user question
            top_k: Number of similar examples to return
            min_similarity: Minimum similarity threshold
            exclude_conversation_id: Exclude queries from this conversation
            
        Returns:
            List of similar query examples with similarity scores
        """
        # Get successful queries from history
        past_queries = await history_manager.get_successful_queries(
            limit=100,
            exclude_conversation_id=exclude_conversation_id
        )
        
        if not past_queries:
            return []
        
        # Calculate similarity scores
        scored_queries = []
        for query in past_queries:
            similarity = self._calculate_similarity(question, query["question"])
            
            if similarity >= min_similarity:
                scored_queries.append({
                    "question": query["question"],
                    "sql": query["sql"],
                    "intent": query["intent"],
                    "similarity_score": similarity
                })
        
        # Sort by similarity score (descending)
        scored_queries.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Return top-k results
        return scored_queries[:top_k]


# Global history search service instance
history_search_service = HistorySearchService()
