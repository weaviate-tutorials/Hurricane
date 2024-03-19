# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import dspy
from dspy.retrieve.weaviate_rm import WeaviateRM
from dspy.retrieve.you_rm import YouRM
import weaviate
from weaviate.util import get_valid_uuid
from uuid import uuid4
import openai
from hurricane_signatures import Question2BlogOutline, Topic2Paragraph, BoldPrediction, WeaviateRelevance, TitleAndTakeaways
from utils import format_weaviate_and_you_contexts
from utils import format_blog_draft, format_blog_post, BlogPost
import os
import re

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_APIKEY")
you_api_key = os.getenv("YOU_APIKEY")

gpt = dspy.OpenAI(model="gpt-3.5-turbo", max_tokens=4000, model_type="chat")

weaviate_client = weaviate.Client("http://localhost:8080")
weaviate_rm = WeaviateRM("WeaviateBlogChunk", weaviate_client=weaviate_client)
you_rm = YouRM(ydc_api_key=you_api_key)
dspy.settings.configure(lm=gpt, rm=weaviate_rm)

# placeholder for loading compiled parameters
class Hurricane(dspy.Module):
    def __init__(self):
        self.question_to_blog_outline = dspy.Predict(Question2BlogOutline)
        self.topic_to_paragraph = dspy.Predict(Topic2Paragraph)
        self.bold_prediction = dspy.Predict(BoldPrediction)
        self.weaviate_relevance = dspy.Predict(WeaviateRelevance)
        self.title_and_key_takeaways = dspy.Predict(TitleAndTakeaways)
    def forward():
        pass

compiled_hurricane = Hurricane()
compiled_hurricane.load("gpt4_compiled_hurricane.json")
question_to_blog_outline = compiled_hurricane.question_to_blog_outline
topic_to_paragraph = compiled_hurricane.topic_to_paragraph
bold_prediction = compiled_hurricane.bold_prediction
weaviate_relevance = compiled_hurricane.weaviate_relevance
title_and_key_takeaways = compiled_hurricane.title_and_key_takeaways

'''
# How to init without loading a compiled program
question_to_blog_outline = dspy.Predict(Question2BlogOutline)
topic_to_paragraph = dspy.Predict(Topic2Paragraph)
bold_prediction = dspy.Predict(BoldPrediction)
weaviate_relevance = dspy.Predict(WeaviateRelevance)
title_and_key_takeaways = dspy.Predict(TitleAndTakeaways)
'''

from pydantic import BaseModel

blog_container = BlogPost()

class InitQuestionRequest(BaseModel):
    question: str
    sessionId: str

class SessionRequest(BaseModel):
    sessionId: str

import random

@app.post("/create-session")
async def create_session():
    wevaiate_gfl_client = weaviate.connect_to_local()
    weaviate_blog_collection = wevaiate_gfl_client.collections.get("Blog")
    random_uuid = get_valid_uuid(uuid4())
    uuid = weaviate_blog_collection.data.insert(
        uuid=random_uuid,
        properties={}
    )
    wevaiate_gfl_client.close()
    return {"session_id" : random_uuid}

@app.post("/question-to-blog")
async def write_blog(request: InitQuestionRequest):
    question = request.question
    sessionId = request.sessionId
    weaviate_gfl_client = weaviate.connect_to_local()
    weaviate_blog_collection = weaviate_gfl_client.collections.get("Blog")
    # Save State to Weaviate
    weaviate_blog_collection.data.update(
        uuid=sessionId,
        properties={
            "question": question
        }
    )
    blog_contexts = dspy.Retrieve(k=5)(question).passages
    web_contexts = you_rm(question)
    blog_contexts, web_contexts = format_weaviate_and_you_contexts(blog_contexts, web_contexts)
    question_to_blog_outline_outputs = question_to_blog_outline(question=question, blog_context=blog_contexts, web_context=web_contexts)
    # Save State to Weaviate
    weaviate_blog_collection.data.update(
        uuid=sessionId,
        properties={
            "outline": question_to_blog_outline_outputs.blog_outline
        }
    )
    # Save State to Weaviate
    weaviate_blog_collection.data.update(
        uuid=sessionId,
        properties={
            "introduction_paragraph": question_to_blog_outline_outputs.introduction_paragraph + "\n"
        }
    )
    weaviate_gfl_client.close()
    thoughts = "Finished making an outline for the blog post."
    return {"thoughts": thoughts}

@app.post("/topic-to-paragraph")
async def research_topic(request: SessionRequest):
    sessionId = request.sessionId
    weaviate_gfl_client = weaviate.connect_to_local()
    weaviate_blog_collection = weaviate_gfl_client.collections.get("Blog")
    # Simulating research process
    # Load State
    blog_outline = weaviate_blog_collection.query.fetch_object_by_id(sessionId).properties["outline"]
    blog_outline = blog_outline.split(",")
    evidence_paragraphs = []
    for topic in blog_outline:
        blog_contexts = dspy.Retrieve(k=3)(topic).passages
        web_contexts = you_rm(topic)
        blog_contexts, web_contexts = format_weaviate_and_you_contexts(blog_contexts, web_contexts)
        # Load State `question`
        weaviate_blog_collection.query.fetch_object_by_id(sessionId)
        question = weaviate_blog_collection.query.fetch_object_by_id(sessionId).properties["question"]
        evidence_paragraphs.append(topic_to_paragraph(topic=topic, original_question=blog_container.question, web_contexts=web_contexts, blog_contexts=blog_contexts).paragraph)
    # Save State, ToDo split this into multiple API calls
    weaviate_blog_collection.data.update(
        uuid=sessionId,
        properties={
            "evidence_paragraphs": evidence_paragraphs
        }
    )
    weaviate_gfl_client.close()
    thoughts = "Finished writing evidence paragraphs."
    return {"thoughts": thoughts}

@app.post("/bold-prediction")
async def bold_prediction_generator(request: SessionRequest):
    sessionId = request.sessionId
    weaviate_gfl_client = weaviate.connect_to_local()
    weaviate_blog_collection = weaviate_gfl_client.collections.get("Blog")

    # load state into a BlogPost to format_blog_draft
    blog_container = BlogPost()
    saved_blog_properties = weaviate_blog_collection.query.fetch_object_by_id(sessionId)
    # dump state into a Pydantic model
    for key in saved_blog_properties.properties:
        setattr(blog_container, key, saved_blog_properties.properties[key])
    blog = format_blog_draft(blog_container)
    bold_prediction_response = bold_prediction(blog=blog)
    weaviate_blog_collection.data.update(
        uuid=sessionId,
        properties={
            "bold_prediction": bold_prediction_response.bold_prediction
        }
    )
    weaviate_gfl_client.close()
    thoughts = "Formed a bold prediction based on the research."
    return {"thoughts": thoughts}


@app.post("/weaviate-relevance")
async def weaviate_relevance_generator(request: SessionRequest):
    sessionId = request.sessionId
    weaviate_gfl_client = weaviate.connect_to_local()
    weaviate_blog_collection = weaviate_gfl_client.collections.get("Blog")
    # load state into a BlogPost to format_blog_draft
    blog_container = BlogPost()
    saved_blog_properties = weaviate_blog_collection.query.fetch_object_by_id(sessionId)
    # dump state into a Pydantic model
    for key in saved_blog_properties.properties:
        setattr(blog_container, key, saved_blog_properties.properties[key])
    blog = format_blog_draft(blog_container)
    blog_contexts = dspy.Retrieve(k=5)("What technology does Weaviate build?").passages
    blog_contexts = "".join(blog_contexts)
    weaviate_relevance_response = weaviate_relevance(blog_contexts=blog_contexts, blog_post=blog)
    # Save State
    weaviate_blog_collection.data.update(
        uuid=sessionId,
        properties={
            "weaviate_relevance": weaviate_relevance_response.weaviate_relevance
        }
    )
    weaviate_gfl_client.close()
    thoughts = "Researched why this topic is relevant to Weaviate."
    return {"thoughts": thoughts}

@app.post("/finish-blog")
async def finish_task(request: SessionRequest):
    sessionId = request.sessionId
    weaviate_gfl_client = weaviate.connect_to_local()
    weaviate_blog_collection = weaviate_gfl_client.collections.get("Blog")
    
    # load state into a BlogPost to format_blog_draft
    blog_container = BlogPost()
    saved_blog_properties = weaviate_blog_collection.query.fetch_object_by_id(sessionId)
    # dump state into a Pydantic model
    for key in saved_blog_properties.properties:
        setattr(blog_container, key, saved_blog_properties.properties[key])
    blog = format_blog_draft(blog_container)
    title_and_takeaways = title_and_key_takeaways(blog=blog, original_question=blog_container.question)
    # bug, fix later
    title = title_and_takeaways.title
    cleaned_title = re.sub(r"Title:", "", title)
    blog_container.title = cleaned_title
    blog_container.takeaways = title_and_takeaways.key_takeaways.split(",")
    # ToDo, Save Final State into Weaviate
    # ToDo, query # of AI-generated blog posts and chunks
    # ToDo, return Database Status

    weaviate_gfl_client.close()
    # Rendering the final blog on the front-end in `Blogpost.js`
    return {"blog": blog_container}