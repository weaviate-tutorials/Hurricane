def format_weaviate_and_you_contexts(weaviateRM_output, youRM_output):
    weaviateRM_output = "".join(weaviateRM_output)
    youRM_output = [d['long_text'] for d in youRM_output]
    youRM_output = "".join(youRM_output)
    return weaviateRM_output, youRM_output

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

def format_blog_draft(blog_post: BlogPost) -> str:
    blog_draft = ""
    for evidence_paragraph in blog_post.evidence_paragraphs:
        blog_draft += evidence_paragraph
        blog_draft += "\n"
    return blog_draft
    

def format_blog_post(blog_post: BlogPost) -> str:
    formatted_blog = f"{blog_post.title}\n\n"
    formatted_blog += f"{blog_post.introduction_paragraph}\n\n"
    
    formatted_blog += "Outline:\n"
    for i, point in enumerate(blog_post.outline, start=1):
        formatted_blog += f"{i}. {point}\n"
    formatted_blog += "\n"
    
    formatted_blog += "Evidence Paragraphs:\n"
    for paragraph in blog_post.evidence_paragraphs:
        formatted_blog += f"{paragraph}\n\n"
    
    formatted_blog += f"Bold Prediction: {blog_post.bold_prediction}\n\n"
    formatted_blog += f"Weaviate Relevance: {blog_post.weaviate_relevance}\n\n"
    
    formatted_blog += "Takeaways:\n"
    for i, takeaway in enumerate(blog_post.takeaways, start=1):
        formatted_blog += f"{i}. {takeaway}\n"
    
    return formatted_blog