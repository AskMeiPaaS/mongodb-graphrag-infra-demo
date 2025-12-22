"""
GraphRAG Chain - Main entry point for infrastructure Q&A
"""

import os
from typing import Dict, Any, Optional
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

from .database import get_db
from .embeddings import EmbeddingGenerator
from .graphrag_retriever import InfrastructureGraphRAGRetriever

load_dotenv()


# Infrastructure-specific prompt template
INFRASTRUCTURE_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert infrastructure analyst at a major financial institution. 
Your role is to analyze the bank's infrastructure knowledge graph and provide accurate, 
detailed answers about networking, firewalls, servers, applications, and security policies.

INFRASTRUCTURE KNOWLEDGE GRAPH CONTEXT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Analyze the provided context carefully
2. Identify all relevant entities, relationships, and firewall rules
3. Consider security implications and compliance requirements
4. Provide specific, actionable information

Your response should include:
- Direct answer to the question
- Relevant entities and their relationships
- Security/compliance considerations if applicable
- Impact assessment if the question involves changes or failures
- Specific technical details (IPs, ports, rules) when relevant

If the context doesn't contain enough information to fully answer the question, 
clearly state what information is missing and what you can infer from available data.

ANSWER:"""
)


IMPACT_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert infrastructure analyst specializing in impact analysis 
and change management at a major financial institution.

INFRASTRUCTURE KNOWLEDGE GRAPH CONTEXT:
{context}

USER QUESTION: {question}

Provide a comprehensive impact analysis including:

1. **Directly Affected Components**:
   - List all systems that would be immediately impacted
   - Specify the type of impact (connectivity, availability, data flow)

2. **Cascade Effects**:
   - Identify downstream dependencies
   - Applications and services that would lose functionality
   - User-facing impacts

3. **Criticality Assessment**:
   - Rate overall impact: Critical/High/Medium/Low
   - Identify Tier-1 (critical) applications affected
   - Compliance implications (PCI-DSS, SOX, etc.)

4. **Mitigation Recommendations**:
   - Failover options available
   - Recommended maintenance windows
   - Pre-requisite changes or notifications needed

5. **Recovery Considerations**:
   - Expected recovery time
   - Validation steps after restoration

Be specific about entity names, IP addresses, and relationship types.

IMPACT ANALYSIS:"""
)


def create_graphrag_chain(
    prompt_type: str = "default",
    vector_search_limit: int = 5,
    graph_depth: int = 3
) -> RetrievalQA:
    """
    Create the GraphRAG chain for infrastructure Q&A
    
    Args:
        prompt_type: "default" or "impact" for different prompt templates
        vector_search_limit: Number of vector search results
        graph_depth: Maximum graph traversal depth
    """
    # Initialize components
    db = get_db()
    embedding_generator = EmbeddingGenerator()
    
    # Create retriever
    retriever = InfrastructureGraphRAGRetriever(
        db=db,
        embedding_generator=embedding_generator,
        vector_search_limit=vector_search_limit,
        graph_depth=graph_depth,
        include_firewall_rules=True
    )
    
    # Select prompt
    prompt = IMPACT_ANALYSIS_PROMPT if prompt_type == "impact" else INFRASTRUCTURE_PROMPT
    
    # Create LLM
    llm = ChatAnthropic(
        model_name=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        temperature=0,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Create chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    
    return chain


def query_infrastructure(
    question: str,
    prompt_type: str = "default",
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Query the infrastructure knowledge graph
    
    Args:
        question: The question to ask
        prompt_type: "default" for general queries, "impact" for impact analysis
        verbose: Whether to print debug information
    """
    chain = create_graphrag_chain(prompt_type=prompt_type)
    
    if verbose:
        print(f"\n🔍 Query: {question}")
        print("-" * 60)
    
    result = chain.invoke({"query": question})
    
    if verbose:
        print(f"\n📊 Retrieved {len(result.get('source_documents', []))} context documents")
        for doc in result.get("source_documents", []):
            print(f"  - {doc.metadata.get('source', 'unknown')}: {doc.metadata}")
    
    return {
        "question": question,
        "answer": result.get("result", "No answer generated"),
        "source_documents": result.get("source_documents", []),
        "prompt_type": prompt_type
    }


class InfrastructureAssistant:
    """
    High-level assistant for infrastructure queries
    """
    
    def __init__(self):
        self.db = get_db()
        self.embedding_generator = EmbeddingGenerator()
        self.default_chain = None
        self.impact_chain = None
    
    def _get_chain(self, prompt_type: str) -> RetrievalQA:
        """Lazy load chains"""
        if prompt_type == "impact":
            if self.impact_chain is None:
                self.impact_chain = create_graphrag_chain(prompt_type="impact")
            return self.impact_chain
        else:
            if self.default_chain is None:
                self.default_chain = create_graphrag_chain(prompt_type="default")
            return self.default_chain
    
    def ask(self, question: str, prompt_type: str = "auto") -> Dict[str, Any]:
        """
        Ask a question about the infrastructure
        
        Args:
            question: The question to ask
            prompt_type: "auto" (detect), "default", or "impact"
        """
        # Auto-detect prompt type
        if prompt_type == "auto":
            impact_keywords = ["impact", "affect", "fail", "down", "maintenance", "change", "outage"]
            if any(kw in question.lower() for kw in impact_keywords):
                prompt_type = "impact"
            else:
                prompt_type = "default"
        
        chain = self._get_chain(prompt_type)
        result = chain.invoke({"query": question})
        
        return {
            "question": question,
            "answer": result.get("result", "No answer generated"),
            "source_documents": result.get("source_documents", []),
            "detected_prompt_type": prompt_type
        }
    
    def impact_analysis(self, entity_name: str) -> Dict[str, Any]:
        """
        Perform impact analysis for an entity
        
        Args:
            entity_name: Name of the entity to analyze
        """
        question = f"What would be the impact if {entity_name} goes offline or needs maintenance?"
        return self.ask(question, prompt_type="impact")
    
    def find_path(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Find network path between two components
        
        Args:
            source: Source entity/zone
            destination: Destination entity/zone
        """
        question = f"Show me all network paths and firewall rules between {source} and {destination}"
        return self.ask(question, prompt_type="default")
    
    def compliance_check(self, compliance_tag: str) -> Dict[str, Any]:
        """
        Get compliance scope information
        
        Args:
            compliance_tag: e.g., "PCI-DSS", "SOX"
        """
        question = f"List all infrastructure components that are in scope for {compliance_tag} compliance"
        return self.ask(question, prompt_type="default")
    
    def get_dependencies(self, entity_name: str) -> Dict[str, Any]:
        """
        Get dependencies for an entity
        
        Args:
            entity_name: Name of the entity
        """
        question = f"What are all the upstream and downstream dependencies of {entity_name}?"
        return self.ask(question, prompt_type="default")

