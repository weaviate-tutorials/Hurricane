// BlogPost.js
import React from 'react';

const BlogPost = ({ blogPost }) => {
  if (!blogPost) {
    return null;
  }

  return (
    <div class = "blogstyling">
      {blogPost.title && <h1>{blogPost.title}</h1>}
      {blogPost.introduction_paragraph && <p>{blogPost.introduction_paragraph}</p>}
      {blogPost.evidence_paragraphs && blogPost.evidence_paragraphs.length > 0 && (
        <div>
          {blogPost.evidence_paragraphs.map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>
      )}
      {blogPost.bold_prediction && (
        <div>
          <h3>Bold Prediction</h3>
          <p>{blogPost.bold_prediction}</p>
        </div>
      )}
      {blogPost.weaviate_relevance && (
        <div>
          <h3>Relevance to Weaviate</h3>
          <p>{blogPost.weaviate_relevance}</p>
        </div>
      )}
      {blogPost.takeaways && blogPost.takeaways.length > 0 && (
        <div>
          <h3>Takeaways from {blogPost.title}:</h3>
          <ul>
            {blogPost.takeaways.map((takeaway, index) => (
              <li key={index}>{takeaway}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default BlogPost;