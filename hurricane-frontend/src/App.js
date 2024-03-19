// App.js
import React, { useState, useRef } from 'react';
import axios from 'axios';
import backgroundImage from './assets/bg-light-3.png';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import './App.css';
import BlogPost from './Blogpost';

const App = () => {
  const [thoughts, setThoughts] = useState(["Waiting for a question or topic."]);
  const [blog, setBlog] = useState('');
  const [inputValue, setInputValue] = useState('');
  const blogRef = useRef(null);

  const handleClick = async () => {
    try {
      // Call the /writeblog endpoint
      setThoughts(prevThoughts => ["Received question: " + String(inputValue)]);
      // Create Session
      const createSessionResponse = await axios.post('http://localhost:8000/create-session');
      const sessionId = String(createSessionResponse.data.session_id);

      console.log(inputValue);
      console.log(sessionId);
      const writeBlogResponse = await axios.post('http://localhost:8000/question-to-blog', {
        question: inputValue,
        sessionId: sessionId
      });
      setThoughts(prevThoughts => [...prevThoughts, writeBlogResponse.data.thoughts]);

      // Call the /researchtopic endpoint
      const researchTopicResponse = await axios.post('http://localhost:8000/topic-to-paragraph', {
        sessionId: sessionId
      });
      setThoughts(prevThoughts => [...prevThoughts, researchTopicResponse.data.thoughts]);

      // Call the /finishtask endpoint
      const boldPrediction = await axios.post('http://localhost:8000/bold-prediction', {
        sessionId: sessionId
      });
      setThoughts(prevThoughts => [...prevThoughts, boldPrediction.data.thoughts]);

      const weaviateRelevance = await axios.post('http://localhost:8000/weaviate-relevance', {
        sessionId: sessionId
      });
      setThoughts(prevThoughts => [...prevThoughts, weaviateRelevance.data.thoughts]);

      const finishTaskResponse = await axios.post('http://localhost:8000/finish-blog', {
        sessionId: sessionId
      });
      setBlog(finishTaskResponse.data.blog);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="app" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <h1>Hurricane</h1>
      <div className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter a question or topic..."
        />
        <button onClick={handleClick}>Process</button>
      </div>
      <div className="content-container">
        <div className="blog-container">
          <h2>Generated Blog</h2>
          <CSSTransition in={blog !== ''} timeout={300} classNames="fade" unmountOnExit>
            <BlogPost ref={blogRef} blogPost={blog} />
          </CSSTransition>
        </div>
        <div className="right-container">
          <div className="thoughts-container">
            <h2>Hurricane Updates</h2>
            <TransitionGroup>
      {thoughts.slice().reverse().map((thought, index) => (
        <CSSTransition key={index} timeout={300} classNames="fade">
          <div className="thought">{thought}</div>
        </CSSTransition>
      ))}
    </TransitionGroup>
          </div>
          <div className="status-container">
            <h2>Database Status</h2>
            <div className="WeaviateStatus">
              <div className="DataTable">
                <h3>Original Blog Count</h3>
                <h4>79 Blogs</h4>
                <h4>1182 Blog Chunks</h4>
              </div>
              <div className="DataTable">
                <h3>Generated Blog Count</h3>
                <h4>0 Blogs</h4>
                <h4>0 Blog Chunks</h4>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;