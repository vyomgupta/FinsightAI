"""
ChromaDB Service for FinSightAI
Handles vector database operations including storage, retrieval, and similarity search
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import uuid
from datetime import datetime

# Try to import ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JinaEmbeddingFunction:
    """Custom embedding function for Jina embeddings in ChromaDB"""
    
    def __init__(self):
        """Initialize the Jina embedding function"""
        # Import here to avoid circular imports
        try:
            from embedding_service import EmbeddingService
            self.embedding_service = EmbeddingService()
            logger.info("Jina embedding function initialized for ChromaDB")
        except ImportError as e:
            logger.error(f"Failed to import embedding service: {e}")
            raise
    
    def __call__(self, input) -> List[List[float]]:
        """Generate embeddings for input texts"""
        try:
            # Handle both single strings and lists
            if isinstance(input, str):
                input = [input]
            
            # Generate embeddings using the Jina service
            embeddings = []
            for text in input:
                embedding = self.embedding_service.encode(text)
                embeddings.append(embedding.tolist() if hasattr(embedding, 'tolist') else embedding)
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 1024 for _ in input]


class ChromaService:
    """
    Service for managing ChromaDB vector database operations
    """
    
    def __init__(self, 
                 persist_directory: str = "./chroma_db",
                 collection_name: str = "finsight_documents",
                 embedding_function: Optional[Any] = None,
                 client_settings: Optional[Dict[str, Any]] = None):
        """
        Initialize ChromaDB service
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
            embedding_function: Custom embedding function
            client_settings: Additional ChromaDB client settings
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is not available. Please install it with: pip install chromadb")
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = self._initialize_client(client_settings)
        
        # Initialize or get collection
        self.collection = self._initialize_collection(embedding_function)
        
        logger.info(f"ChromaDB service initialized at {self.persist_directory}")
        logger.info(f"Collection: {self.collection_name}")
    
    def _initialize_client(self, client_settings: Optional[Dict[str, Any]]) -> chromadb.Client:
        """Initialize ChromaDB client"""
        try:
            settings = Settings(
                persist_directory=str(self.persist_directory),
                anonymized_telemetry=False
            )
            
            if client_settings:
                for key, value in client_settings.items():
                    setattr(settings, key, value)
            
            client = chromadb.Client(settings)
            logger.info("ChromaDB client initialized successfully")
            return client
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {e}")
            raise
    
    def _initialize_collection(self, embedding_function: Optional[Any]) -> chromadb.Collection:
        """Initialize or get the collection"""
        try:
            # Use Jina embedding function if none provided
            if embedding_function is None:
                try:
                    embedding_function = JinaEmbeddingFunction()
                    logger.info("Using Jina embedding function for ChromaDB")
                except Exception as e:
                    logger.warning(f"Failed to initialize Jina embedding function: {e}")
                    logger.info("Falling back to default embedding function")
                    embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Try to get existing collection first
            try:
                collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
                logger.info(f"Retrieved existing collection: {self.collection_name}")
                return collection
            except Exception as get_error:
                logger.debug(f"Collection {self.collection_name} not found, attempting to create: {get_error}")
            
            # If getting collection failed, try to create a new one
            try:
                collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function,
                    metadata={"description": "FinSightAI document collection"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
                return collection
            except Exception as create_error:
                # If creation also fails, it might be because collection exists but with different embedding function
                # Try to get it without specifying embedding function
                logger.warning(f"Failed to create collection, trying to get existing: {create_error}")
                try:
                    collection = self.client.get_collection(name=self.collection_name)
                    logger.info(f"Retrieved existing collection without embedding function: {self.collection_name}")
                    return collection
                except Exception as final_error:
                    logger.error(f"All attempts to initialize collection failed: {final_error}")
                    raise final_error
            
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def add_documents(self, 
                     documents: List[Dict[str, Any]],
                     batch_size: int = 100) -> List[str]:
        """
        Add documents to the vector database
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata' keys
            batch_size: Number of documents to process in each batch
        
        Returns:
            List of document IDs
        """
        try:
            if not documents:
                logger.warning("No documents provided")
                return []
            
            # Prepare documents for ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                # Generate unique ID if not provided
                doc_id = doc.get('id', str(uuid.uuid4()))
                ids.append(doc_id)
                
                # Extract text content
                text = doc.get('text', '')
                if not text:
                    logger.warning(f"Document {doc_id} has no text content, skipping")
                    continue
                
                texts.append(text)
                
                # Prepare metadata
                metadata = doc.get('metadata', {}).copy()
                metadata['added_at'] = datetime.now().isoformat()
                metadatas.append(metadata)
            
            # Add documents in batches
            all_ids = []
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                batch_texts = texts[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]
                
                try:
                    self.collection.add(
                        ids=batch_ids,
                        documents=batch_texts,
                        metadatas=batch_metadatas
                    )
                    all_ids.extend(batch_ids)
                    logger.info(f"Added batch of {len(batch_ids)} documents")
                    
                except Exception as e:
                    logger.error(f"Error adding batch {i//batch_size + 1}: {e}")
                    continue
            
            logger.info(f"Successfully added {len(all_ids)} documents")
            return all_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(self, 
               query: str,
               n_results: int = 10,
               where: Optional[Dict[str, Any]] = None,
               where_document: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for similar documents
        
        Args:
            query: Search query text
            n_results: Number of results to return
            where: Filter metadata conditions
            where_document: Filter document content conditions
        
        Returns:
            Search results with documents, metadatas, distances, and ids
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            logger.info(f"Search returned {len(results['ids'][0])} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    def search_by_embedding(self, 
                           query_embedding: List[float],
                           n_results: int = 10,
                           where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search using a pre-computed embedding
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Filter metadata conditions
        
        Returns:
            Search results
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"Embedding search returned {len(results['ids'][0])} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching by embedding: {e}")
            raise
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            document_id: Document ID to retrieve
        
        Returns:
            Document data or None if not found
        """
        try:
            result = self.collection.get(ids=[document_id])
            
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'text': result['documents'][0],
                    'metadata': result['metadatas'][0],
                    'embedding': result['embeddings'][0] if result['embeddings'] else None
                }
            else:
                logger.warning(f"Document {document_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None
    
    def update_document(self, 
                       document_id: str,
                       text: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing document
        
        Args:
            document_id: Document ID to update
            text: New text content
            metadata: New metadata
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing document
            existing = self.get_document(document_id)
            if not existing:
                return False
            
            # Prepare update data
            update_data = {}
            if text is not None:
                update_data['documents'] = [text]
            if metadata is not None:
                # Merge with existing metadata
                new_metadata = existing['metadata'].copy()
                new_metadata.update(metadata)
                new_metadata['updated_at'] = datetime.now().isoformat()
                update_data['metadatas'] = [new_metadata]
            
            if update_data:
                self.collection.update(
                    ids=[document_id],
                    **update_data
                )
                logger.info(f"Updated document {document_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document
        
        Args:
            document_id: Document ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def delete_collection(self) -> bool:
        """
        Delete the entire collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False
    
    def reset_collection(self, embedding_function: Optional[Any] = None) -> bool:
        """
        Reset the collection (delete and recreate)
        
        Args:
            embedding_function: Optional embedding function for the new collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete existing collection
            self.delete_collection()
            
            # Recreate collection
            self.collection = self._initialize_collection(embedding_function)
            
            logger.info(f"Reset collection {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection"""
        try:
            if not self.collection:
                return {"error": "No collection loaded"}
            
            # Get collection count
            count = self.collection.count()
            
            # Get collection name
            name = self.collection.name
            
            return {
                "collection_name": name,
                "document_count": count,
                "metadata_schema": self.collection.metadata_schema,
                "embedding_function": "jina-embeddings-v3"
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "error": str(e),
                "collection_name": self.collection.name if self.collection else "unknown",
                "document_count": 0
            }
    
    def export_collection(self, export_path: str) -> bool:
        """
        Export collection data to JSON
        
        Args:
            export_path: Path to export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all documents
            all_docs = self.collection.get()
            
            export_data = {
                "collection_name": self.collection_name,
                "exported_at": datetime.now().isoformat(),
                "document_count": len(all_docs['ids']),
                "documents": []
            }
            
            for i in range(len(all_docs['ids'])):
                doc_data = {
                    'id': all_docs['ids'][i],
                    'text': all_docs['documents'][i],
                    'metadata': all_docs['metadatas'][i]
                }
                export_data['documents'].append(doc_data)
            
            # Write to file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported collection to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting collection: {e}")
            return False
    
    def import_collection(self, import_path: str, clear_existing: bool = False) -> bool:
        """
        Import collection data from JSON
        
        Args:
            import_path: Path to import file
            clear_existing: Whether to clear existing documents first
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read import file
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Clear existing if requested
            if clear_existing:
                self.collection.delete(where={})
                logger.info("Cleared existing documents")
            
            # Prepare documents for import
            documents = []
            for doc in import_data.get('documents', []):
                documents.append({
                    'id': doc['id'],
                    'text': doc['text'],
                    'metadata': doc['metadata']
                })
            
            # Add documents
            if documents:
                self.add_documents(documents)
                logger.info(f"Imported {len(documents)} documents from {import_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error importing collection: {e}")
            return False


# Factory function for easy service creation
def create_chroma_service(persist_directory: str = "./chroma_db",
                         collection_name: str = "finsight_documents",
                         **kwargs) -> ChromaService:
    """
    Factory function to create a ChromaDB service
    
    Args:
        persist_directory: Directory to persist the database
        collection_name: Name of the collection to use
        **kwargs: Additional arguments for ChromaService
    
    Returns:
        Configured ChromaService instance
    """
    return ChromaService(
        persist_directory=persist_directory,
        collection_name=collection_name,
        **kwargs
    )


if __name__ == "__main__":
    # Test the ChromaDB service
    try:
        service = create_chroma_service()
        
        # Test adding documents
        test_docs = [
            {
                'id': 'doc1',
                'text': 'This is a test document about finance.',
                'metadata': {'category': 'finance', 'source': 'test'}
            },
            {
                'id': 'doc2',
                'text': 'Another document about stock markets.',
                'metadata': {'category': 'markets', 'source': 'test'}
            }
        ]
        
        service.add_documents(test_docs)
        
        # Test search
        results = service.search("finance", n_results=5)
        print(f"Search results: {results}")
        
        # Get collection info
        info = service.get_collection_info()
        print(f"Collection info: {info}")
        
    except Exception as e:
        print(f"Error testing ChromaDB service: {e}")
