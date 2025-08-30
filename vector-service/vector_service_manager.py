"""
Vector Service Manager for FinSightAI
Main interface that orchestrates all vector services
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json
from datetime import datetime

# Import our services
try:
    from .embedding_service import EmbeddingService, create_embedding_service
    from .chroma_service import ChromaService, create_chroma_service
    from .document_service import DocumentService, create_document_service
    from .search_service import SearchService, create_search_service
except ImportError:
    from embedding_service import EmbeddingService, create_embedding_service
    from chroma_service import ChromaService, create_chroma_service
    from document_service import DocumentService, create_document_service
    from search_service import SearchService, create_search_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorServiceManager:
    """
    Main interface for managing all vector services
    """
    
    def __init__(self,
                 config: Optional[Dict[str, Any]] = None,
                 base_dir: str = "./vector_services"):
        """
        Initialize the vector service manager
        
        Args:
            config: Configuration dictionary
            base_dir: Base directory for all services
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = config or self._load_default_config()
        
        # Initialize services
        self.embedding_service = None
        self.chroma_service = None
        self.document_service = None
        self.search_service = None
        
        # Initialize all services
        self._initialize_services()
        
        logger.info("Vector Service Manager initialized successfully")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'embedding': {
                'model_name': 'all-MiniLM-L6-v2',
                'model_type': 'sentence_transformers',
                'cache_dir': str(self.base_dir / 'embeddings')
            },
            'chroma': {
                'persist_directory': str(self.base_dir / 'chroma_db'),
                'collection_name': 'finsight_documents'
            },
            'document': {
                'storage_dir': str(self.base_dir / 'documents')
            },
            'search': {
                'default_search_type': 'hybrid',
                'semantic_weight': 0.7,
                'text_weight': 0.3
            }
        }
    
    def _initialize_services(self) -> None:
        """Initialize all vector services"""
        try:
            # Initialize embedding service
            embedding_config = self.config['embedding']
            self.embedding_service = create_embedding_service(
                model_name=embedding_config['model_name'],
                model_type=embedding_config['model_type'],
                cache_dir=embedding_config['cache_dir']
            )
            logger.info("Embedding service initialized")
            
            # Initialize ChromaDB service
            chroma_config = self.config['chroma']
            self.chroma_service = create_chroma_service(
                persist_directory=chroma_config['persist_directory'],
                collection_name=chroma_config['collection_name']
            )
            logger.info("ChromaDB service initialized")
            
            # Initialize document service
            document_config = self.config['document']
            self.document_service = create_document_service(
                storage_dir=document_config['storage_dir']
            )
            logger.info("Document service initialized")
            
            # Initialize search service
            self.search_service = create_search_service(
                embedding_service=self.embedding_service,
                chroma_service=self.chroma_service,
                document_service=self.document_service
            )
            logger.info("Search service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise
    
    def add_documents(self, 
                     documents: List[Dict[str, Any]],
                     generate_embeddings: bool = True,
                     add_to_vector_db: bool = True) -> List[str]:
        """
        Add documents to the system
        
        Args:
            documents: List of document dictionaries
            generate_embeddings: Whether to generate embeddings
            add_to_vector_db: Whether to add to vector database
        
        Returns:
            List of document IDs
        """
        try:
            added_ids = []
            
            for doc_data in documents:
                # Add to document service
                doc = self.document_service.add_document(
                    text=doc_data['text'],
                    document_id=doc_data.get('id'),
                    metadata=doc_data.get('metadata', {})
                )
                added_ids.append(doc.document_id)
                
                # Generate embedding if requested
                if generate_embeddings:
                    embedding = self.embedding_service.encode(doc.text)
                    doc.embedding = embedding
                    
                    # Update document with embedding
                    self.document_service.update_document(
                        doc.document_id,
                        metadata={'embedding_generated': True}
                    )
                
                # Add to vector database if requested
                if add_to_vector_db and generate_embeddings:
                    chroma_doc = doc.to_chroma_format()
                    self.chroma_service.add_documents([chroma_doc])
            
            logger.info(f"Added {len(added_ids)} documents to the system")
            return added_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(self, 
               query: str,
               search_type: str = "hybrid",
               n_results: int = 10,
               metadata_filters: Optional[Dict[str, Any]] = None,
               **kwargs) -> List[Any]:
        """
        Search for documents
        
        Args:
            query: Search query
            search_type: Type of search ('semantic', 'text', 'hybrid')
            n_results: Number of results to return
            metadata_filters: Metadata filters to apply
            **kwargs: Additional search parameters
        
        Returns:
            List of search results
        """
        try:
            if search_type == "semantic":
                return self.search_service.semantic_search(
                    query=query,
                    n_results=n_results,
                    metadata_filters=metadata_filters,
                    **kwargs
                )
            elif search_type == "text":
                return self.search_service.text_search(
                    query=query,
                    n_results=n_results,
                    metadata_filters=metadata_filters,
                    **kwargs
                )
            else:  # hybrid
                return self.search_service.hybrid_search(
                    query=query,
                    n_results=n_results,
                    metadata_filters=metadata_filters,
                    **kwargs
                )
                
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    def search_by_category(self, 
                          category: str,
                          query: str = None,
                          n_results: int = 10,
                          search_type: str = "hybrid") -> List[Any]:
        """Search within a specific category"""
        return self.search_service.search_by_category(
            category=category,
            query=query,
            n_results=n_results,
            search_type=search_type
        )
    
    def search_by_source(self, 
                        source: str,
                        query: str = None,
                        n_results: int = 10,
                        search_type: str = "hybrid") -> List[Any]:
        """Search within a specific source"""
        return self.search_service.search_by_source(
            source=source,
            query=query,
            n_results=n_results,
            search_type=search_type
        )
    
    def get_document(self, document_id: str) -> Optional[Any]:
        """Get a document by ID"""
        return self.document_service.get_document(document_id)
    
    def update_document(self, 
                       document_id: str,
                       text: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       regenerate_embedding: bool = False) -> bool:
        """
        Update a document
        
        Args:
            document_id: Document ID to update
            text: New text content
            metadata: New metadata
            regenerate_embedding: Whether to regenerate embedding
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update in document service
            success = self.document_service.update_document(
                document_id=document_id,
                text=text,
                metadata=metadata
            )
            
            if success and regenerate_embedding:
                # Get updated document
                doc = self.document_service.get_document(document_id)
                if doc:
                    # Generate new embedding
                    new_embedding = self.embedding_service.encode(doc.text)
                    
                    # Update in ChromaDB
                    chroma_doc = doc.to_chroma_format()
                    self.chroma_service.update_document(
                        document_id=document_id,
                        text=doc.text,
                        metadata=doc.metadata
                    )
                    
                    logger.info(f"Regenerated embedding for document {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        try:
            # Delete from document service
            doc_success = self.document_service.delete_document(document_id)
            
            # Delete from vector database
            vector_success = self.chroma_service.delete_document(document_id)
            
            return doc_success and vector_success
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'embedding': self.embedding_service.get_model_info() if self.embedding_service else None,
                    'chroma': self.chroma_service.get_collection_info() if self.chroma_service else None,
                    'document': {
                        'total_documents': self.document_service.get_document_count() if self.document_service else 0,
                        'metadata_summary': self.document_service.get_metadata_summary() if self.document_service else {}
                    }
                },
                'search_capabilities': self.search_service.get_search_analytics() if self.search_service else {},
                'configuration': self.config
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def export_system_data(self, export_path: str) -> bool:
        """
        Export all system data
        
        Args:
            export_path: Path to export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get system status
            status = self.get_system_status()
            
            # Export documents
            docs_export_path = str(Path(export_path).parent / "documents_export.json")
            docs_success = self.document_service.export_documents(docs_export_path)
            
            # Export vector database
            vector_export_path = str(Path(export_path).parent / "vector_export.json")
            vector_success = self.chroma_service.export_collection(vector_export_path)
            
            # Combine all exports
            export_data = {
                'system_status': status,
                'documents_exported': docs_success,
                'vector_data_exported': vector_success,
                'export_paths': {
                    'documents': docs_export_path if docs_success else None,
                    'vector_data': vector_export_path if vector_success else None
                }
            }
            
            # Write main export file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"System data exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting system data: {e}")
            return False
    
    def import_system_data(self, import_path: str, clear_existing: bool = False) -> bool:
        """
        Import system data
        
        Args:
            import_path: Path to import file
            clear_existing: Whether to clear existing data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read import file
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Import documents
            docs_path = import_data.get('export_paths', {}).get('documents')
            if docs_path and Path(docs_path).exists():
                docs_success = self.document_service.import_documents(
                    docs_path, clear_existing=clear_existing
                )
            else:
                docs_success = False
            
            # Import vector data
            vector_path = import_data.get('export_paths', {}).get('vector_data')
            if vector_path and Path(vector_path).exists():
                vector_success = self.chroma_service.import_collection(
                    vector_path, clear_existing=clear_existing
                )
            else:
                vector_success = False
            
            logger.info(f"System data import completed - Documents: {docs_success}, Vector: {vector_success}")
            return docs_success or vector_success
            
        except Exception as e:
            logger.error(f"Error importing system data: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # Close ChromaDB client
            if self.chroma_service:
                self.chroma_service.client.close()
            
            logger.info("Vector Service Manager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Factory function for easy manager creation
def create_vector_service_manager(config: Optional[Dict[str, Any]] = None,
                                base_dir: str = "./vector_services") -> VectorServiceManager:
    """
    Factory function to create a vector service manager
    
    Args:
        config: Configuration dictionary
        base_dir: Base directory for all services
    
    Returns:
        Configured VectorServiceManager instance
    """
    return VectorServiceManager(config=config, base_dir=base_dir)


# Pre-configured manager for common use cases
def get_default_vector_service_manager() -> VectorServiceManager:
    """Get a default vector service manager with recommended settings"""
    return create_vector_service_manager()


if __name__ == "__main__":
    # Test the vector service manager
    try:
        manager = get_default_vector_service_manager()
        
        # Get system status
        status = manager.get_system_status()
        print(f"System status: {json.dumps(status, indent=2)}")
        
        # Test adding documents
        test_docs = [
            {
                'text': 'This is a test document about finance and investments.',
                'metadata': {'category': 'finance', 'source': 'test', 'tags': ['finance', 'investments']}
            },
            {
                'text': 'Another document about stock market analysis and trading strategies.',
                'metadata': {'category': 'markets', 'source': 'test', 'tags': ['stocks', 'trading', 'analysis']}
            }
        ]
        
        doc_ids = manager.add_documents(test_docs)
        print(f"Added documents with IDs: {doc_ids}")
        
        # Test search
        results = manager.search("finance", search_type="hybrid", n_results=5)
        print(f"Search returned {len(results)} results")
        
        # Cleanup
        manager.cleanup()
        
    except Exception as e:
        print(f"Error testing vector service manager: {e}")
