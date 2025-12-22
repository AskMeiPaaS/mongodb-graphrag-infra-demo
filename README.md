# MongoDB Atlas GraphRAG - Infrastructure Knowledge Graph Demo

A complete demonstration of **GraphRAG (Graph-based Retrieval Augmented Generation)** using MongoDB Atlas for managing a bank's infrastructure knowledge graph - including networking, firewalls, servers, applications, and security policies.

## 🎯 What This Demo Does

This demo showcases how to:
- Build a **knowledge graph** of infrastructure entities (servers, firewalls, applications, VLANs, etc.)
- Use **MongoDB Atlas Vector Search** for semantic similarity queries
- Leverage **$graphLookup** for multi-hop graph traversals
- Combine graph context with **LLM (Claude)** to answer natural language questions about infrastructure

**Example Questions You Can Ask:**
- "What would happen if FW-PROD-01 fails?"
- "Show me all dependencies of the Payment Gateway"
- "What firewall rules allow traffic from DMZ to database tier?"
- "List all PCI-DSS compliant components"

---

## 📸 Infrastructure Topology

The demo generates a complete infrastructure knowledge graph with the following components:

![Infrastructure Topology](images/topology.png)

*The topology shows the relationships between Firewalls, Load Balancers, Switches, VLANs, Servers, and Applications in a top-down traffic flow.*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Query                                    │
│  "What systems are affected if FW-PROD-01 goes down?"           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LangChain GraphRAG Chain                       │
├─────────────────────────────────────────────────────────────────┤
│  1. Parse query & generate embedding (VoyageAI)                  │
│  2. Vector search for relevant entities                          │
│  3. Graph traversal via $graphLookup                             │
│  4. Construct enriched context                                   │
│  5. LLM generates contextual response (Claude)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MongoDB Atlas                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  entities   │  │relationships│  │firewall_    │              │
│  │             │  │             │  │rules        │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  ┌─────────────────────────────────────────────────┐            │
│  │  Atlas Vector Search    │   $graphLookup        │            │
│  │  (Semantic Similarity)  │   (Graph Traversal)   │            │
│  └─────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

Before starting, ensure you have:

| Requirement | Description | Where to Get |
|-------------|-------------|--------------|
| **Python 3.9+** | Programming language | [python.org](https://python.org) |
| **MongoDB Atlas Cluster** | M10+ tier (for Vector Search) | [MongoDB Atlas](https://www.mongodb.com/atlas) |
| **VoyageAI API Key** | For generating embeddings | [VoyageAI](https://www.voyageai.com/) |
| **Anthropic API Key** | For Claude LLM responses | [Anthropic Console](https://console.anthropic.com/) |

---

## 🚀 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/harshitmehta1988/mongodb-graphrag-infra-demo.git
cd mongodb-graphrag-infra-demo
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Now edit the `.env` file with your credentials:

```env
# MongoDB Atlas Connection
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=infrastructure_graph

# VoyageAI (for embeddings)
VOYAGE_API_KEY=your_voyageai_api_key_here
VOYAGE_EMBEDDING_MODEL=voyage-2

# Anthropic (for LLM)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Vector dimensions (VoyageAI voyage-2 uses 1024)
VECTOR_DIMENSIONS=1024
```

### Step 5: Set Up MongoDB Atlas

#### 5.1 Create a Cluster
1. Log in to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a new cluster (M10+ tier recommended for Vector Search)
3. Wait for the cluster to be provisioned

#### 5.2 Configure Network Access
1. Go to **Security** → **Network Access**
2. Click **Add IP Address**
3. Add your current IP or use `0.0.0.0/0` for testing (not recommended for production)

#### 5.3 Create Database User
1. Go to **Security** → **Database Access**
2. Click **Add New Database User**
3. Create a user with **Read and Write** permissions
4. Note the username and password for your `.env` file

#### 5.4 Get Connection String
1. Click **Connect** on your cluster
2. Choose **Connect your application**
3. Copy the connection string
4. Replace `<password>` with your actual password in the `.env` file

### Step 6: Load Sample Data

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Load the sample infrastructure data
python scripts/load_sample_data.py
```

This will:
- Create the database and collections
- Generate sample infrastructure entities (servers, firewalls, applications, VLANs, etc.)
- Create relationships between entities
- Generate vector embeddings for all entities
- Load everything into MongoDB Atlas

### Step 7: Create Vector Search Indexes

After loading the sample data, you need to create **2 Vector Search indexes** in MongoDB Atlas.

#### 7.1 Create Index for `entities` Collection

1. In Atlas, go to your cluster → **Browse Collections**
2. You should see the `infrastructure_graph` database with `entities`, `relationships`, and `firewall_rules` collections
3. Go to **Atlas Search** → **Create Search Index**
4. Select **JSON Editor** and choose the `entities` collection
5. Set the **Index Name** to: `entities_vector_index`
6. Paste this configuration:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "description_embedding",
      "numDimensions": 1024,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "entity_type"
    },
    {
      "type": "filter",
      "path": "properties.criticality"
    }
  ]
}
```

7. Click **Create Search Index**

#### 7.2 Create Index for `firewall_rules` Collection

1. Go to **Atlas Search** → **Create Search Index**
2. Select **JSON Editor** and choose the `firewall_rules` collection
3. Set the **Index Name** to: `firewall_rules_vector_index`
4. Paste this configuration:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "description_embedding",
      "numDimensions": 1024,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "firewall"
    },
    {
      "type": "filter",
      "path": "source_zone"
    },
    {
      "type": "filter",
      "path": "destination_zone"
    },
    {
      "type": "filter",
      "path": "action"
    }
  ]
}
```

5. Click **Create Search Index**

> ⏳ **Note**: Vector Search indexes may take a few minutes to build. Wait until the status shows **Active** before proceeding to run the demo.


---

## ▶️ Running the Demo

### Streamlit Web UI

```bash
source venv/bin/activate
streamlit run demo/streamlit_app.py
```

This opens a web interface at `http://localhost:8501` with:
- **💬 Chat**: Ask natural language questions about infrastructure
- **🗺️ Topology**: Visual graph of all infrastructure components
- **⚡ Impact Analysis**: Analyze impact of component failures

---

## 📁 Project Structure

```
mongodb-graphrag-infra-demo/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
│
├── config/
│   └── atlas_indexes.json         # Vector & Search index definitions
│
├── data/
│   └── sample_data.py             # Sample infrastructure data generator
│
├── src/
│   ├── __init__.py
│   ├── database.py                # MongoDB connection & operations
│   ├── embeddings.py              # VoyageAI embedding generation
│   ├── graph_queries.py           # MongoDB graph traversal queries
│   ├── graphrag_retriever.py      # Custom LangChain retriever
│   └── graphrag_chain.py          # Main GraphRAG chain with Claude
│
├── scripts/
│   ├── setup_database.py          # Initialize database & indexes
│   └── load_sample_data.py        # Load sample data with embeddings
│
├── demo/
│   ├── demo_queries.py            # Interactive CLI demo
│   └── streamlit_app.py           # Streamlit web UI
│
└── tests/
    └── test_queries.py            # Test suite
```

---

## 🔍 How It Works

### 1. Data Model

The knowledge graph consists of three main collections:

**entities** - Infrastructure components:
- Servers (SRV-WEB-001, SRV-DB-001, etc.)
- Firewalls (FW-PROD-01, FW-DMZ-01, etc.)
- Load Balancers (LB-WEB-01, etc.)
- Applications (Payment-Gateway, Core-Banking-Service, etc.)
- VLANs (VLAN-DMZ, VLAN-WEB, VLAN-APP, etc.)
- Switches (SW-CORE-01, SW-CORE-02)

**relationships** - Connections between entities:
- RUNS_ON (Application → Server)
- BELONGS_TO (Server → VLAN)
- ROUTES_TO (Load Balancer → Server)
- PROTECTS (Firewall → VLAN)
- DEPENDS_ON (Application → Application)

**firewall_rules** - Network security policies:
- Source/destination zones
- Allowed services and ports
- Compliance tags (PCI-DSS, SOX, etc.)

### 2. Query Flow

When you ask a question:

1. **Embedding Generation**: Your query is converted to a vector using VoyageAI
2. **Vector Search**: MongoDB finds semantically similar entities
3. **Graph Traversal**: `$graphLookup` finds related entities (upstream/downstream)
4. **Context Assembly**: All relevant information is compiled
5. **LLM Response**: Claude generates a natural language answer

### 3. Key MongoDB Features Used

- **Atlas Vector Search**: Semantic similarity search on embeddings
- **$graphLookup**: Multi-hop graph traversals for dependency chains
- **Aggregation Pipeline**: Complex queries combining vector search and graph operations

---

## 📊 Sample Queries to Try

| Query | What It Does |
|-------|--------------|
| "What would happen if FW-PROD-01 fails?" | Impact analysis with dependency chain |
| "Show dependencies of Payment-Gateway" | Upstream and downstream dependencies |
| "What firewall rules exist from DMZ to database?" | Network path analysis |
| "List all PCI-DSS components" | Compliance scope query |
| "What applications run on SRV-APP-001?" | Asset discovery |
| "Impact of SRV-DB-003 maintenance" | Maintenance impact assessment |

---
