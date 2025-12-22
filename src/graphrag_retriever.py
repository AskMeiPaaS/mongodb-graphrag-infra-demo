"""
Custom LangChain Retriever for Infrastructure GraphRAG
"""

import json
from typing import List, Dict, Any, Optional
from langchain.schema import BaseRetriever, Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from pydantic import Field

from .embeddings import EmbeddingGenerator
from .graph_queries import (
    vector_search_entities,
    get_downstream_dependencies,
    get_upstream_dependencies,
    find_network_paths,
    get_compliance_scope
)


class InfrastructureGraphRAGRetriever(BaseRetriever):
    """
    Custom retriever that combines:
    1. Vector search for semantic similarity
    2. Graph traversal for relationship context
    3. Firewall rule lookup for network paths
    """
    
    db: Any = Field(description="MongoDB database connection")
    embedding_generator: Any = Field(description="Embedding generator instance")
    vector_search_limit: int = Field(default=5, description="Number of vector search results")
    graph_depth: int = Field(default=3, description="Maximum graph traversal depth")
    include_firewall_rules: bool = Field(default=True, description="Include firewall rules in context")
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents for the query
        
        Strategy:
        1. Vector search to find semantically similar entities
        2. Graph traversal to get related entities
        3. Firewall rules lookup if network/security related
        4. Compliance scope if compliance mentioned
        """
        documents = []
        
        # Step 1: Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Step 2: Vector search for relevant entities
        vector_results = vector_search_entities(
            self.db.db,
            query_embedding,
            limit=self.vector_search_limit
        )
        
        if vector_results:
            # Format seed entities
            seed_entities_text = self._format_entities(vector_results)
            documents.append(Document(
                page_content=f"## Primary Entities (Vector Search Results):\n{seed_entities_text}",
                metadata={"source": "vector_search", "count": len(vector_results)}
            ))
            
            # Step 3: Graph traversal for each seed entity
            all_downstream = []
            all_upstream = []
            
            for entity in vector_results[:3]:  # Limit graph queries to top 3
                entity_id = entity["_id"]
                
                # Get downstream (what depends on this)
                downstream = get_downstream_dependencies(
                    self.db.db,
                    entity_id,
                    max_depth=self.graph_depth
                )
                all_downstream.extend(downstream)
                
                # Get upstream (what this depends on)
                upstream = get_upstream_dependencies(
                    self.db.db,
                    entity_id,
                    max_depth=self.graph_depth
                )
                all_upstream.extend(upstream)
            
            if all_downstream:
                downstream_text = self._format_relationships(all_downstream, "downstream")
                documents.append(Document(
                    page_content=f"## Downstream Dependencies (What depends on these entities):\n{downstream_text}",
                    metadata={"source": "graph_downstream", "count": len(all_downstream)}
                ))
            
            if all_upstream:
                upstream_text = self._format_relationships(all_upstream, "upstream")
                documents.append(Document(
                    page_content=f"## Upstream Dependencies (What these entities depend on):\n{upstream_text}",
                    metadata={"source": "graph_upstream", "count": len(all_upstream)}
                ))
        
        # Step 4: Check for network/firewall related queries
        if self.include_firewall_rules and self._is_network_query(query):
            firewall_docs = self._get_firewall_context(query)
            documents.extend(firewall_docs)
        
        # Step 5: Check for compliance queries
        compliance_tag = self._extract_compliance_tag(query)
        if compliance_tag:
            compliance_scope = get_compliance_scope(self.db.db, compliance_tag)
            compliance_text = self._format_compliance_scope(compliance_scope)
            documents.append(Document(
                page_content=f"## {compliance_tag} Compliance Scope:\n{compliance_text}",
                metadata={"source": "compliance", "tag": compliance_tag}
            ))
        
        return documents
    
    def _format_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Format entities for context"""
        formatted = []
        for entity in entities:
            props = entity.get("properties", {})
            entry = f"""
### {entity.get('name', 'Unknown')} ({entity.get('entity_type', 'unknown')})
- **Criticality**: {props.get('criticality', 'N/A')}
- **Compliance Tags**: {', '.join(props.get('compliance_tags', [])) or 'N/A'}
- **Data Classification**: {props.get('data_classification', 'N/A')}
- **Owner**: {props.get('owner', 'N/A')}
- **Description**: {entity.get('description', 'No description')}
- **Vector Score**: {entity.get('score', 'N/A'):.4f}
"""
            formatted.append(entry)
        return "\n".join(formatted)
    
    def _format_relationships(self, relationships: List[Dict[str, Any]], direction: str) -> str:
        """Format relationships for context"""
        formatted = []
        seen = set()
        
        for rel in relationships:
            source = rel.get("source", {})
            target = rel.get("target", {})
            rel_type = rel.get("relationship_type", "RELATED_TO")
            
            # Dedup
            key = f"{source.get('name')}-{rel_type}-{target.get('name')}"
            if key in seen:
                continue
            seen.add(key)
            
            if direction == "downstream":
                entity_info = rel.get("source_entity", {})
                entry = f"- **{source.get('name')}** --[{rel_type}]--> {target.get('name')}"
            else:
                entity_info = rel.get("target_entity", {})
                entry = f"- {source.get('name')} --[{rel_type}]--> **{target.get('name')}**"
            
            if entity_info:
                entry += f"\n  - Type: {entity_info.get('entity_type', 'N/A')}"
                entry += f"\n  - Criticality: {entity_info.get('properties', {}).get('criticality', 'N/A')}"
            
            formatted.append(entry)
        
        return "\n".join(formatted) if formatted else "No relationships found."
    
    def _is_network_query(self, query: str) -> bool:
        """Check if query is network/firewall related"""
        network_keywords = [
            "firewall", "network", "traffic", "port", "rule", "acl",
            "zone", "dmz", "path", "route", "allow", "deny", "block",
            "connection", "protocol", "inbound", "outbound"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in network_keywords)
    
    def _get_firewall_context(self, query: str) -> List[Document]:
        """Get relevant firewall rules based on query"""
        documents = []
        
        # Check for zone-to-zone queries
        zones = ["dmz", "external", "internal", "web-tier", "app-tier", "db-tier"]
        mentioned_zones = [z for z in zones if z in query.lower()]
        
        if len(mentioned_zones) >= 2:
            # Find paths between mentioned zones
            for i, source_zone in enumerate(mentioned_zones):
                for target_zone in mentioned_zones[i+1:]:
                    paths = find_network_paths(self.db.db, source_zone, target_zone)
                    if paths:
                        paths_text = self._format_firewall_rules(paths)
                        documents.append(Document(
                            page_content=f"## Firewall Rules: {source_zone} → {target_zone}:\n{paths_text}",
                            metadata={"source": "firewall_rules", "zones": f"{source_zone}->{target_zone}"}
                        ))
        
        # Also do vector search on firewall rules
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "firewall_vector_index",
                    "path": "description_embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 50,
                    "limit": 5
                }
            },
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
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        try:
            firewall_results = list(self.db.db.firewall_rules.aggregate(pipeline))
            if firewall_results:
                rules_text = self._format_firewall_rules(firewall_results)
                documents.append(Document(
                    page_content=f"## Relevant Firewall Rules (Semantic Search):\n{rules_text}",
                    metadata={"source": "firewall_vector_search", "count": len(firewall_results)}
                ))
        except Exception as e:
            # Vector index might not exist
            pass
        
        return documents
    
    def _format_firewall_rules(self, rules: List[Dict[str, Any]]) -> str:
        """Format firewall rules for context"""
        formatted = []
        for rule in rules:
            services = rule.get("services", [])
            services_str = ", ".join([
                f"{s.get('protocol', 'any')}:{s.get('port', 'any')}" 
                for s in services
            ]) if services else "any"
            
            entry = f"""
### {rule.get('rule_id', 'Unknown')} - {rule.get('name', 'Unnamed')}
- **Firewall**: {rule.get('firewall', 'N/A')}
- **Direction**: {rule.get('source_zone', 'any')} → {rule.get('destination_zone', 'any')}
- **Source**: {', '.join(rule.get('source_addresses', ['any']))}
- **Destination**: {', '.join(rule.get('destination_addresses', ['any']))}
- **Services**: {services_str}
- **Action**: {rule.get('action', 'N/A').upper()}
- **Description**: {rule.get('description', 'No description')}
- **Compliance**: {rule.get('compliance_notes', 'N/A')}
"""
            formatted.append(entry)
        return "\n".join(formatted)
    
    def _extract_compliance_tag(self, query: str) -> Optional[str]:
        """Extract compliance framework from query"""
        compliance_tags = {
            "pci": "PCI-DSS",
            "pci-dss": "PCI-DSS",
            "pci dss": "PCI-DSS",
            "sox": "SOX",
            "sarbanes": "SOX",
            "glba": "GLBA",
            "gramm-leach": "GLBA"
        }
        
        query_lower = query.lower()
        for keyword, tag in compliance_tags.items():
            if keyword in query_lower:
                return tag
        return None
    
    def _format_compliance_scope(self, scope: Dict[str, Any]) -> str:
        """Format compliance scope for context"""
        lines = [
            f"**Compliance Framework**: {scope.get('compliance_tag', 'N/A')}",
            f"**Total Entities in Scope**: {scope.get('entity_count', 0)}",
            f"**Firewall Rules**: {scope.get('rule_count', 0)}",
            f"**Relationships**: {scope.get('relationship_count', 0)}",
            "\n**Key Entities**:"
        ]
        
        for entity in scope.get("entities", [])[:10]:  # Limit to 10
            lines.append(f"- {entity.get('name', 'Unknown')} ({entity.get('entity_type', 'unknown')})")
        
        if scope.get("entity_count", 0) > 10:
            lines.append(f"- ... and {scope.get('entity_count', 0) - 10} more")
        
        return "\n".join(lines)

