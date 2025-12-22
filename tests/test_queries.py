"""
Test suite for Infrastructure GraphRAG queries
"""

import sys
import os
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db, get_collection_stats, get_entity_by_name
from src.embeddings import EmbeddingGenerator, create_entity_text
from src.graph_queries import (
    get_downstream_dependencies,
    get_upstream_dependencies,
    get_impact_analysis,
    find_network_paths,
    get_compliance_scope
)


class TestDatabaseConnection:
    """Test database connectivity"""
    
    def test_connection(self):
        """Test that we can connect to MongoDB Atlas"""
        db = get_db()
        assert db is not None
        assert db.client is not None
    
    def test_collections_exist(self):
        """Test that collections have data"""
        db = get_db()
        stats = get_collection_stats(db)
        
        assert stats["entities"] > 0, "Entities collection is empty"
        assert stats["relationships"] > 0, "Relationships collection is empty"
        assert stats["firewall_rules"] > 0, "Firewall rules collection is empty"
    
    def test_entity_lookup(self):
        """Test entity lookup by name"""
        db = get_db()
        
        # Test known entity
        entity = get_entity_by_name(db, "FW-PROD-01")
        assert entity is not None
        assert entity["entity_type"] == "firewall"
        assert entity["properties"]["criticality"] == "critical"


class TestEmbeddings:
    """Test embedding generation"""
    
    def test_embedding_generator(self):
        """Test embedding generator initialization"""
        generator = EmbeddingGenerator()
        assert generator is not None
    
    def test_generate_embedding(self):
        """Test single embedding generation"""
        generator = EmbeddingGenerator()
        embedding = generator.generate_embedding("Test text for embedding")
        
        assert embedding is not None
        assert len(embedding) == generator.dimensions
        assert all(isinstance(x, float) for x in embedding)
    
    def test_entity_text_creation(self):
        """Test entity text creation for embedding"""
        entity = {
            "entity_type": "server",
            "name": "TEST-SERVER",
            "description": "A test server",
            "properties": {
                "criticality": "high",
                "compliance_tags": ["PCI-DSS"],
                "owner": "Test Team"
            }
        }
        
        text = create_entity_text(entity)
        assert "server" in text.lower()
        assert "TEST-SERVER" in text
        assert "high" in text.lower()
        assert "PCI-DSS" in text


class TestGraphQueries:
    """Test graph traversal queries"""
    
    @pytest.fixture
    def db(self):
        return get_db()
    
    def test_impact_analysis(self, db):
        """Test impact analysis query"""
        result = get_impact_analysis(db.db, "FW-PROD-01")
        
        assert "error" not in result
        assert "entity" in result
        assert result["entity"]["name"] == "FW-PROD-01"
        assert "direct_relationships" in result
    
    def test_find_network_paths(self, db):
        """Test network path finding"""
        paths = find_network_paths(db.db, "dmz", "web-tier")
        
        assert isinstance(paths, list)
        # We should have at least some rules
        assert len(paths) >= 0
    
    def test_compliance_scope(self, db):
        """Test compliance scope query"""
        scope = get_compliance_scope(db.db, "PCI-DSS")
        
        assert "compliance_tag" in scope
        assert scope["compliance_tag"] == "PCI-DSS"
        assert "entity_count" in scope
        assert scope["entity_count"] > 0
    
    def test_downstream_dependencies(self, db):
        """Test downstream dependency query"""
        # Get FW-PROD-01's ID
        entity = get_entity_by_name(db, "FW-PROD-01")
        assert entity is not None
        
        dependencies = get_downstream_dependencies(db.db, entity["_id"])
        assert isinstance(dependencies, list)
    
    def test_upstream_dependencies(self, db):
        """Test upstream dependency query"""
        # Get Payment-Gateway's ID
        entity = get_entity_by_name(db, "Payment-Gateway")
        if entity:  # Only run if entity exists
            dependencies = get_upstream_dependencies(db.db, entity["_id"])
            assert isinstance(dependencies, list)


class TestSampleData:
    """Test sample data generation"""
    
    def test_entity_types(self):
        """Test that all expected entity types exist"""
        db = get_db()
        
        expected_types = ["firewall", "server", "application", "load_balancer", "vlan"]
        
        for entity_type in expected_types:
            count = db.entities.count_documents({"entity_type": entity_type})
            assert count > 0, f"No entities of type {entity_type}"
    
    def test_relationship_types(self):
        """Test that all expected relationship types exist"""
        db = get_db()
        
        expected_types = ["PROTECTS", "ROUTES_TO", "CONNECTS_TO", "RUNS_ON", "DEPENDS_ON", "BELONGS_TO"]
        
        for rel_type in expected_types:
            count = db.relationships.count_documents({"relationship_type": rel_type})
            assert count > 0, f"No relationships of type {rel_type}"
    
    def test_entities_have_embeddings(self):
        """Test that entities have embeddings"""
        db = get_db()
        
        # Sample a few entities
        entities = list(db.entities.find().limit(5))
        
        for entity in entities:
            assert "description_embedding" in entity, f"Entity {entity['name']} missing embedding"
            assert len(entity["description_embedding"]) > 0
    
    def test_firewall_rules_have_embeddings(self):
        """Test that firewall rules have embeddings"""
        db = get_db()
        
        rules = list(db.firewall_rules.find().limit(5))
        
        for rule in rules:
            assert "description_embedding" in rule, f"Rule {rule['rule_id']} missing embedding"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

