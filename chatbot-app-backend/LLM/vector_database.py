import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime

class VectorDatabase:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = "vector_index"):
        """
        Initialize the Vector Database with FAISS and SentenceTransformers
        
        Args:
            model_name: HuggingFace model for embeddings
            index_path: Path to save/load FAISS index
        """
        self.model_name = model_name
        self.index_path = index_path
        self.embedding_model = SentenceTransformer(model_name)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.documents = []
        self.metadata = []
        
        # Load existing index if available
        self.load_index()
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts"""
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        return embeddings
    
    def add_documents(self, texts: List[str], metadata: List[Dict] = None):
        """
        Add documents to the vector database
        
        Args:
            texts: List of text documents to add
            metadata: Optional metadata for each document
        """
        if not texts:
            return
        
        embeddings = self.create_embeddings(texts)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store documents and metadata
        self.documents.extend(texts)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(texts))
        
        print(f"Added {len(texts)} documents. Total documents: {len(self.documents)}")
    
    def search(self, query: str, k: int = 5, score_threshold: float = 0.3) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of dictionaries with document, metadata, and score
        """
        if self.index.ntotal == 0:
            return []
        
        # Create query embedding
        query_embedding = self.create_embeddings([query])
        
        # Search
        scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= score_threshold and idx < len(self.documents):
                results.append({
                    'document': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'score': float(score),
                    'index': int(idx)
                })
        
        return results
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{self.index_path}.faiss")
        
        # Save documents and metadata
        with open(f"{self.index_path}_data.pkl", 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'model_name': self.model_name,
                'dimension': self.dimension,
                'created_at': datetime.now().isoformat()
            }, f)
        
        print(f"Index saved to {self.index_path}")
    
    def load_index(self):
        """Load FAISS index and metadata from disk"""
        faiss_path = f"{self.index_path}.faiss"
        data_path = f"{self.index_path}_data.pkl"
        
        if os.path.exists(faiss_path) and os.path.exists(data_path):
            try:
                # Load FAISS index
                self.index = faiss.read_index(faiss_path)
                
                # Load documents and metadata
                with open(data_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.metadata = data.get('metadata', [])
                    saved_model = data.get('model_name', self.model_name)
                    
                    if saved_model != self.model_name:
                        print(f"Warning: Loaded model ({saved_model}) differs from current model ({self.model_name})")
                
                print(f"Loaded index with {len(self.documents)} documents")
                
            except Exception as e:
                print(f"Error loading index: {e}")
                # Initialize empty index
                self.index = faiss.IndexFlatIP(self.dimension)
                self.documents = []
                self.metadata = []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal,
            'dimension': self.dimension,
            'model_name': self.model_name
        }

class FinancialVectorDB:
    def __init__(self, dataset_path: str = r"C:\mydata\MUFG\Hackathon_Dataset.csv"):
        """
        Specialized vector database for financial data
        """
        self.dataset_path = dataset_path
        self.vector_db = VectorDatabase(index_path="financial_vector_index")
        self.df = None
        
        # Load and process dataset
        self.load_financial_data()
    
    def load_financial_data(self):
        """Load and process financial dataset into vector database"""
        try:
            self.df = pd.read_csv(self.dataset_path)
            print(f"Loaded dataset with {len(self.df)} rows")
            
            # Only process if index is empty
            if self.vector_db.index.ntotal == 0:
                self.process_dataset()
            
        except Exception as e:
            print(f"Error loading financial data: {e}")
            self.df = pd.DataFrame()
    
    def process_dataset(self):
        """Process dataset into searchable chunks"""
        if self.df.empty:
            return
        
        documents = []
        metadata = []
        
        for idx, row in self.df.iterrows():
            # Create comprehensive text representation of each fund/investment
            fund_text = self.create_fund_description(row)
            documents.append(fund_text)
            
            # Store metadata
            metadata.append({
                'index': idx,
                'fund_type': row.get('Fund_Type', ''),
                'fund_name': row.get('Fund_Name', ''),
                'annual_return': row.get('Annual_Return_%', 0),
                'risk_level': row.get('Risk_Level', ''),
                'original_data': row.to_dict()
            })
        
        # Add to vector database
        self.vector_db.add_documents(documents, metadata)
        self.vector_db.save_index()
    
    def create_fund_description(self, row) -> str:
        """Create a comprehensive text description of a fund for embedding"""
        description_parts = []
        
        # Fund basics
        fund_name = row.get('Fund_Name', 'Unknown Fund')
        fund_type = row.get('Fund_Type', 'Unknown Type')
        description_parts.append(f"Fund Name: {fund_name}")
        description_parts.append(f"Fund Type: {fund_type}")
        
        # Performance metrics
        annual_return = row.get('Annual_Return_%', 0)
        description_parts.append(f"Annual Return: {annual_return}%")
        
        # Risk characteristics
        risk_level = row.get('Risk_Level', 'Unknown')
        description_parts.append(f"Risk Level: {risk_level}")
        
        # Additional characteristics
        for col in ['Sector', 'Investment_Strategy', 'Target_Audience', 'Management_Style']:
            if col in row and pd.notna(row[col]):
                description_parts.append(f"{col.replace('_', ' ')}: {row[col]}")
        
        # Create searchable text
        searchable_text = " | ".join(description_parts)
        
        # Add contextual information for better matching
        context_terms = []
        if 'growth' in fund_type.lower():
            context_terms.extend(['high growth', 'capital appreciation', 'aggressive investment'])
        elif 'conservative' in fund_type.lower():
            context_terms.extend(['low risk', 'capital preservation', 'stable returns'])
        elif 'balanced' in fund_type.lower():
            context_terms.extend(['moderate risk', 'diversified', 'mixed portfolio'])
        
        if context_terms:
            searchable_text += " | Context: " + ", ".join(context_terms)
        
        return searchable_text
    
    def search_funds(self, query: str, k: int = 5, score_threshold: float = 0.3) -> List[Dict]:
        """Search for relevant funds based on query"""
        return self.vector_db.search(query, k, score_threshold)
    
    def get_similar_funds(self, fund_name: str, k: int = 3) -> List[Dict]:
        """Get funds similar to a specific fund"""
        return self.search_funds(fund_name, k)
    
    def search_by_criteria(self, risk_level: str = None, fund_type: str = None, 
                          min_return: float = None, k: int = 5) -> List[Dict]:
        """Search funds by specific criteria"""
        query_parts = []
        
        if risk_level:
            query_parts.append(f"risk level {risk_level}")
        if fund_type:
            query_parts.append(f"fund type {fund_type}")
        if min_return:
            query_parts.append(f"high return above {min_return}%")
        
        query = " ".join(query_parts) if query_parts else "investment fund"
        return self.search_funds(query, k)
    
    def get_fund_recommendations(self, user_profile: Dict) -> List[Dict]:
        """Get fund recommendations based on user profile"""
        query_parts = []
        
        # Build query based on user profile
        risk_tolerance = user_profile.get('risk_tolerance', '').lower()
        if risk_tolerance:
            query_parts.append(f"risk tolerance {risk_tolerance}")
        
        investment_experience = user_profile.get('investment_experience', '').lower()
        if investment_experience:
            query_parts.append(f"investment experience {investment_experience}")
        
        age = user_profile.get('age', 0)
        if age:
            if age < 35:
                query_parts.append("growth high return aggressive investment young investor")
            elif age < 55:
                query_parts.append("balanced moderate risk diversified portfolio")
            else:
                query_parts.append("conservative low risk stable returns retirement")
        
        retirement_goal = user_profile.get('retirement_goal', 0)
        if retirement_goal:
            query_parts.append(f"retirement planning target {retirement_goal}")
        
        query = " ".join(query_parts) if query_parts else "suitable investment fund"
        return self.search_funds(query, k=7, score_threshold=0.2)
