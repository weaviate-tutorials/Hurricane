import weaviate
import weaviate.classes as wvc

client = weaviate.connect_to_local()

client.collections.create(
    name="Blog",
    description="An AI-generated blog post by Hurricane.",
    properties=[
        wvc.config.Property(
            data_type=wvc.config.DataType.TEXT,
            description="Title of the Article",
            name="title",
        ),
        wvc.config.Property(
            data_type=wvc.config.DataType.TEXT,
            description="Initial question that inspired the blog post.",
            name="question",   
        ),
        wvc.config.Property(
            data_type=wvc.config.DataType.TEXT,
            description="The introduction paragraph",
            name="introduction_paragraph",    
        ),
        wvc.config.Property(
            data_type=wvc.config.DataType.TEXT,
            description="The outline for the blog.",
            name="outline",    
        ),
        wvc.config.Property(
            data_type=wvc.config.DataType.TEXT_ARRAY,
            description="Evidence paragraphs that support the arguments in the blog.",
            name="evidence_paragraphs"    
        ),
        wvc.config.Property(
            data_type=wvc.config.DataType.TEXT,
            description="A bold prediciton based on the content of the blog post.",
            name="bold_prediction"    
        ),
        wvc.config.Property(
            data_type=wvc.config.DataType.TEXT,
            description="The relevance of the blog post to the Weaviate Vector Database.",
            name="weaviate_relevance",    
        ),
        wvc.config.Property(
            data_type=wvc.config.DataType.TEXT_ARRAY,
            description="Takeaways from the blog post.",
            name="takeaways"    
        ),
    ]
)

client.close()