import dspy

class Question2BlogOutline(dspy.Signature):
    """Your task is to write a Weaviate blog post that will help answer the given question.\nPlease use the contexts from a web search and published Weaviate blog posts to evaluate the structure of the blog post."""
    
    question = dspy.InputField()
    blog_context = dspy.InputField()
    web_context = dspy.InputField()
    blog_outline = dspy.OutputField(desc="A list of topics the blog will cover. IMPORTANT!! This must follow a comma separated list of values!")
    introduction_paragraph = dspy.OutputField(desc="An introduction overview of the blog post that previews the topics and presents the question the blog post seeks to answer.")

class Topic2Paragraph(dspy.Signature):
    """Please write a paragraph that explains a topic based on contexts fom a web search and blog posts from an authoritative source. You are also given the original question that inspired research into this topic, please try to connect your review of the topic to the original question."""
    
    topic = dspy.InputField(desc="A topic to write a paragraph about based on the information in the contexts.")
    original_question = dspy.InputField(desc="The original question that inspired research into this topic.")
    web_contexts = dspy.InputField(desc="Contains relevant information abuot the topic from a web search.")
    blog_contexts = dspy.InputField(desc="Contains relevant information about the topic from the published Weaviate blogs.")
    paragraph = dspy.OutputField()

class BoldPrediction(dspy.Signature):
    """Please review this blog post and propose a bold prediction about it's content."""

    blog = dspy.InputField()
    bold_prediction = dspy.OutputField(desc="A bold prediction about it's content.")

class WeaviateRelevance(dspy.Signature):
    """Please review this blog post and describe why it's content and the claims it's making are relevant for the development of the Weaviate Vector Database. You are given additional contexts describing what Weaviate is and some aspects of it's technology."""

    blog_contexts = dspy.InputField(desc="Content describing what Weaviate is")
    blog_post = dspy.InputField()
    weaviate_relevance = dspy.OutputField()

class TitleAndTakeaways(dspy.Signature):
    """Write a title and key takeaways for a blog post given the blog post and the original question it sought to answer as input and a bold prediction the author discovered after conducting initial research on the topic."""
    
    blog = dspy.InputField()
    original_question = dspy.InputField()
    title = dspy.OutputField()
    key_takeaways = dspy.OutputField(desc="A list of key takeaways from the blog. IMPORTANT!! This must follow a comma separated list of values!")