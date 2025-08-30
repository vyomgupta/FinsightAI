# Jina Embeddings Integration

This document describes the integration of Jina embeddings into the FinSightAI Vector Service Layer.

## Overview

Jina embeddings provide high-quality, multilingual text embeddings through their API. The integration supports:
- **Model**: `jina-embeddings-v3`
- **Task**: `text-matching` (optimized for semantic similarity)
- **Dimensions**: 1024
- **Languages**: Multi-language support (English, German, Spanish, Chinese, Japanese, etc.)

## Setup

### 1. API Key Configuration

Set your Jina API key as an environment variable:

**Windows (Command Prompt):**
```cmd
set JINA_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:JINA_API_KEY = "your_api_key_here"
```

**Linux/macOS:**
```bash
export JINA_API_KEY='your_api_key_here'
```

### 2. Installation

Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from embedding_service import get_jina_embedding_service

# Create Jina embedding service
jina_service = get_jina_embedding_service()

# Generate embeddings
texts = ["Hello world", "Bonjour le monde", "Hola mundo"]
embeddings = jina_service.encode(texts)

# Calculate similarity
similarity = jina_service.similarity(embeddings[0], embeddings[1])
```

### Advanced Configuration

```python
from embedding_service import create_embedding_service

# Custom configuration
jina_service = create_embedding_service(
    model_name="jina-embeddings-v3",
    model_type="jina",
    jina_api_key="your_custom_key"
)
```

### Integration with Vector Service Manager

```python
from vector_service_manager import VectorServiceManager

# Initialize with Jina embeddings
manager = VectorServiceManager(
    embedding_model_name="jina-embeddings-v3",
    embedding_model_type="jina"
)

# Add documents (embeddings will be generated automatically)
doc_ids = manager.add_documents([
    {"text": "Financial markets analysis", "metadata": {"category": "finance"}},
    {"text": "Stock trading strategies", "metadata": {"category": "trading"}}
])

# Search with semantic similarity
results = manager.search("investment opportunities", search_type="semantic")
```

## Testing

### Quick Test

Run the dedicated Jina test script:
```bash
python test_jina_embeddings.py
```

### Full System Test

Run the complete vector service test suite:
```bash
python test_vector_services.py
```

### Automated Testing

Use the provided scripts:

**Windows:**
```cmd
run_jina_test.bat
```

**PowerShell:**
```powershell
.\run_jina_test.ps1
```

## API Details

### Request Format

The integration automatically formats requests to the Jina API:

```json
{
  "model": "jina-embeddings-v3",
  "task": "text-matching",
  "input": ["text1", "text2", "text3"]
}
```

### Response Processing

Responses are automatically processed to extract embeddings:
```python
# API response structure
{
  "data": [
    {"embedding": [0.1, 0.2, ...]},
    {"embedding": [0.3, 0.4, ...]},
    {"embedding": [0.5, 0.6, ...]}
  ]
}
```

## Features

### Multilingual Support
- Automatically handles different languages
- Maintains semantic similarity across languages
- Optimized for cross-language comparisons

### Batch Processing
- Processes multiple texts efficiently
- Configurable batch sizes
- Automatic error handling and retries

### Normalization
- Embeddings are automatically normalized
- Cosine similarity calculations are optimized
- Consistent with other embedding models

## Performance

### Speed
- API-based processing (no local model loading)
- Batch processing for multiple texts
- Configurable timeout settings

### Quality
- 1024-dimensional embeddings
- Optimized for text-matching tasks
- High semantic accuracy

## Error Handling

The integration includes comprehensive error handling:

- **API Key Validation**: Checks for valid API key before making requests
- **Network Errors**: Handles connection timeouts and network issues
- **Rate Limiting**: Respects API rate limits
- **Fallback Options**: Can fall back to other embedding models if needed

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   ValueError: Jina API key not provided
   ```
   Solution: Set the `JINA_API_KEY` environment variable

2. **Network Timeout**
   ```
   requests.exceptions.Timeout
   ```
   Solution: Check internet connection and API availability

3. **Authentication Error**
   ```
   requests.exceptions.HTTPError: 401
   ```
   Solution: Verify your API key is correct

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Financial News Analysis

```python
# Analyze financial news in multiple languages
news_texts = [
    "Stock markets rise on positive earnings",
    "Los mercados de valores suben por ganancias positivas",
    "Die Aktienmärkte steigen aufgrund positiver Gewinne"
]

jina_service = get_jina_embedding_service()
embeddings = jina_service.encode(news_texts)

# Find most similar news items
similarities = jina_service.batch_similarity(embeddings[0], embeddings[1:])
```

### Document Clustering

```python
# Cluster documents by semantic similarity
documents = [
    {"id": "1", "text": "Investment strategies for beginners"},
    {"id": "2", "text": "Advanced trading techniques"},
    {"id": "3", "text": "Risk management in finance"}
]

# Generate embeddings
texts = [doc["text"] for doc in documents]
embeddings = jina_service.encode(texts)

# Calculate similarity matrix
similarity_matrix = []
for i, emb1 in enumerate(embeddings):
    row = []
    for j, emb2 in enumerate(embeddings):
        if i == j:
            row.append(1.0)
        else:
            row.append(jina_service.similarity(emb1, emb2))
    similarity_matrix.append(row)
```

## Integration Notes

- **Compatible**: Works seamlessly with existing vector service architecture
- **Extensible**: Easy to add new embedding models
- **Configurable**: Supports environment-based configuration
- **Tested**: Comprehensive test coverage included

## Support

For issues related to:
- **Jina API**: Contact Jina support
- **Integration**: Check the main vector service documentation
- **Testing**: Run the provided test scripts
