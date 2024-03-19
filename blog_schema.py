from typing import List, Optional
from pydantic import BaseModel

class BlogPost(BaseModel):
    question: Optional[str] = None
    title: Optional[str] = None
    introduction_paragraph: Optional[str] = None
    outline: Optional[str] = None
    evidence_paragraphs: Optional[List[str]] = []
    bold_prediction: Optional[str] = None
    weaviate_relevance: Optional[str] = None
    takeaways: Optional[List[str]] = []