from transcript_generator import Transcript_Generator
from document import Document_transcript
from Embedding_Manager import Embedding_Manager
from vector_store import VectorStore
from RagRetriver import RagRetriver

videoId = 'cdYlZSzEHdQ'
transcript_generator = Transcript_Generator(videoId)
transcript = transcript_generator.generate_transcript()

transcipt_document = Document_transcript(transcript=transcript,videoId=videoId)
transcript_chunks = transcipt_document.split_docs()

texts = [doc.page_content for doc in transcript_chunks]#only text from the document in chunks

embedding_manager = Embedding_Manager()

embeddings = embedding_manager.generate_embedding(texts)#embedding vector of text

# print(embeddings)

vector_store = VectorStore()
vector_store.add_documents(transcript_chunks,embeddings)#chunk have pagecontent,metadata



## RAG Retriver
rag_retriver = RagRetriver(vector_store,embedding_manager)






#llm

import os
from dotenv import load_dotenv

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




## Now Augmentation
from search import AugmentedGeneration




aug = AugmentedGeneration(rag_retriver, llm=llm)
result = aug.generate("what is this youtube video about and what is her name?", top_k=3, min_score=0.1, stream=True, summarize=True)
print("\nFinal Answer:", result['answer'])
print("Summary:", result['summary'])
print("History:", result['history'][-1])
