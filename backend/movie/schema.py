from pydantic import BaseModel
from typing import List, Optional

class MovieRatingRequest(BaseModel):
    """
    Request schema for movie rating search
    """
    movie_name: str

class MovieRatingPlatform(BaseModel):
    """
    Schema for movie rating from a specific platform
    """
    platform: str
    movie_title: str
    movie_rating: float
    type_of_movie: str
    positive_review_percentage: int
    negative_review_percentage: int

class MovieRatingResponse(BaseModel):
    """
    Response schema for movie rating search
    """
    status: str
    message: Optional[str] = None
    data: List[MovieRatingPlatform]
