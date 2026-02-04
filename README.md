## This is my RAG Retriver Project 
# What i have used??
- Langchain,chromaDB,youtube-transcript-api,sentence-transformers, python 3.12,Langchain_groq
- I have use groq llm as my llm 
  
## RAG Pipeline
- The RAG pipeline is as follows:
  1. first the video id is taken as input 
  2. then the transcript of the video is generated using youtube-transcript-api
  3. then the transcript is first transformed into langchain documents and then split into chunks using langchain-text-splitters
  4. then the embeddings are generated using sentence transformer model
  5. then the embeddings are added to the vector store using chromaDB here i also have persisted the vector store in data folder
  6. then comes main Retriver Pipeline where 1st the user query is taken as input which is converted to embeddings using sentence transformer model(same as above)
  7. then the resuts is fetched for top k document in collection with collection.query of chromaDB
  8. the fetched k documents along with embeddings and metadata again goes through another method for selecting only the relevant documents with threshold score 
  9. then the result is returned 
  10. now comes Augmentation and Generation Part where i have used groq llm to generate the response for the user query
  11. i also have sources and summary for the response along with the final answer 
  12. then the final answer is returned
