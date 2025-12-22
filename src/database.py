"""
MongoDB Atlas Database Connection and Operations
"""

import os
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()


class MongoDBConnection:
    """Singleton MongoDB connection manager"""
    
    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB Atlas"""
        uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGODB_DATABASE", "infrastructure_kg")
        
        if not uri:
            raise ValueError("MONGODB_URI environment variable is required")
        
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        
        # Test connection
        self._client.admin.command('ping')
        print(f"✅ Connected to MongoDB Atlas - Database: {db_name}")
    
    @property
    def client(self) -> MongoClient:
        return self._client
    
    @property
    def db(self) -> Database:
        return self._db
    
    @property
    def entities(self) -> Collection:
        return self._db["entities"]
    
    @property
    def relationships(self) -> Collection:
        return self._db["relationships"]
    
    @property
    def firewall_rules(self) -> Collection:
        return self._db["firewall_rules"]
    
    def close(self):
        """Close the MongoDB connection"""
        if self._client:
            self._client.close()
            print("🔌 MongoDB connection closed")


def get_db() -> MongoDBConnection:
    """Get MongoDB connection instance"""
    return MongoDBConnection()


def create_indexes(db: MongoDBConnection):
    """Create required indexes for graph queries"""
    
    # Entity indexes
    db.entities.create_index([("entity_type", 1)])
    db.entities.create_index([("name", 1)], unique=True)
    db.entities.create_index([("properties.criticality", 1)])
    db.entities.create_index([("properties.compliance_tags", 1)])
    
    # Relationship indexes for graph traversal
    db.relationships.create_index([("source.entity_id", 1)])
    db.relationships.create_index([("target.entity_id", 1)])
    db.relationships.create_index([("relationship_type", 1)])
    db.relationships.create_index([
        ("source.entity_id", 1),
        ("target.entity_id", 1),
        ("relationship_type", 1)
    ])
    
    # Firewall rules indexes
    db.firewall_rules.create_index([("firewall", 1)])
    db.firewall_rules.create_index([("source_zone", 1), ("destination_zone", 1)])
    db.firewall_rules.create_index([("rule_id", 1)], unique=True)
    
    print("✅ Database indexes created successfully")


def clear_collections(db: MongoDBConnection):
    """Clear all collections (for reset)"""
    db.entities.delete_many({})
    db.relationships.delete_many({})
    db.firewall_rules.delete_many({})
    print("🗑️ All collections cleared")


def insert_entities(db: MongoDBConnection, entities: List[Dict[str, Any]]):
    """Insert entities into the database"""
    if entities:
        result = db.entities.insert_many(entities)
        print(f"📥 Inserted {len(result.inserted_ids)} entities")
        return result.inserted_ids
    return []


def insert_relationships(db: MongoDBConnection, relationships: List[Dict[str, Any]]):
    """Insert relationships into the database"""
    if relationships:
        result = db.relationships.insert_many(relationships)
        print(f"📥 Inserted {len(result.inserted_ids)} relationships")
        return result.inserted_ids
    return []


def insert_firewall_rules(db: MongoDBConnection, rules: List[Dict[str, Any]]):
    """Insert firewall rules into the database"""
    if rules:
        result = db.firewall_rules.insert_many(rules)
        print(f"📥 Inserted {len(result.inserted_ids)} firewall rules")
        return result.inserted_ids
    return []


def get_entity_by_name(db: MongoDBConnection, name: str) -> Optional[Dict[str, Any]]:
    """Get entity by name"""
    return db.entities.find_one({"name": name})


def get_entity_by_id(db: MongoDBConnection, entity_id) -> Optional[Dict[str, Any]]:
    """Get entity by ID"""
    return db.entities.find_one({"_id": entity_id})


def get_entities_by_type(db: MongoDBConnection, entity_type: str) -> List[Dict[str, Any]]:
    """Get all entities of a specific type"""
    return list(db.entities.find({"entity_type": entity_type}))


def get_relationships_for_entity(db: MongoDBConnection, entity_id) -> List[Dict[str, Any]]:
    """Get all relationships where entity is source or target"""
    return list(db.relationships.find({
        "$or": [
            {"source.entity_id": entity_id},
            {"target.entity_id": entity_id}
        ]
    }))


def get_collection_stats(db: MongoDBConnection) -> Dict[str, int]:
    """Get document counts for all collections"""
    return {
        "entities": db.entities.count_documents({}),
        "relationships": db.relationships.count_documents({}),
        "firewall_rules": db.firewall_rules.count_documents({})
    }

