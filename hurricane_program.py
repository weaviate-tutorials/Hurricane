import dspy
from hurricane_signatures import Question2BlogOutline, Topic2Paragraph, BoldPrediction, WeaviateRelevance, TitleAndTakeaways
from utils import format_weaviate_and_you_contexts
from utils import format_blog_draft, format_blog_post, BlogPost

class Hurricane(dspy.Module):
    def __init__(self, you_rm):
        # 5 LLM Layers (Question2BlogOutline, Topic2Paragraph, BoldPrediction, WeaviateRelevance, TitleAndTakeaways)
        # 2 Retrieval Engines (Weaviate and You)
        
        self.question_to_blog_outline = dspy.ChainOfThought(Question2BlogOutline)
        self.topic_to_paragraph = dspy.ChainOfThought(Topic2Paragraph)
        self.bold_prediction = dspy.ChainOfThought(BoldPrediction)
        self.weaviate_relevance = dspy.ChainOfThought(WeaviateRelevance)
        self.title_and_key_takeaways = dspy.ChainOfThought(TitleAndTakeaways)
        self.you_rm = you_rm

    def forward(self, question):
        blog_container = BlogPost()
        blog_contexts = dspy.Retrieve(k=5)(question).passages
        web_contexts = self.you_rm(question)
        blog_contexts, web_contexts = format_weaviate_and_you_contexts(blog_contexts, web_contexts)
        question_to_blog_outline_outputs = self.question_to_blog_outline(question=question, blog_context=blog_contexts, web_context=web_contexts)
        blog_container.outline = question_to_blog_outline_outputs.blog_outline
        parsed_blog_outline = blog_container.outline.split(",")
        blog_container.introduction_paragraph = question_to_blog_outline_outputs.introduction_paragraph
        for topic in parsed_blog_outline:
            blog_contexts = dspy.Retrieve(k=5)(topic).passages
            web_contexts = self.you_rm(topic)
            blog_contexts, web_contexts = format_weaviate_and_you_contexts(blog_contexts, web_contexts)
            blog_container.evidence_paragraphs.append(self.topic_to_paragraph(topic=topic, original_question=question, web_contexts=web_contexts, blog_contexts=blog_contexts).paragraph)
        blog = format_blog_draft(blog_container)
        blog_container.bold_prediction = self.bold_prediction(blog=blog).bold_prediction
        blog_contexts = dspy.Retrieve(k=8)("What technology does Weaviate build?").passages
        blog_contexts = "".join(blog_contexts)
        blog_container.weaviate_relevance = self.weaviate_relevance(blog_contexts=blog_contexts, blog_post=blog).weaviate_relevance
        title_and_takeaways = self.title_and_key_takeaways(blog=blog, original_question=question)
        blog_container.title = title_and_takeaways.title
        blog_container.takeaways = title_and_takeaways.key_takeaways
        
        final_blog = format_blog_post(blog_container)
        return dspy.Prediction(blog=final_blog)