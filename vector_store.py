import numpy as np
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
import uuid
import os
from sklearn.metrics.pairwise import cosine_similarity
class VectorStore:
    """
    Manages documeent embeddings in a chromaDB vector store
    """

    def __init__(self,collection_name:str = 'Youtube_transcript',persist_directory:str = './data/vector_store'):
        """
        initializ vector store
        
        :param self: Description
        :param collection_name: collection name in database
        :type collection_name: str
        :param persist_directory: persit storage directory in local machine
        :type persist_directory: str
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize ChromaDB client and collection"""

        try:
            os.makedirs(self.persist_directory,exist_ok=True)
            self.client = chromadb.PersistentClient(path = self.persist_directory)

            self.collection = self.client.get_or_create_collection(
                name = self.collection_name,
                metadata={"description":"Youtube video transcript embedding for RAG"}
            )
            print(f"Vector store initialized Collection:{self.collection_name}")
            print(f"Existing documents in collection:{self.collection.count()}")

        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise
    
    def add_documents(self,documents:List[Any],embeddings:np.ndarray):
        """
        Add documents and their embeddings to the vector store
        
        :param documents: List of Langchain documents
        :type documents: List[Any]
        :param embeddings: corresponding embeddings for documents
        :type embeddings: np.ndarray
        """
        
        if(len(documents) != len(embeddings)):
            raise ValueError("Number of documents must match no of Embeddings.")
        
        print(f"Adding {len(documents)} documents to vector store ...")

        ids = []
        metadatas = []
        document_texts = []
        embeddings_list = []

        for i,(doc,embeddings) in enumerate(zip(documents,embeddings)):
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)

            metadata = dict(doc.metadata)
            metadata['doc_index'] = i
            metadata['content_length'] = len(doc.page_content)
            metadatas.append(metadata)

            document_texts.append(doc.page_content) 

            embeddings_list.append(embeddings.tolist())

        # print(ids,metadatas,document_texts)
        self.collection.add(
            ids=ids,#list of ids with comma seperated ids
            embeddings=embeddings_list,#list of list of embeddings
            documents=document_texts,# in onelist there is comma seperated text field only from different documents
            metadatas=metadatas#list of metadatas of type dict of each document's metadata
        )

       

        # print(document_texts,embeddings_list)
        print(self.collection.count(),"documents successfully added in collection")


