import numpy as np 
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
class Embedding_Manager:
    def __init__(self,model_name:str="all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager

        Args:
            model_name:HuggingFace model name for sentence embeddings
        """
        self.model = None
        self.model_name = model_name
        self._load_model()

    
    def _load_model(self):
        """
            Loads huggingface model for embedding
        """
        try:
            model = SentenceTransformer(self.model_name)
            self.model = model
            print(f"model {self.model_name} loaded successfully")
        
        except:
            raise ValueError('model not found.')
    
    def generate_embedding(self,texts:List[Any]) -> np.ndarray:
        """Generate embeddings for a list of texts

            Args:
            texts:List of text strings to embed

            Returns:
            numpy array of embeddings with shape (len(textss),embedding_dim)
        """
        if(self is None):
            raise ValueError('Model not found')

        embeddings = self.model.encode(texts,show_progress_bar=True)
        print(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    
        

        