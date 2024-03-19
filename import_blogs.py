# Import Weaviate and Connect to Client
import weaviate
client = weaviate.Client("http://localhost:8080")

# Create Schema
schema = {
   "classes": [
       {
           "class": "WeaviateBlogChunk",
           "description": "A snippet from a Weaviate blogpost.",
           "moduleConfig": {
               "text2vec-openai": {
                    "skip": False,
                    "vectorizeClassName": False,
                    "vectorizePropertyName": False
                },
                "generative-openai": {
                    "model": "gpt-3.5-turbo"
                }
           },
           "vectorIndexType": "hnsw",
           "vectorizer": "text2vec-openai",
           "properties": [
               {
                   "name": "content",
                   "dataType": ["text"],
                   "description": "The text content of the podcast clip",
                   "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": False,
                        "vectorizePropertyName": False,
                        "vectorizeClassName": False
                    }
                   }
               },
               {
                "name": "author",
                "dataType": ["text"],
                "description": "The author of the blog post.",
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True,
                        "vectorizePropertyName": False,
                        "vectorizeClassName": False
                    }
                }
               }
           ]
       }      
   ]
}
    
client.schema.create(schema)

import os
import re

def chunk_list(lst, chunk_size):
    """Break a list into chunks of the specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def split_into_sentences(text):
    """Split text into sentences using regular expressions."""
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]

def read_and_chunk_index_files(main_folder_path):
    """Read index.md files from subfolders, split into sentences, and chunk every 5 sentences."""
    blog_chunks = []
    
    # You need to keep the part-whole relationship here
    
    for folder_name in os.listdir(main_folder_path):
        subfolder_path = os.path.join(main_folder_path, folder_name)
        if os.path.isdir(subfolder_path):
            index_file_path = os.path.join(subfolder_path, 'index.mdx')
            if os.path.isfile(index_file_path):
                with open(index_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    sentences = split_into_sentences(content)
                    sentence_chunks = chunk_list(sentences, 5)
                    sentence_chunks = [' '.join(chunk) for chunk in sentence_chunks]
                    blog_chunks.extend(sentence_chunks)
    return blog_chunks

# Example usage
main_folder_path = './blog'
blog_chunks = read_and_chunk_index_files(main_folder_path)

client.batch.configure(
  # `batch_size` takes an `int` value to enable auto-batching
  # (`None` is used for manual batching)
  batch_size=100,
  # dynamically update the `batch_size` based on import speed
  dynamic=False,
  # `timeout_retries` takes an `int` value to retry on time outs
  timeout_retries=3,
  # checks for batch-item creation errors
  # this is the default in weaviate-client >= 3.6.0
  callback=weaviate.util.check_batch_result,
)

from weaviate.util import get_valid_uuid
from uuid import uuid4
import time
start = time.time()
for idx, blog_chunk in enumerate(blog_chunks):
    data_properties = {
        "content": blog_chunk
    }
    id = get_valid_uuid(uuid4())
    with client.batch as batch:
        batch.add_data_object(
            data_properties,
            "WeaviateBlogChunk"
        )
    '''
    client.data_object.create(
        data_object = data_properties,
        class_name = "WeaviateBlogChunk",
        uuid=id
    )
    '''

print(f"Uploaded {idx} documents in {time.time() - start} seconds.")
