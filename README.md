# Hurricane 🌀
Writing Blog Posts with Generative Feedback Loops!

To run, follow these steps:
1. Spin up Weaviate with: (add your OpenAI API key)
```bash
docker-compose up -d
```
2. Insert the current Weaviate blogs into Weaviate by running:
```bash
python3 import_blogs.py
```
3. Start the backend with: (add your OpenAI and You API keys)
```bash
uvicorn backend:app --reload
```
4. Start the frontend with:
```bash
cd hurricane-frontend
npm install
npm start
```
