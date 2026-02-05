from transcript_generator import Transcript_Generator
from document import Document_transcript
from Embedding_Manager import Embedding_Manager
from vector_store import VectorStore
from RagRetriver import RagRetriver
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv
from search import AugmentedGeneration



load_dotenv()

os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    # other params...
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_session = {}

class ChatRequest(BaseModel):
    query: str
    video_id: str

class VideoIdRequest(BaseModel):
    video_id: str

@app.post("/api/retrive")
async def retrive_endpoint(request: VideoIdRequest):
    try:
        videoId = request.video_id
        transcript_generator = Transcript_Generator(videoId)
        transcript = transcript_generator.generate_transcript()

        transcipt_document = Document_transcript(transcript=transcript,videoId=videoId)
        transcript_chunks = transcipt_document.split_docs()

        texts = [doc.page_content for doc in transcript_chunks]#only text from the document in chunks

        embedding_manager = Embedding_Manager()

        embeddings = embedding_manager.generate_embedding(texts)#embedding vector of text

        vector_store = VectorStore()
        vector_store.add_documents(transcript_chunks,embeddings)#chunk have pagecontent,metadata



        ## RAG Retriver
        rag_retriver = RagRetriver(vector_store,embedding_manager)

        aug = AugmentedGeneration(rag_retriver, llm=llm)

        active_session[videoId] = aug

        return {"status": "success", "message": f"Video {videoId} indexed."}


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        videoId = request.video_id
        if videoId not in active_session:
            raise HTTPException(status_code=404, detail=f"Video {videoId} not found.")

        aug = active_session[videoId]

        def generate_wrapper():

            result = aug.generate(
                request.query, 
                top_k=3, 
                min_score=0.1, 
                stream=True, 
                summarize=True
            )

            answer_text = result.get('answer', '')
            
           
            yield f"data: {json.dumps({'token': answer_text})}\n\n"

            metadata = {
                "sources": result.get('sources', []),
                "summary": result.get('summary', '')
            }
            
            yield f"data: {json.dumps({'metadata': metadata})}\n\n"

        return StreamingResponse(generate_wrapper(), media_type="text/event-stream")

    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

