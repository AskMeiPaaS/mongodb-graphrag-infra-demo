#!/usr/bin/env python3
"""
Load Sample Data Script
Generates sample infrastructure data with embeddings and loads into MongoDB
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import (
    get_db, 
    insert_entities, 
    insert_relationships, 
    insert_firewall_rules,
    get_collection_stats,
    clear_collections
)
from src.embeddings import (
    EmbeddingGenerator,
    add_embeddings_to_entities,
    add_embeddings_to_firewall_rules
)
from data.sample_data import (
    generate_entities,
    generate_relationships,
    generate_firewall_rules
)


def main():
    print("=" * 60)
    print("MongoDB Infrastructure Knowledge Graph - Load Sample Data")
    print("=" * 60)
    
    # Connect to database
    print("\n📡 Connecting to MongoDB Atlas...")
    db = get_db()
    
    # Check if data exists
    stats = get_collection_stats(db)
    if any(count > 0 for count in stats.values()):
        print("\n⚠️  Collections already have data:")
        for collection, count in stats.items():
            print(f"  - {collection}: {count} documents")
        response = input("\nClear existing data and reload? (y/N): ")
        if response.lower() != 'y':
            print("Aborting. Use existing data.")
            return
        clear_collections(db)
    
    # Generate sample data
    print("\n📦 Generating sample infrastructure data...")
    
    start_time = time.time()
    
    entities = generate_entities()
    print(f"  ✓ Generated {len(entities)} entities")
    
    relationships = generate_relationships()
    print(f"  ✓ Generated {len(relationships)} relationships")
    
    firewall_rules = generate_firewall_rules()
    print(f"  ✓ Generated {len(firewall_rules)} firewall rules")
    
    # Initialize embedding generator
    print("\n🧠 Initializing embedding generator...")
    embedding_gen = EmbeddingGenerator()
    
    # Add embeddings to entities
    print("\n🔄 Generating embeddings for entities...")
    entities_with_embeddings = add_embeddings_to_entities(entities, embedding_gen)
    
    # Add embeddings to firewall rules
    print("\n🔄 Generating embeddings for firewall rules...")
    rules_with_embeddings = add_embeddings_to_firewall_rules(firewall_rules, embedding_gen)
    
    # Insert data
    print("\n💾 Inserting data into MongoDB...")
    
    insert_entities(db, entities_with_embeddings)
    insert_relationships(db, relationships)
    insert_firewall_rules(db, rules_with_embeddings)
    
    end_time = time.time()
    
    # Final statistics
    print("\n✅ Data loading complete!")
    print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
    
    print("\n📊 Final collection statistics:")
    stats = get_collection_stats(db)
    for collection, count in stats.items():
        print(f"  - {collection}: {count} documents")
    
    # Show entity breakdown
    print("\n📋 Entity breakdown:")
    entity_types = {}
    for entity in entities:
        etype = entity.get("entity_type", "unknown")
        entity_types[etype] = entity_types.get(etype, 0) + 1
    for etype, count in sorted(entity_types.items()):
        print(f"  - {etype}: {count}")
    
    # Show relationship breakdown
    print("\n🔗 Relationship breakdown:")
    rel_types = {}
    for rel in relationships:
        rtype = rel.get("relationship_type", "unknown")
        rel_types[rtype] = rel_types.get(rtype, 0) + 1
    for rtype, count in sorted(rel_types.items()):
        print(f"  - {rtype}: {count}")
    
    print("\n" + "=" * 60)
    print("🎉 Sample data loaded successfully!")
    print("\n⚠️  REMINDER: Create Vector Search Index in Atlas UI if not done yet")
    print("   See config/atlas_indexes.json for index definitions")
    print("=" * 60)


if __name__ == "__main__":
    main()

