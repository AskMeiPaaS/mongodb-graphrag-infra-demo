"""
Graph Traversal Queries using MongoDB Aggregation Pipeline
"""

from typing import List, Dict, Any, Optional
from bson import ObjectId


def vector_search_entities(
    db,
    query_embedding: List[float],
    limit: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Perform vector search on entities collection
    
    Args:
        db: MongoDB database connection
        query_embedding: Query vector
        limit: Maximum number of results
        filters: Optional filters (e.g., {"entity_type": "server"})
    """
    pipeline = [
        {
            "$vectorSearch": {
                "index": "entities_vector_index",
                "path": "description_embedding",
                "queryVector": query_embedding,
                "numCandidates": limit * 20,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 1,
                "entity_type": 1,
                "name": 1,
                "properties": 1,
                "description": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    # Add filter stage if provided
    if filters:
        pipeline.insert(1, {"$match": filters})
    
    return list(db.entities.aggregate(pipeline))


def get_downstream_dependencies(
    db,
    entity_id: ObjectId,
    max_depth: int = 3,
    relationship_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Find all downstream dependencies of an entity using $graphLookup
    
    This answers: "What depends on this entity?"
    """
    if relationship_types is None:
        relationship_types = ["DEPENDS_ON", "CONNECTS_TO", "RUNS_ON", "ROUTES_TO"]
    
    pipeline = [
        # Start with relationships where our entity is the target (things that depend on it)
        {
            "$match": {
                "target.entity_id": entity_id,
                "relationship_type": {"$in": relationship_types}
            }
        },
        # Recursively find downstream dependencies
        {
            "$graphLookup": {
                "from": "relationships",
                "startWith": "$source.entity_id",
                "connectFromField": "source.entity_id",
                "connectToField": "target.entity_id",
                "as": "dependency_chain",
                "maxDepth": max_depth,
                "depthField": "depth",
                "restrictSearchWithMatch": {
                    "relationship_type": {"$in": relationship_types}
                }
            }
        },
        # Lookup source entity details
        {
            "$lookup": {
                "from": "entities",
                "localField": "source.entity_id",
                "foreignField": "_id",
                "as": "source_entity"
            }
        },
        {
            "$unwind": "$source_entity"
        },
        # Project useful fields
        {
            "$project": {
                "relationship_type": 1,
                "source": 1,
                "target": 1,
                "properties": 1,
                "source_entity": {
                    "name": 1,
                    "entity_type": 1,
                    "properties.criticality": 1,
                    "properties.compliance_tags": 1,
                    "description": 1
                },
                "dependency_chain": 1
            }
        }
    ]
    
    return list(db.relationships.aggregate(pipeline))


def get_upstream_dependencies(
    db,
    entity_id: ObjectId,
    max_depth: int = 3,
    relationship_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Find all upstream dependencies of an entity
    
    This answers: "What does this entity depend on?"
    """
    if relationship_types is None:
        relationship_types = ["DEPENDS_ON", "CONNECTS_TO", "RUNS_ON", "ROUTES_TO"]
    
    pipeline = [
        # Start with relationships where our entity is the source (things it depends on)
        {
            "$match": {
                "source.entity_id": entity_id,
                "relationship_type": {"$in": relationship_types}
            }
        },
        # Recursively find upstream dependencies
        {
            "$graphLookup": {
                "from": "relationships",
                "startWith": "$target.entity_id",
                "connectFromField": "target.entity_id",
                "connectToField": "source.entity_id",
                "as": "upstream_chain",
                "maxDepth": max_depth,
                "depthField": "depth",
                "restrictSearchWithMatch": {
                    "relationship_type": {"$in": relationship_types}
                }
            }
        },
        # Lookup target entity details
        {
            "$lookup": {
                "from": "entities",
                "localField": "target.entity_id",
                "foreignField": "_id",
                "as": "target_entity"
            }
        },
        {
            "$unwind": "$target_entity"
        },
        {
            "$project": {
                "relationship_type": 1,
                "source": 1,
                "target": 1,
                "properties": 1,
                "target_entity": {
                    "name": 1,
                    "entity_type": 1,
                    "properties.criticality": 1,
                    "properties.compliance_tags": 1,
                    "description": 1
                },
                "upstream_chain": 1
            }
        }
    ]
    
    return list(db.relationships.aggregate(pipeline))


def get_impact_analysis(
    db,
    entity_name: str,
    max_depth: int = 5
) -> Dict[str, Any]:
    """
    Comprehensive impact analysis for an entity
    
    Returns entities grouped by impact level (hops away)
    """
    # First get the entity
    entity = db.entities.find_one({"name": entity_name})
    if not entity:
        return {"error": f"Entity {entity_name} not found"}
    
    entity_id = entity["_id"]
    
    pipeline = [
        # Find all relationships where this entity is target or source
        {
            "$match": {
                "$or": [
                    {"target.entity_id": entity_id},
                    {"source.entity_id": entity_id}
                ]
            }
        },
        # Graph lookup for multi-hop impact
        {
            "$graphLookup": {
                "from": "relationships",
                "startWith": "$source.entity_id",
                "connectFromField": "source.entity_id",
                "connectToField": "target.entity_id",
                "as": "impact_path",
                "maxDepth": max_depth,
                "depthField": "impact_level"
            }
        },
        # Unwind the impact path
        {"$unwind": {"path": "$impact_path", "preserveNullAndEmptyArrays": True}},
        # Lookup impacted entity details
        {
            "$lookup": {
                "from": "entities",
                "localField": "impact_path.source.entity_id",
                "foreignField": "_id",
                "as": "impacted_entity"
            }
        },
        # Group by impact level
        {
            "$group": {
                "_id": "$impact_path.impact_level",
                "affected_entities": {
                    "$addToSet": {
                        "name": {"$arrayElemAt": ["$impacted_entity.name", 0]},
                        "type": {"$arrayElemAt": ["$impacted_entity.entity_type", 0]},
                        "criticality": {"$arrayElemAt": ["$impacted_entity.properties.criticality", 0]},
                        "relationship": "$impact_path.relationship_type"
                    }
                }
            }
        },
        {"$sort": {"_id": 1}},
        # Filter out nulls
        {"$match": {"_id": {"$ne": None}}}
    ]
    
    impact_results = list(db.relationships.aggregate(pipeline))
    
    # Also get direct relationships
    direct_relationships = list(db.relationships.find({
        "$or": [
            {"target.entity_id": entity_id},
            {"source.entity_id": entity_id}
        ]
    }))
    
    return {
        "entity": {
            "name": entity["name"],
            "type": entity["entity_type"],
            "criticality": entity.get("properties", {}).get("criticality"),
            "description": entity.get("description")
        },
        "direct_relationships": direct_relationships,
        "impact_by_level": impact_results
    }


def find_network_paths(
    db,
    source_zone: str,
    destination_zone: str,
    include_deny_rules: bool = False
) -> List[Dict[str, Any]]:
    """
    Find all firewall rules and network paths between security zones
    """
    match_criteria = {
        "source_zone": source_zone,
        "destination_zone": destination_zone,
        "enabled": True
    }
    
    if not include_deny_rules:
        match_criteria["action"] = "allow"
    
    pipeline = [
        {"$match": match_criteria},
        # Lookup firewall details
        {
            "$lookup": {
                "from": "entities",
                "localField": "firewall",
                "foreignField": "name",
                "as": "firewall_details"
            }
        },
        # Project relevant fields
        {
            "$project": {
                "rule_id": 1,
                "name": 1,
                "firewall": 1,
                "source_zone": 1,
                "destination_zone": 1,
                "source_addresses": 1,
                "destination_addresses": 1,
                "services": 1,
                "action": 1,
                "description": 1,
                "compliance_notes": 1,
                "hit_count": 1,
                "firewall_details": {"$arrayElemAt": ["$firewall_details", 0]}
            }
        },
        {"$sort": {"hit_count": -1}}
    ]
    
    return list(db.firewall_rules.aggregate(pipeline))


def get_compliance_scope(
    db,
    compliance_tag: str
) -> Dict[str, Any]:
    """
    Get all entities and rules within a compliance scope (e.g., PCI-DSS)
    """
    # Get entities with this compliance tag
    entities = list(db.entities.find({
        "properties.compliance_tags": compliance_tag
    }, {
        "name": 1,
        "entity_type": 1,
        "properties.criticality": 1,
        "properties.data_classification": 1,
        "description": 1
    }))
    
    # Get firewall rules with this compliance requirement
    rules = list(db.firewall_rules.find({
        "$or": [
            {"compliance_notes": {"$regex": compliance_tag, "$options": "i"}},
            {"properties.compliance_tags": compliance_tag}
        ]
    }, {
        "rule_id": 1,
        "name": 1,
        "firewall": 1,
        "source_zone": 1,
        "destination_zone": 1,
        "action": 1,
        "compliance_notes": 1
    }))
    
    # Get relationships between compliance-scoped entities
    entity_ids = [e["_id"] for e in entities]
    relationships = list(db.relationships.find({
        "$or": [
            {"source.entity_id": {"$in": entity_ids}},
            {"target.entity_id": {"$in": entity_ids}}
        ]
    }))
    
    return {
        "compliance_tag": compliance_tag,
        "entity_count": len(entities),
        "rule_count": len(rules),
        "relationship_count": len(relationships),
        "entities": entities,
        "firewall_rules": rules,
        "relationships": relationships
    }


def get_entity_neighborhood(
    db,
    entity_id: ObjectId,
    hops: int = 1
) -> Dict[str, Any]:
    """
    Get the neighborhood of an entity (all connected entities within N hops)
    """
    pipeline = [
        {"$match": {"_id": entity_id}},
        {
            "$graphLookup": {
                "from": "relationships",
                "startWith": "$_id",
                "connectFromField": "target.entity_id",
                "connectToField": "source.entity_id",
                "as": "outbound_connections",
                "maxDepth": hops,
                "depthField": "distance"
            }
        },
        {
            "$graphLookup": {
                "from": "relationships",
                "startWith": "$_id",
                "connectFromField": "source.entity_id",
                "connectToField": "target.entity_id",
                "as": "inbound_connections",
                "maxDepth": hops,
                "depthField": "distance"
            }
        }
    ]
    
    result = list(db.entities.aggregate(pipeline))
    if result:
        return result[0]
    return {}


def search_entities_hybrid(
    db,
    query_embedding: List[float],
    text_query: str,
    limit: int = 10,
    vector_weight: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Hybrid search combining vector similarity and text search
    
    Note: Requires Atlas Search index with both vector and text fields
    """
    pipeline = [
        {
            "$vectorSearch": {
                "index": "entities_vector_index",
                "path": "description_embedding",
                "queryVector": query_embedding,
                "numCandidates": limit * 20,
                "limit": limit * 2  # Get more for re-ranking
            }
        },
        {
            "$addFields": {
                "vector_score": {"$meta": "vectorSearchScore"}
            }
        },
        # Text match scoring (simple regex for demo - use Atlas Search in production)
        {
            "$addFields": {
                "text_match": {
                    "$cond": {
                        "if": {
                            "$regexMatch": {
                                "input": {"$ifNull": ["$description", ""]},
                                "regex": text_query,
                                "options": "i"
                            }
                        },
                        "then": 1,
                        "else": 0
                    }
                }
            }
        },
        # Compute hybrid score
        {
            "$addFields": {
                "hybrid_score": {
                    "$add": [
                        {"$multiply": ["$vector_score", vector_weight]},
                        {"$multiply": ["$text_match", 1 - vector_weight]}
                    ]
                }
            }
        },
        {"$sort": {"hybrid_score": -1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 1,
                "entity_type": 1,
                "name": 1,
                "properties": 1,
                "description": 1,
                "vector_score": 1,
                "text_match": 1,
                "hybrid_score": 1
            }
        }
    ]
    
    return list(db.entities.aggregate(pipeline))

