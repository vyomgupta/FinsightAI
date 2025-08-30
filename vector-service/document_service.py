"""
Document Service for FinSightAI
Handles document processing, metadata management, and document operations
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import uuid
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Document:
    """
    Represents a document in the system
    """
    
    def __init__(self, 
                 text: str,
                 document_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 embedding: Optional[List[float]] = None):
        """
        Initialize a document
        
        Args:
            text: Document text content
            document_id: Unique document identifier
            metadata: Document metadata
            embedding: Pre-computed embedding vector
        """
        self.text = text
        self.document_id = document_id or str(uuid.uuid4())
        self.metadata = metadata or {}
        self.embedding = embedding
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        
        # Generate content hash for change detection
        self.content_hash = self._generate_content_hash()
    
    def _generate_content_hash(self) -> str:
        """Generate hash of document content"""
        return hashlib.md5(self.text.encode('utf-8')).hexdigest()
    
    def update_text(self, new_text: str) -> bool:
        """
        Update document text
        
        Args:
            new_text: New text content
        
        Returns:
            True if text changed, False otherwise
        """
        if new_text != self.text:
            self.text = new_text
            self.content_hash = self._generate_content_hash()
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """
        Update document metadata
        
        Args:
            new_metadata: New metadata to merge
        """
        self.metadata.update(new_metadata)
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return {
            'id': self.document_id,
            'text': self.text,
            'metadata': self.metadata,
            'embedding': self.embedding,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'content_hash': self.content_hash
        }
    
    def to_chroma_format(self) -> Dict[str, Any]:
        """Convert to ChromaDB format"""
        return {
            'id': self.document_id,
            'text': self.text,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary"""
        return cls(
            text=data['text'],
            document_id=data.get('id'),
            metadata=data.get('metadata', {}),
            embedding=data.get('embedding')
        )


class DocumentService:
    """
    Service for managing documents and their operations
    """
    
    def __init__(self, storage_dir: str = "./documents"):
        """
        Initialize document service
        
        Args:
            storage_dir: Directory to store document metadata
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Document registry
        self.documents: Dict[str, Document] = {}
        self.metadata_index: Dict[str, List[str]] = {}
        
        # Load existing documents
        self._load_documents()
        
        logger.info(f"Document service initialized at {self.storage_dir}")
    
    def _load_documents(self) -> None:
        """Load existing documents from storage"""
        try:
            registry_file = self.storage_dir / "document_registry.json"
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for doc_data in data.get('documents', []):
                    doc = Document.from_dict(doc_data)
                    self.documents[doc.document_id] = doc
                
                # Rebuild metadata index
                self._rebuild_metadata_index()
                
                logger.info(f"Loaded {len(self.documents)} existing documents")
                
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
    
    def _save_documents(self) -> None:
        """Save documents to storage"""
        try:
            registry_file = self.storage_dir / "document_registry.json"
            
            data = {
                'exported_at': datetime.now().isoformat(),
                'document_count': len(self.documents),
                'documents': [doc.to_dict() for doc in self.documents.values()]
            }
            
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug("Documents saved to storage")
            
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
    
    def _rebuild_metadata_index(self) -> None:
        """Rebuild the metadata index"""
        self.metadata_index = {}
        
        for doc_id, doc in self.documents.items():
            for key, value in doc.metadata.items():
                if key not in self.metadata_index:
                    self.metadata_index[key] = {}
                
                if isinstance(value, (str, int, float, bool)):
                    if value not in self.metadata_index[key]:
                        self.metadata_index[key][value] = []
                    self.metadata_index[key][value].append(doc_id)
                elif isinstance(value, list):
                    for item in value:
                        if item not in self.metadata_index[key]:
                            self.metadata_index[key][item] = []
                        self.metadata_index[key][item].append(doc_id)
    
    def add_document(self, 
                    text: str,
                    document_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Add a new document
        
        Args:
            text: Document text content
            document_id: Optional document ID
            metadata: Document metadata
        
        Returns:
            Created document
        """
        try:
            # Check if document with same content already exists
            content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            
            for existing_doc in self.documents.values():
                if existing_doc.content_hash == content_hash:
                    logger.warning(f"Document with same content already exists: {existing_doc.document_id}")
                    return existing_doc
            
            # Create new document
            doc = Document(text=text, document_id=document_id, metadata=metadata)
            
            # Add to registry
            self.documents[doc.document_id] = doc
            
            # Update metadata index
            self._update_metadata_index(doc)
            
            # Save to storage
            self._save_documents()
            
            logger.info(f"Added document: {doc.document_id}")
            return doc
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def _update_metadata_index(self, doc: Document) -> None:
        """Update metadata index for a document"""
        for key, value in doc.metadata.items():
            if key not in self.metadata_index:
                self.metadata_index[key] = {}
            
            if isinstance(value, (str, int, float, bool)):
                if value not in self.metadata_index[key]:
                    self.metadata_index[key][value] = []
                if doc.document_id not in self.metadata_index[key][value]:
                    self.metadata_index[key][value].append(doc.document_id)
            elif isinstance(value, list):
                for item in value:
                    if item not in self.metadata_index[key]:
                        self.metadata_index[key][item] = []
                    if doc.document_id not in self.metadata_index[key][item]:
                        self.metadata_index[key][item].append(doc.document_id)
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """
        Get document by ID
        
        Args:
            document_id: Document ID to retrieve
        
        Returns:
            Document or None if not found
        """
        return self.documents.get(document_id)
    
    def update_document(self, 
                       document_id: str,
                       text: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing document
        
        Args:
            document_id: Document ID to update
            text: New text content
            metadata: New metadata to merge
        
        Returns:
            True if successful, False otherwise
        """
        try:
            doc = self.get_document(document_id)
            if not doc:
                logger.warning(f"Document {document_id} not found")
                return False
            
            # Update text if provided
            if text is not None:
                doc.update_text(text)
            
            # Update metadata if provided
            if metadata is not None:
                doc.update_metadata(metadata)
            
            # Rebuild metadata index
            self._rebuild_metadata_index()
            
            # Save to storage
            self._save_documents()
            
            logger.info(f"Updated document: {document_id}")
            return True
            
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
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found")
                return False
            
            # Remove from registry
            del self.documents[document_id]
            
            # Rebuild metadata index
            self._rebuild_metadata_index()
            
            # Save to storage
            self._save_documents()
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def search_documents(self, 
                        query: str = None,
                        metadata_filters: Optional[Dict[str, Any]] = None,
                        limit: Optional[int] = None) -> List[Document]:
        """
        Search documents by text and metadata
        
        Args:
            query: Text query to search in document content
            metadata_filters: Metadata filters to apply
            limit: Maximum number of results to return
        
        Returns:
            List of matching documents
        """
        try:
            matching_docs = []
            
            # Apply metadata filters first
            if metadata_filters:
                filtered_ids = self._apply_metadata_filters(metadata_filters)
                candidates = [self.documents[doc_id] for doc_id in filtered_ids if doc_id in self.documents]
            else:
                candidates = list(self.documents.values())
            
            # Apply text search if query provided
            if query:
                query_lower = query.lower()
                text_matches = []
                
                for doc in candidates:
                    if query_lower in doc.text.lower():
                        text_matches.append(doc)
                
                candidates = text_matches
            
            # Apply limit
            if limit:
                candidates = candidates[:limit]
            
            matching_docs = candidates
            
            logger.info(f"Search returned {len(matching_docs)} documents")
            return matching_docs
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def _apply_metadata_filters(self, filters: Dict[str, Any]) -> List[str]:
        """Apply metadata filters and return matching document IDs"""
        try:
            matching_ids = set()
            first_filter = True
            
            for key, value in filters.items():
                if key not in self.metadata_index:
                    continue
                
                if isinstance(value, (str, int, float, bool)):
                    if value in self.metadata_index[key]:
                        filter_ids = set(self.metadata_index[key][value])
                    else:
                        filter_ids = set()
                elif isinstance(value, list):
                    filter_ids = set()
                    for item in value:
                        if item in self.metadata_index[key]:
                            filter_ids.update(self.metadata_index[key][item])
                else:
                    continue
                
                if first_filter:
                    matching_ids = filter_ids
                    first_filter = False
                else:
                    # Intersection for AND logic
                    matching_ids = matching_ids.intersection(filter_ids)
                
                if not matching_ids:
                    break
            
            return list(matching_ids)
            
        except Exception as e:
            logger.error(f"Error applying metadata filters: {e}")
            return []
    
    def get_documents_by_category(self, category: str) -> List[Document]:
        """
        Get documents by category
        
        Args:
            category: Category to filter by
        
        Returns:
            List of documents in the category
        """
        return self.search_documents(metadata_filters={'category': category})
    
    def get_documents_by_source(self, source: str) -> List[Document]:
        """
        Get documents by source
        
        Args:
            source: Source to filter by
        
        Returns:
            List of documents from the source
        """
        return self.search_documents(metadata_filters={'source': source})
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
    
    def get_metadata_summary(self) -> Dict[str, Any]:
        """Get summary of document metadata"""
        try:
            summary = {
                'total_documents': len(self.documents),
                'metadata_fields': {},
                'categories': {},
                'sources': {}
            }
            
            # Analyze metadata
            for doc in self.documents.values():
                for key, value in doc.metadata.items():
                    if key not in summary['metadata_fields']:
                        summary['metadata_fields'][key] = set()
                    
                    if isinstance(value, (str, int, float, bool)):
                        summary['metadata_fields'][key].add(value)
                    elif isinstance(value, list):
                        summary['metadata_fields'][key].update(value)
                
                # Track categories and sources
                category = doc.metadata.get('category', 'unknown')
                source = doc.metadata.get('source', 'unknown')
                
                summary['categories'][category] = summary['categories'].get(category, 0) + 1
                summary['sources'][source] = summary['sources'].get(source, 0) + 1
            
            # Convert sets to lists for JSON serialization
            for key in summary['metadata_fields']:
                summary['metadata_fields'][key] = list(summary['metadata_fields'][key])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating metadata summary: {e}")
            return {}
    
    def export_documents(self, export_path: str, 
                        filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Export documents to JSON
        
        Args:
            export_path: Path to export file
            filters: Optional filters to apply before export
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Apply filters if provided
            if filters:
                documents_to_export = self.search_documents(metadata_filters=filters)
            else:
                documents_to_export = list(self.documents.values())
            
            # Prepare export data
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'document_count': len(documents_to_export),
                'filters_applied': filters,
                'documents': [doc.to_dict() for doc in documents_to_export]
            }
            
            # Write to file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(documents_to_export)} documents to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting documents: {e}")
            return False
    
    def import_documents(self, import_path: str, 
                        clear_existing: bool = False) -> bool:
        """
        Import documents from JSON
        
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
                self.documents.clear()
                self.metadata_index.clear()
                logger.info("Cleared existing documents")
            
            # Import documents
            imported_count = 0
            for doc_data in import_data.get('documents', []):
                try:
                    doc = Document.from_dict(doc_data)
                    self.documents[doc.document_id] = doc
                    imported_count += 1
                except Exception as e:
                    logger.warning(f"Error importing document: {e}")
                    continue
            
            # Rebuild metadata index
            self._rebuild_metadata_index()
            
            # Save to storage
            self._save_documents()
            
            logger.info(f"Imported {imported_count} documents from {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing documents: {e}")
            return False


# Factory function for easy service creation
def create_document_service(storage_dir: str = "./documents") -> DocumentService:
    """
    Factory function to create a document service
    
    Args:
        storage_dir: Directory to store document metadata
    
    Returns:
        Configured DocumentService instance
    """
    return DocumentService(storage_dir=storage_dir)


if __name__ == "__main__":
    # Test the document service
    service = create_document_service()
    
    # Test adding documents
    doc1 = service.add_document(
        text="This is a test document about finance.",
        metadata={'category': 'finance', 'source': 'test', 'tags': ['finance', 'test']}
    )
    
    doc2 = service.add_document(
        text="Another document about stock markets.",
        metadata={'category': 'markets', 'source': 'test', 'tags': ['markets', 'stocks']}
    )
    
    # Test search
    results = service.search_documents(query="finance")
    print(f"Search results: {len(results)} documents")
    
    # Test metadata filtering
    finance_docs = service.get_documents_by_category('finance')
    print(f"Finance documents: {len(finance_docs)}")
    
    # Get summary
    summary = service.get_metadata_summary()
    print(f"Metadata summary: {summary}")
