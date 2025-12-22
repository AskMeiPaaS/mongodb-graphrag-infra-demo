#!/usr/bin/env python3
"""
Database Setup Script
Creates collections and indexes for the infrastructure knowledge graph
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db, create_indexes, clear_collections, get_collection_stats


def main():
    print("=" * 60)
    print("MongoDB Infrastructure Knowledge Graph - Database Setup")
    print("=" * 60)
    
    # Connect to database
    print("\n📡 Connecting to MongoDB Atlas...")
    db = get_db()
    
    # Check current state
    print("\n📊 Current collection statistics:")
    stats = get_collection_stats(db)
    for collection, count in stats.items():
        print(f"  - {collection}: {count} documents")
    
    # Ask for confirmation if data exists
    if any(count > 0 for count in stats.values()):
        response = input("\n⚠️  Collections have existing data. Clear them? (y/N): ")
        if response.lower() == 'y':
            clear_collections(db)
        else:
            print("Keeping existing data.")
    
    # Create indexes
    print("\n📇 Creating indexes...")
    create_indexes(db)
    
    # Final stats
    print("\n✅ Database setup complete!")
    print("\n📊 Final collection statistics:")
    stats = get_collection_stats(db)
    for collection, count in stats.items():
        print(f"  - {collection}: {count} documents")
    
    print("\n🔔 IMPORTANT: Create Vector Search Index manually in Atlas UI")
    print("   Navigate to: Database > Search > Create Search Index > JSON Editor")
    print("   Use the index definition from config/atlas_indexes.json")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

