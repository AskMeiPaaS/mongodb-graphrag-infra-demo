"""
Streamlit UI for Infrastructure GraphRAG Demo
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.database import get_db, get_collection_stats, get_entities_by_type
from src.graphrag_chain import InfrastructureAssistant
from src.graph_queries import get_impact_analysis, find_network_paths, get_compliance_scope


# Page config
st.set_page_config(
    page_title="Infrastructure GraphRAG - MongoDB Atlas",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00684A;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_database():
    """Get cached database connection"""
    return get_db()


@st.cache_resource
def get_assistant():
    """Get cached assistant instance"""
    return InfrastructureAssistant()


def render_header():
    """Render page header"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<p class="main-header">🏦 Infrastructure GraphRAG</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Powered by MongoDB Atlas + LangChain</p>', unsafe_allow_html=True)
    with col2:
        st.image("https://webimages.mongodb.com/_com_assets/cms/kuyjf3vea2hg34taa-horizontal_default_slate_blue.svg", width=200)


def render_sidebar():
    """Render sidebar with stats and sample queries"""
    with st.sidebar:
        st.header("📊 Database Stats")
        
        try:
            db = get_database()
            stats = get_collection_stats(db)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Entities", stats.get("entities", 0))
            col2.metric("Relations", stats.get("relationships", 0))
            col3.metric("FW Rules", stats.get("firewall_rules", 0))
            
        except Exception as e:
            st.error(f"Database error: {e}")
        
        st.divider()
        
        st.header("💡 Sample Queries")
        
        sample_queries = {
            "Impact Analysis": [
                "What would happen if FW-PROD-01 fails?",
                "Impact of SRV-DB-003 maintenance"
            ],
            "Network Paths": [
                "Show firewall rules from DMZ to database",
                "Network path to Payment-Gateway"
            ],
            "Dependencies": [
                "Dependencies of Payment-Gateway",
                "What runs on SRV-APP-001?"
            ]            
        }
        
        for category, queries in sample_queries.items():
            with st.expander(category):
                for query in queries:
                    if st.button(query, key=f"sample_{query[:20]}"):
                        st.session_state.query = query


def render_chat_interface():
    """Render the main chat interface"""
    st.header("💬 Ask About Your Infrastructure")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'query' not in st.session_state:
        st.session_state.query = ""
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Query input
    query = st.chat_input("Ask a question about your infrastructure...")
    
    # Use sample query if selected
    if st.session_state.query:
        query = st.session_state.query
        st.session_state.query = ""
    
    if query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing infrastructure knowledge graph..."):
                try:
                    assistant = get_assistant()
                    result = assistant.ask(query)
                    response = result['answer']
                    
                    st.markdown(response)
                    
                    # Show context sources
                    with st.expander("📚 Context Sources"):
                        for doc in result.get('source_documents', []):
                            st.caption(f"**Source**: {doc.metadata.get('source', 'unknown')}")
                            st.text(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
                            st.divider()
                    
                except Exception as e:
                    response = f"Error processing query: {str(e)}"
                    st.error(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})


def render_topology_view():
    """Render infrastructure topology visualization"""
    st.header("🗺️ Infrastructure Topology")
    
    try:
        db = get_database()
        
        # Get all entities
        entities = list(db.entities.find({}, {"name": 1, "entity_type": 1, "properties": 1}))
        relationships = list(db.relationships.find({}, {"source": 1, "target": 1, "relationship_type": 1}))
        
        # Define layer hierarchy (top to bottom flow)
        layer_config = {
            "firewall": {"level": 0, "label": "🔥 Firewalls", "color": "#e74c3c"},
            "load_balancer": {"level": 1, "label": "⚖️ Load Balancers", "color": "#3498db"},
            "switch": {"level": 2, "label": "🔀 Switches", "color": "#9b59b6"},
            "vlan": {"level": 3, "label": "🌐 VLANs", "color": "#f39c12"},
            "server": {"level": 4, "label": "🖥️ Servers", "color": "#1abc9c"},
            "application": {"level": 5, "label": "📱 Applications", "color": "#2ecc71"}
        }
        
        # Group entities by layer
        entities_by_layer = {}
        for e in entities:
            entity_type = e["entity_type"]
            level = layer_config.get(entity_type, {}).get("level", 3)
            if level not in entities_by_layer:
                entities_by_layer[level] = []
            entities_by_layer[level].append(e)
        
        # Layout settings
        vertical_spacing = 5.0    # Space between layers vertically
        
        # Find the layer with most entities to determine the chart width
        max_entities_in_layer = max(len(ents) for ents in entities_by_layer.values()) if entities_by_layer else 1
        chart_width = max(max_entities_in_layer * 5, 40)  # Minimum width of 40 units
        
        # Calculate positions - spread entities evenly across the full width for each layer
        node_positions = {}
        
        for level, level_entities in entities_by_layer.items():
            count = len(level_entities)
            if count == 1:
                # Center single entity
                node_positions[str(level_entities[0]["_id"])] = (0, -level * vertical_spacing)
            else:
                # Spread evenly across the chart width
                spacing = chart_width / (count - 1) if count > 1 else 0
                for idx, e in enumerate(level_entities):
                    x = (idx * spacing) - (chart_width / 2)
                    y = -level * vertical_spacing
                    node_positions[str(e["_id"])] = (x, y)
        
        max_width = chart_width
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Add layer labels on the left side
        for entity_type, config in layer_config.items():
            level = config["level"]
            if level in entities_by_layer and entities_by_layer[level]:
                y_pos = -level * vertical_spacing
                fig.add_annotation(
                    x=-(max_width / 2) - 6,
                    y=y_pos,
                    text=config["label"],
                    showarrow=False,
                    font=dict(size=10, color="#444", family="Arial Black"),
                    xanchor="right"
                )
        
        # Add edges
        for rel in relationships:
            source_id = str(rel["source"]["entity_id"])
            target_id = str(rel["target"]["entity_id"])
            
            if source_id in node_positions and target_id in node_positions:
                x0, y0 = node_positions[source_id]
                x1, y1 = node_positions[target_id]
                
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=1.5, color='rgba(100, 100, 100, 0.6)'),
                    hoverinfo='none',
                    showlegend=False
                ))
        
        # Add nodes by type - 60px circles with fitted text
        for entity_type, config in layer_config.items():
            type_entities = [e for e in entities if e["entity_type"] == entity_type]
            if not type_entities:
                continue
            
            x_vals = [node_positions[str(e["_id"])][0] for e in type_entities]
            y_vals = [node_positions[str(e["_id"])][1] for e in type_entities]
            names = [e["name"] for e in type_entities]
            
            # Add 60px nodes
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers',
                marker=dict(
                    size=60,
                    color=config["color"],
                    line=dict(width=2, color='white'),
                    symbol='circle'
                ),
                name=entity_type.replace("_", " ").title(),
                hovertemplate="<b>%{customdata}</b><br><i>" + entity_type.replace("_", " ").title() + "</i><extra></extra>",
                customdata=names
            ))
            
            # Add text labels inside circles - split into 2-3 lines to fit
            for x, y, name in zip(x_vals, y_vals, names):
                # Split name into lines that fit in 60px circle (approx 8-10 chars per line)
                if "-" in name:
                    parts = name.split("-")
                    if len(parts) == 2:
                        display_name = f"{parts[0]}<br>{parts[1]}"
                    elif len(parts) == 3:
                        display_name = f"{parts[0]}<br>{parts[1]}<br>{parts[2]}"
                    else:
                        display_name = f"{parts[0]}<br>{'-'.join(parts[1:])}"
                elif len(name) > 10:
                    # Split long names without hyphens
                    mid = len(name) // 2
                    display_name = f"{name[:mid]}<br>{name[mid:]}"
                else:
                    display_name = name
                
                fig.add_annotation(
                    x=x,
                    y=y,
                    text=display_name,
                    showarrow=False,
                    font=dict(size=7, color="white", family="Arial"),
                    xanchor="center",
                    yanchor="middle"
                )
        
        # Add flow arrow
        fig.add_annotation(
            x=(max_width / 2) + 6,
            y=-2.5 * vertical_spacing,
            text="⬇️<br>Traffic<br>Flow",
            showarrow=False,
            font=dict(size=11, color="#666"),
            align="center"
        )
        
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            hovermode='closest',
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-(max_width / 2) - 10, (max_width / 2) + 10]
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-6 * vertical_spacing - 1, vertical_spacing + 1]
            ),
            height=800,
            title=dict(
                text="Infrastructure Topology",
                font=dict(size=16)
            ),
            plot_bgcolor='rgba(250, 250, 252, 1)',
            margin=dict(l=130, r=80, t=80, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Entity reference table below the graph
        st.subheader("📋 Entity Reference")
        st.caption("Full list of all infrastructure entities by type")
        
        # Create columns for each entity type
        cols = st.columns(3)
        col_idx = 0
        
        for entity_type, config in layer_config.items():
            type_entities = [e for e in entities if e["entity_type"] == entity_type]
            if type_entities:
                with cols[col_idx % 3]:
                    st.markdown(f"**{config['label']}**")
                    for e in type_entities:
                        st.markdown(f"<span style='color:{config['color']};'>●</span> {e['name']}", unsafe_allow_html=True)
                    st.write("")
                col_idx += 1
        
    except Exception as e:
        st.error(f"Error rendering topology: {e}")


def render_impact_analysis_view():
    """Render impact analysis interface"""
    st.header("⚡ Impact Analysis")
    
    try:
        db = get_database()
        
        # Get entity names for dropdown
        entities = list(db.entities.find({}, {"name": 1, "entity_type": 1}))
        entity_options = [f"{e['name']} ({e['entity_type']})" for e in entities]
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected = st.selectbox(
                "Select entity to analyze:",
                options=entity_options,
                index=0
            )
        
        with col2:
            analyze_btn = st.button("🔍 Analyze Impact", type="primary")
        
        if analyze_btn and selected:
            entity_name = selected.split(" (")[0]
            
            with st.spinner("Analyzing impact..."):
                assistant = get_assistant()
                result = assistant.impact_analysis(entity_name)
            
            st.markdown("### Analysis Results")
            st.markdown(result['answer'])
            
    except Exception as e:
        st.error(f"Error: {e}")


def render_compliance_view():
    """Render compliance scope view"""
    st.header("📋 Compliance Scope")
    
    try:
        db = get_database()
        
        compliance_tags = ["PCI-DSS", "SOX", "GLBA"]
        
        selected_tag = st.selectbox("Select compliance framework:", compliance_tags)
        
        if st.button("📊 View Scope", type="primary"):
            with st.spinner("Loading compliance scope..."):
                scope = get_compliance_scope(db.db, selected_tag)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Entities", scope.get("entity_count", 0))
            col2.metric("Firewall Rules", scope.get("rule_count", 0))
            col3.metric("Relationships", scope.get("relationship_count", 0))
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("In-Scope Entities")
                entities_df = pd.DataFrame(scope.get("entities", []))
                if not entities_df.empty:
                    st.dataframe(entities_df[["name", "entity_type"]], hide_index=True)
            
            with col2:
                st.subheader("Related Firewall Rules")
                rules_df = pd.DataFrame(scope.get("firewall_rules", []))
                if not rules_df.empty:
                    st.dataframe(rules_df[["rule_id", "name", "action"]], hide_index=True)
    
    except Exception as e:
        st.error(f"Error: {e}")


def render_firewall_rules_view():
    """Render firewall rules explorer"""
    st.header("🔥 Firewall Rules Explorer")
    
    try:
        db = get_database()
        
        col1, col2 = st.columns(2)
        
        zones = ["external", "dmz", "web-tier", "app-tier", "db-tier", "internal", "management"]
        
        with col1:
            source_zone = st.selectbox("Source Zone:", zones, index=1)
        with col2:
            dest_zone = st.selectbox("Destination Zone:", zones, index=4)
        
        if st.button("🔍 Find Rules", type="primary"):
            with st.spinner("Searching firewall rules..."):
                rules = find_network_paths(db.db, source_zone, dest_zone)
            
            if rules:
                st.success(f"Found {len(rules)} rules")
                
                for rule in rules:
                    with st.expander(f"**{rule.get('rule_id')}** - {rule.get('name')}"):
                        col1, col2, col3 = st.columns(3)
                        col1.write(f"**Firewall:** {rule.get('firewall')}")
                        col2.write(f"**Action:** {rule.get('action', 'N/A').upper()}")
                        col3.write(f"**Hits:** {rule.get('hit_count', 'N/A'):,}")
                        
                        st.write(f"**Description:** {rule.get('description', 'N/A')}")
                        st.write(f"**Compliance:** {rule.get('compliance_notes', 'N/A')}")
                        
                        services = rule.get('services', [])
                        if services:
                            services_str = ", ".join([f"{s.get('protocol')}:{s.get('port')}" for s in services])
                            st.write(f"**Services:** {services_str}")
            else:
                st.warning("No rules found for this path")
    
    except Exception as e:
        st.error(f"Error: {e}")


def main():
    render_header()
    render_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3  = st.tabs([
        "💬 Chat", 
        "🗺️ Topology", 
        "⚡ Impact Analysis"
       # "📋 Compliance",
       # "🔥 Firewall Rules"
    ])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_topology_view()
    
    with tab3:
        render_impact_analysis_view()
    
    #with tab4:
    #    render_compliance_view()
    
    #with tab5:
    #    render_firewall_rules_view()


if __name__ == "__main__":
    main()

