"""
Embedding Generation Utilities
"""

import os
from typing import List, Dict, Any, Optional
import voyageai
from dotenv import load_dotenv

load_dotenv()


class EmbeddingGenerator:
    """Generate embeddings using VoyageAI API"""
    
    def __init__(self, model: Optional[str] = None):
        self.client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.model = model or os.getenv("VOYAGE_EMBEDDING_MODEL", "voyage-2")
        self.dimensions = int(os.getenv("VECTOR_DIMENSIONS", 1024))
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        result = self.client.embed(
            texts=[text],
            model=self.model,
            input_type="document"
        )
        return result.embeddings[0]
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 128) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches"""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self.client.embed(
                texts=batch,
                model=self.model,
                input_type="document"
            )
            all_embeddings.extend(result.embeddings)
            print(f"  Generated embeddings for {min(i + batch_size, len(texts))}/{len(texts)} texts")
        
        return all_embeddings


def create_entity_text(entity: Dict[str, Any]) -> str:
    """Create searchable text representation of an entity"""
    parts = []
    
    # Entity type and name
    parts.append(f"{entity.get('entity_type', 'unknown')} named {entity.get('name', 'unknown')}")
    
    # Description
    if entity.get('description'):
        parts.append(entity['description'])
    
    # Key properties
    props = entity.get('properties', {})
    if props.get('criticality'):
        parts.append(f"Criticality level: {props['criticality']}")
    if props.get('data_classification'):
        parts.append(f"Data classification: {props['data_classification']}")
    if props.get('compliance_tags'):
        parts.append(f"Compliance: {', '.join(props['compliance_tags'])}")
    if props.get('owner'):
        parts.append(f"Owned by: {props['owner']}")
    if props.get('location'):
        parts.append(f"Location: {props['location']}")
    if props.get('security_zone'):
        parts.append(f"Security zone: {props['security_zone']}")
    
    return ". ".join(parts)


def create_firewall_rule_text(rule: Dict[str, Any]) -> str:
    """Create searchable text representation of a firewall rule"""
    parts = []
    
    parts.append(f"Firewall rule {rule.get('rule_id', 'unknown')} on {rule.get('firewall', 'unknown')}")
    parts.append(f"Named: {rule.get('name', 'unknown')}")
    
    # Zones
    parts.append(f"From {rule.get('source_zone', 'any')} to {rule.get('destination_zone', 'any')}")
    
    # Action
    parts.append(f"Action: {rule.get('action', 'unknown')}")
    
    # Description
    if rule.get('description'):
        parts.append(rule['description'])
    
    # Compliance notes
    if rule.get('compliance_notes'):
        parts.append(f"Compliance: {rule['compliance_notes']}")
    
    return ". ".join(parts)


def add_embeddings_to_entities(
    entities: List[Dict[str, Any]], 
    embedding_generator: EmbeddingGenerator
) -> List[Dict[str, Any]]:
    """Add embeddings to entities"""
    print("🔄 Generating embeddings for entities...")
    
    texts = [create_entity_text(entity) for entity in entities]
    embeddings = embedding_generator.generate_embeddings_batch(texts)
    
    for entity, embedding in zip(entities, embeddings):
        entity['description_embedding'] = embedding
    
    print(f"✅ Added embeddings to {len(entities)} entities")
    return entities


def add_embeddings_to_firewall_rules(
    rules: List[Dict[str, Any]], 
    embedding_generator: EmbeddingGenerator
) -> List[Dict[str, Any]]:
    """Add embeddings to firewall rules"""
    print("🔄 Generating embeddings for firewall rules...")
    
    texts = [create_firewall_rule_text(rule) for rule in rules]
    embeddings = embedding_generator.generate_embeddings_batch(texts)
    
    for rule, embedding in zip(rules, embeddings):
        rule['description_embedding'] = embedding
    
    print(f"✅ Added embeddings to {len(rules)} firewall rules")
    return rules

