#!/usr/bin/env python3
"""
Test script for Jina embeddings integration
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from embedding_service import get_jina_embedding_service, EmbeddingService


def test_jina_embeddings(jina_api_key: str):
    """Test Jina embeddings functionality"""
    
    print("✅ Jina API key provided")
    
    try:
        # Create Jina embedding service
        print("\n🔧 Creating Jina embedding service...")
        jina_service = get_jina_embedding_service(api_key=jina_api_key)
        
        # Get model info
        model_info = jina_service.get_model_info()
        print(f"📊 Model info: {model_info}")
        
        # Test texts (using the examples from your curl request)
        test_texts = [
            "Organic skincare for sensitive skin with aloe vera and chamomile: Imagine the soothing embrace of nature with our organic skincare range, crafted specifically for sensitive skin. Infused with the calming properties of aloe vera and chamomile, each product provides gentle nourishment and protection. Say goodbye to irritation and hello to a glowing, healthy complexion.",
            "Bio-Hautpflege für empfindliche Haut mit Aloe Vera und Kamille: Erleben Sie die wohltuende Wirkung unserer Bio-Hautpflege, speziell für empfindliche Haut entwickelt. Mit den beruhigenden Eigenschaften von Aloe Vera und Kamille pflegen und schützen unsere Produkte Ihre Haut auf natürliche Weise. Verabschieden Sie sich von Hautirritationen und genießen Sie einen strahlenden Teint.",
            "Cuidado de la piel orgánico para piel sensible con aloe vera y manzanilla: Descubre el poder de la naturaleza con nuestra línea de cuidado de la piel orgánico, diseñada especialmente para pieles sensibles. Enriquecidos con aloe vera y manzanilla, estos productos ofrecen una hidratación y protección suave. Despídete de las irritaciones y saluda a una piel radiante y saludable.",
            "针对敏感肌专门设计的天然有机护肤产品：体验由芦荟和洋甘菊提取物带来的自然呵护。我们的护肤产品特别为敏感肌设计，温和滋润，保护您的肌肤不受刺激。让您的肌肤告别不适，迎来健康光彩。",
            "新しいメイクのトレンドは鮮やかな色と革新的な技術に焦点を当てています: 今シーズンのメイクアップトレンドは、大胆な色彩と革新的な技術に注目しています。ネオンアイライナーからホログラフィックハイライターまで、クリエイティビティを解き放ち、毎回ユニークなルックを演出しましょう。"
        ]
        
        print(f"\n📝 Testing with {len(test_texts)} multilingual texts...")
        
        # Generate embeddings
        print("🔄 Generating embeddings...")
        embeddings = jina_service.encode(test_texts)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"📏 Each embedding has {len(embeddings[0])} dimensions")
        
        # Test similarity between different languages
        print("\n🔍 Testing similarity between different languages...")
        
        # Compare English with other languages
        english_embedding = embeddings[0]
        
        similarities = []
        languages = ["English", "German", "Spanish", "Chinese", "Japanese"]
        
        for i, (lang, embedding) in enumerate(zip(languages[1:], embeddings[1:])):
            similarity = jina_service.similarity(english_embedding, embedding)
            similarities.append((lang, similarity))
            print(f"   English ↔ {lang}: {similarity:.4f}")
        
        # Find most similar language
        most_similar = max(similarities, key=lambda x: x[1])
        print(f"\n🏆 Most similar to English: {most_similar[0]} ({most_similar[1]:.4f})")
        
        # Test batch similarity
        print("\n📊 Testing batch similarity...")
        batch_similarities = jina_service.batch_similarity(english_embedding, embeddings[1:])
        
        for lang, sim in zip(languages[1:], batch_similarities):
            print(f"   {lang}: {sim:.4f}")
        
        print("\n✅ Jina embeddings test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Jina embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Testing Jina Embeddings Integration")
    print("=" * 50)
    
    # Test actual embeddings
    jina_api_key = "jina_ba0d2881234348758498f2c39b2f04afjX8ZUm4OmB2cTGBNQ2RQlOGQ-QbQ" # Directly using the provided API key
    embedding_success = test_jina_embeddings(jina_api_key)
    
    if embedding_success:
        print("\n🎉 All tests passed! Jina embeddings are working correctly.")
    else:
        print("\n❌ Embedding generation failed. Check your configuration.")
    
    print("\n" + "=" * 50)
    print("Test completed.")

