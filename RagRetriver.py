from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
class RagRetriver:
    """Handles query based retrieval from the vector store"""

    def __init__(self,vector_store,embedding_manager):
        """
        Initialize the retriever

        Args:
            vector_store:Vector store containing document embeddings
            embedding_manager : Manager for generating query embeddings
        """

        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    
    def retrieve(self,query:str,top_k:int = 5, score_threshold:float = 0.0) -> List[Dict[str,Any]]:
        ##steps 1.first convert query to the embeding with same technique as for the document
        #2. then i will be searching for the document with collection.query method with the embedded query and take top k documents
        #3. then take the top documents and check for the document that meets threshold and only return thos documents which passes threshold
        """
        Retrieve relevant documents for a query
        
        Args:
            query:The Search query
            top_k : Number of top results to return
            score_threshold:Minimum similarity score threshold
        
        Returns:
            List of dictionaries containing retrieved documents and metadata

        """

        print(f"Retrieving documents for query : {query}")
        print(f"Top K : {top_k},score threshold {score_threshold}")

        #generate query embedding
        query_embedding = self.embedding_manager.generate_embedding([query])[0]

        #search in vector DB

        if self.vector_store.collection is None:
            raise RuntimeError("Vector store collection is not initialized")

        try:
            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],# one embedding is in a list with list of embeddings so we need to convert it to list then perform query search
                n_results=top_k
            )#returns top 5 resutls for collection with ids,metadata,embeddings,documnets list,

            retrieved_docs = []

            if results['documents'] and results['documents'][0]:#select all queried documents metadatas,ids and distances
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                ids = results['ids'][0]

                for i, (doc_id,document,metadata,distance) in enumerate (zip(ids,documents,metadatas,distances)):#now only the documents with threshold are retrived

                    similarity_score = 1 / (1 + distance)

                    # print(similarity_score)
                    if similarity_score >= score_threshold:

                        retrieved_docs.append({
                            'id':doc_id,
                            'content':document,
                            'metadata':metadata,
                            'similarity_score':similarity_score,
                            'distance':distance,
                            'rank':i+1
                        })

                print(f"Retrieved {len(retrieved_docs)} documents")
                # print(retrieved_docs)
            else:
                print('no document found')

            return retrieved_docs #this is now list of dictionaries of retrieved documents
                
        
        except Exception as e:
            print(f"Error retrieving : {e}")
            return []

