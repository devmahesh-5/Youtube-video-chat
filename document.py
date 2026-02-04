from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
class Document_transcript:
    def __init__(self, transcript,videoId):
        self.transcript = transcript
        self.videoId = videoId
        self.docs = []
    
        self._load_document()
    
    def _load_document(self):
        docs = [
            Document(page_content=snippit.text,metadata={'start':snippit.start,'duration':snippit.duration,'source':self.videoId}) for snippit in self.transcript
        ]
        self.docs = docs
    
    def split_docs(self,chunk_size =1000,chunk_overlap = 200):
        documents = self.docs
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size= chunk_size,
            chunk_overlap = chunk_overlap,
            length_function = len,
            separators=["\n\n","\n",""," "]
        )
        chunks = text_splitter.split_documents(documents)
        print(f'split {len(documents)} into {len(chunks)} chunks')

        if (chunks):
            # print(f"content : {chunks[0].page_content[:1000]}")
            print(f"Metadata {chunks[0].metadata}")

        return chunks
    
    
    
    