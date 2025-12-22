"""
Sample Infrastructure Data Generator
Generates realistic bank infrastructure data for the GraphRAG demo
"""

from datetime import datetime, timedelta
from bson import ObjectId
import random

# Pre-generate ObjectIds for consistent relationships
ENTITY_IDS = {
    # Firewalls
    "FW-PROD-01": ObjectId(),
    "FW-PROD-02": ObjectId(),
    "FW-DMZ-01": ObjectId(),
    "FW-INTERNAL-01": ObjectId(),
    
    # Servers - Database
    "SRV-DB-001": ObjectId(),
    "SRV-DB-002": ObjectId(),
    "SRV-DB-003": ObjectId(),
    "SRV-DB-004": ObjectId(),
    
    # Servers - Web
    "SRV-WEB-001": ObjectId(),
    "SRV-WEB-002": ObjectId(),
    "SRV-WEB-003": ObjectId(),
    "SRV-WEB-004": ObjectId(),
    
    # Servers - Application
    "SRV-APP-001": ObjectId(),
    "SRV-APP-002": ObjectId(),
    "SRV-APP-003": ObjectId(),
    "SRV-APP-004": ObjectId(),
    
    # Load Balancers
    "LB-WEB-01": ObjectId(),
    "LB-APP-01": ObjectId(),
    "LB-DB-01": ObjectId(),
    
    # Applications
    "APP-PAYMENT-GW": ObjectId(),
    "APP-CORE-BANKING": ObjectId(),
    "APP-CUSTOMER-PORTAL": ObjectId(),
    "APP-FRAUD-DETECT": ObjectId(),
    "APP-REPORTING": ObjectId(),
    "APP-MOBILE-API": ObjectId(),
    
    # Network Segments
    "VLAN-DMZ": ObjectId(),
    "VLAN-WEB": ObjectId(),
    "VLAN-APP": ObjectId(),
    "VLAN-DB-PROD": ObjectId(),
    "VLAN-MGMT": ObjectId(),
    
    # Switches
    "SW-CORE-01": ObjectId(),
    "SW-CORE-02": ObjectId(),
    "SW-ACCESS-01": ObjectId(),
    "SW-ACCESS-02": ObjectId(),
}


def generate_entities():
    """Generate all infrastructure entities"""
    entities = []
    now = datetime.utcnow()
    
    # ========== FIREWALLS ==========
    firewalls = [
        {
            "_id": ENTITY_IDS["FW-PROD-01"],
            "entity_type": "firewall",
            "name": "FW-PROD-01",
            "properties": {
                "vendor": "Palo Alto",
                "model": "PA-5220",
                "firmware_version": "10.2.3",
                "management_ip": "10.0.1.10",
                "location": "DC-East",
                "rack": "R15-U20",
                "security_zone": "perimeter",
                "criticality": "critical",
                "compliance_tags": ["PCI-DSS", "SOX", "GLBA"],
                "ha_pair": "FW-PROD-02",
                "throughput_gbps": 20
            },
            "interfaces": [
                {"name": "eth1/1", "ip": "10.0.1.1", "zone": "internal", "vlan": 100},
                {"name": "eth1/2", "ip": "192.168.1.1", "zone": "dmz", "vlan": 50},
                {"name": "eth1/3", "ip": "203.0.113.1", "zone": "external", "vlan": None},
                {"name": "eth1/4", "ip": "10.0.100.1", "zone": "management", "vlan": 999}
            ],
            "description": "Primary perimeter firewall protecting production environment. Handles all inbound traffic from internet to DMZ and internal networks. Part of HA cluster with FW-PROD-02. Critical for PCI-DSS compliance.",
            "last_updated": now - timedelta(hours=2)
        },
        {
            "_id": ENTITY_IDS["FW-PROD-02"],
            "entity_type": "firewall",
            "name": "FW-PROD-02",
            "properties": {
                "vendor": "Palo Alto",
                "model": "PA-5220",
                "firmware_version": "10.2.3",
                "management_ip": "10.0.1.11",
                "location": "DC-East",
                "rack": "R15-U22",
                "security_zone": "perimeter",
                "criticality": "critical",
                "compliance_tags": ["PCI-DSS", "SOX", "GLBA"],
                "ha_pair": "FW-PROD-01",
                "throughput_gbps": 20
            },
            "interfaces": [
                {"name": "eth1/1", "ip": "10.0.1.2", "zone": "internal", "vlan": 100},
                {"name": "eth1/2", "ip": "192.168.1.2", "zone": "dmz", "vlan": 50},
                {"name": "eth1/3", "ip": "203.0.113.2", "zone": "external", "vlan": None},
                {"name": "eth1/4", "ip": "10.0.100.2", "zone": "management", "vlan": 999}
            ],
            "description": "Secondary perimeter firewall in HA pair with FW-PROD-01. Provides failover capability for production traffic. Active-passive configuration.",
            "last_updated": now - timedelta(hours=2)
        },
        {
            "_id": ENTITY_IDS["FW-DMZ-01"],
            "entity_type": "firewall",
            "name": "FW-DMZ-01",
            "properties": {
                "vendor": "Fortinet",
                "model": "FortiGate-600E",
                "firmware_version": "7.2.4",
                "management_ip": "10.0.1.20",
                "location": "DC-East",
                "rack": "R16-U10",
                "security_zone": "dmz-internal",
                "criticality": "high",
                "compliance_tags": ["PCI-DSS"],
                "throughput_gbps": 10
            },
            "interfaces": [
                {"name": "port1", "ip": "192.168.1.10", "zone": "dmz", "vlan": 50},
                {"name": "port2", "ip": "10.10.0.1", "zone": "web-tier", "vlan": 110},
                {"name": "port3", "ip": "10.0.100.20", "zone": "management", "vlan": 999}
            ],
            "description": "DMZ segmentation firewall controlling traffic between DMZ and internal web tier. Inspects all traffic from public-facing services before reaching application servers.",
            "last_updated": now - timedelta(days=1)
        },
        {
            "_id": ENTITY_IDS["FW-INTERNAL-01"],
            "entity_type": "firewall",
            "name": "FW-INTERNAL-01",
            "properties": {
                "vendor": "Palo Alto",
                "model": "PA-3260",
                "firmware_version": "10.2.3",
                "management_ip": "10.0.1.30",
                "location": "DC-East",
                "rack": "R17-U15",
                "security_zone": "internal-segmentation",
                "criticality": "critical",
                "compliance_tags": ["PCI-DSS", "SOX"],
                "throughput_gbps": 15
            },
            "interfaces": [
                {"name": "eth1/1", "ip": "10.10.0.10", "zone": "web-tier", "vlan": 110},
                {"name": "eth1/2", "ip": "10.20.0.1", "zone": "app-tier", "vlan": 120},
                {"name": "eth1/3", "ip": "10.50.0.1", "zone": "db-tier", "vlan": 150},
                {"name": "eth1/4", "ip": "10.0.100.30", "zone": "management", "vlan": 999}
            ],
            "description": "Internal segmentation firewall providing micro-segmentation between web, application, and database tiers. Critical for PCI-DSS cardholder data environment isolation.",
            "last_updated": now - timedelta(hours=6)
        }
    ]
    entities.extend(firewalls)
    
    # ========== DATABASE SERVERS ==========
    db_servers = [
        {
            "_id": ENTITY_IDS["SRV-DB-001"],
            "entity_type": "server",
            "name": "SRV-DB-001",
            "properties": {
                "os": "Oracle Linux 8.7",
                "ip_addresses": ["10.50.10.10"],
                "vlan": "VLAN-DB-PROD",
                "data_center": "DC-East",
                "rack": "R20-U1",
                "cpu": "Intel Xeon Gold 6348 x2",
                "memory_gb": 512,
                "storage_tb": 20,
                "applications": ["Oracle-RAC-Node1"],
                "criticality": "critical",
                "data_classification": "PCI",
                "owner": "Database Team",
                "backup_schedule": "hourly",
                "compliance_tags": ["PCI-DSS", "SOX"]
            },
            "description": "Primary Oracle RAC node for core banking database. Hosts customer account data, transaction history, and financial records. Part of 4-node RAC cluster.",
            "last_updated": now - timedelta(hours=1)
        },
        {
            "_id": ENTITY_IDS["SRV-DB-002"],
            "entity_type": "server",
            "name": "SRV-DB-002",
            "properties": {
                "os": "Oracle Linux 8.7",
                "ip_addresses": ["10.50.10.11"],
                "vlan": "VLAN-DB-PROD",
                "data_center": "DC-East",
                "rack": "R20-U3",
                "cpu": "Intel Xeon Gold 6348 x2",
                "memory_gb": 512,
                "storage_tb": 20,
                "applications": ["Oracle-RAC-Node2"],
                "criticality": "critical",
                "data_classification": "PCI",
                "owner": "Database Team",
                "backup_schedule": "hourly",
                "compliance_tags": ["PCI-DSS", "SOX"]
            },
            "description": "Secondary Oracle RAC node for core banking database. Provides high availability and load distribution for database queries.",
            "last_updated": now - timedelta(hours=1)
        },
        {
            "_id": ENTITY_IDS["SRV-DB-003"],
            "entity_type": "server",
            "name": "SRV-DB-003",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.50.10.45"],
                "vlan": "VLAN-DB-PROD",
                "data_center": "DC-East",
                "rack": "R21-U5",
                "cpu": "Intel Xeon Gold 6342 x2",
                "memory_gb": 256,
                "storage_tb": 10,
                "applications": ["PostgreSQL-PaymentGW"],
                "criticality": "critical",
                "data_classification": "PCI",
                "owner": "Database Team",
                "backup_schedule": "continuous",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "PostgreSQL database server dedicated to Payment Gateway application. Stores payment transaction logs, card tokenization data, and payment processing records.",
            "last_updated": now - timedelta(hours=3)
        },
        {
            "_id": ENTITY_IDS["SRV-DB-004"],
            "entity_type": "server",
            "name": "SRV-DB-004",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.50.10.60"],
                "vlan": "VLAN-DB-PROD",
                "data_center": "DC-East",
                "rack": "R21-U10",
                "cpu": "Intel Xeon Gold 6342 x2",
                "memory_gb": 128,
                "storage_tb": 50,
                "applications": ["MongoDB-FraudDetection"],
                "criticality": "high",
                "data_classification": "internal",
                "owner": "Data Science Team",
                "backup_schedule": "daily",
                "compliance_tags": ["SOX"]
            },
            "description": "MongoDB server for fraud detection analytics. Stores transaction patterns, ML model features, and fraud scoring data.",
            "last_updated": now - timedelta(days=2)
        }
    ]
    entities.extend(db_servers)
    
    # ========== WEB SERVERS ==========
    web_servers = [
        {
            "_id": ENTITY_IDS["SRV-WEB-001"],
            "entity_type": "server",
            "name": "SRV-WEB-001",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.10.10.10"],
                "vlan": "VLAN-WEB",
                "data_center": "DC-East",
                "rack": "R10-U1",
                "cpu": "Intel Xeon Silver 4316 x2",
                "memory_gb": 64,
                "storage_tb": 1,
                "applications": ["nginx-reverse-proxy", "Customer-Portal-Frontend"],
                "criticality": "high",
                "data_classification": "public",
                "owner": "Platform Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Web server hosting customer portal frontend and nginx reverse proxy. Handles HTTPS termination and static content delivery.",
            "last_updated": now - timedelta(hours=4)
        },
        {
            "_id": ENTITY_IDS["SRV-WEB-002"],
            "entity_type": "server",
            "name": "SRV-WEB-002",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.10.10.11"],
                "vlan": "VLAN-WEB",
                "data_center": "DC-East",
                "rack": "R10-U3",
                "cpu": "Intel Xeon Silver 4316 x2",
                "memory_gb": 64,
                "storage_tb": 1,
                "applications": ["nginx-reverse-proxy", "Customer-Portal-Frontend"],
                "criticality": "high",
                "data_classification": "public",
                "owner": "Platform Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Secondary web server for customer portal. Part of load-balanced cluster for high availability.",
            "last_updated": now - timedelta(hours=4)
        },
        {
            "_id": ENTITY_IDS["SRV-WEB-003"],
            "entity_type": "server",
            "name": "SRV-WEB-003",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.10.10.20"],
                "vlan": "VLAN-WEB",
                "data_center": "DC-East",
                "rack": "R10-U5",
                "cpu": "Intel Xeon Silver 4316 x2",
                "memory_gb": 64,
                "storage_tb": 1,
                "applications": ["nginx-api-gateway", "Mobile-API-Gateway"],
                "criticality": "high",
                "data_classification": "public",
                "owner": "Platform Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "API gateway server for mobile banking application. Handles authentication, rate limiting, and API routing.",
            "last_updated": now - timedelta(hours=5)
        },
        {
            "_id": ENTITY_IDS["SRV-WEB-004"],
            "entity_type": "server",
            "name": "SRV-WEB-004",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.10.10.21"],
                "vlan": "VLAN-WEB",
                "data_center": "DC-East",
                "rack": "R10-U7",
                "cpu": "Intel Xeon Silver 4316 x2",
                "memory_gb": 64,
                "storage_tb": 1,
                "applications": ["nginx-api-gateway", "Mobile-API-Gateway"],
                "criticality": "high",
                "data_classification": "public",
                "owner": "Platform Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Secondary API gateway for mobile banking. Provides redundancy for mobile app traffic.",
            "last_updated": now - timedelta(hours=5)
        }
    ]
    entities.extend(web_servers)
    
    # ========== APPLICATION SERVERS ==========
    app_servers = [
        {
            "_id": ENTITY_IDS["SRV-APP-001"],
            "entity_type": "server",
            "name": "SRV-APP-001",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.20.10.10"],
                "vlan": "VLAN-APP",
                "data_center": "DC-East",
                "rack": "R12-U1",
                "cpu": "Intel Xeon Gold 6342 x2",
                "memory_gb": 128,
                "storage_tb": 2,
                "applications": ["Payment-Gateway", "Payment-Processor"],
                "criticality": "critical",
                "data_classification": "PCI",
                "owner": "Payments Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Primary application server for payment gateway. Processes credit card transactions, communicates with payment networks (Visa, Mastercard).",
            "last_updated": now - timedelta(hours=1)
        },
        {
            "_id": ENTITY_IDS["SRV-APP-002"],
            "entity_type": "server",
            "name": "SRV-APP-002",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.20.10.11"],
                "vlan": "VLAN-APP",
                "data_center": "DC-East",
                "rack": "R12-U3",
                "cpu": "Intel Xeon Gold 6342 x2",
                "memory_gb": 128,
                "storage_tb": 2,
                "applications": ["Payment-Gateway", "Payment-Processor"],
                "criticality": "critical",
                "data_classification": "PCI",
                "owner": "Payments Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Secondary payment gateway application server. Provides active-active redundancy for payment processing.",
            "last_updated": now - timedelta(hours=1)
        },
        {
            "_id": ENTITY_IDS["SRV-APP-003"],
            "entity_type": "server",
            "name": "SRV-APP-003",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.20.10.30"],
                "vlan": "VLAN-APP",
                "data_center": "DC-East",
                "rack": "R12-U10",
                "cpu": "Intel Xeon Gold 6342 x2",
                "memory_gb": 256,
                "storage_tb": 2,
                "applications": ["Core-Banking-Service", "Account-Management"],
                "criticality": "critical",
                "data_classification": "PCI",
                "owner": "Core Banking Team",
                "compliance_tags": ["PCI-DSS", "SOX"]
            },
            "description": "Core banking application server. Hosts account management, balance inquiries, and fund transfer services.",
            "last_updated": now - timedelta(hours=2)
        },
        {
            "_id": ENTITY_IDS["SRV-APP-004"],
            "entity_type": "server",
            "name": "SRV-APP-004",
            "properties": {
                "os": "RHEL 8.6",
                "ip_addresses": ["10.20.10.50"],
                "vlan": "VLAN-APP",
                "data_center": "DC-East",
                "rack": "R12-U15",
                "cpu": "Intel Xeon Gold 6342 x2",
                "memory_gb": 128,
                "storage_tb": 2,
                "applications": ["Fraud-Detection-Engine", "ML-Scoring-Service"],
                "criticality": "high",
                "data_classification": "internal",
                "owner": "Data Science Team",
                "compliance_tags": ["SOX"]
            },
            "description": "Fraud detection application server. Runs real-time ML models to score transactions and detect suspicious activity.",
            "last_updated": now - timedelta(hours=3)
        }
    ]
    entities.extend(app_servers)
    
    # ========== LOAD BALANCERS ==========
    load_balancers = [
        {
            "_id": ENTITY_IDS["LB-WEB-01"],
            "entity_type": "load_balancer",
            "name": "LB-WEB-01",
            "properties": {
                "vendor": "F5",
                "model": "BIG-IP i5800",
                "firmware_version": "16.1.3",
                "management_ip": "10.0.1.50",
                "vip_addresses": ["192.168.1.100", "192.168.1.101"],
                "location": "DC-East",
                "rack": "R08-U10",
                "criticality": "critical",
                "compliance_tags": ["PCI-DSS"],
                "throughput_gbps": 40,
                "ssl_offload": True
            },
            "pools": [
                {"name": "customer-portal-pool", "members": ["10.10.10.10:443", "10.10.10.11:443"]},
                {"name": "mobile-api-pool", "members": ["10.10.10.20:8443", "10.10.10.21:8443"]}
            ],
            "description": "Primary web tier load balancer. Handles SSL termination and distributes traffic to customer portal and mobile API servers.",
            "last_updated": now - timedelta(hours=6)
        },
        {
            "_id": ENTITY_IDS["LB-APP-01"],
            "entity_type": "load_balancer",
            "name": "LB-APP-01",
            "properties": {
                "vendor": "F5",
                "model": "BIG-IP i5800",
                "firmware_version": "16.1.3",
                "management_ip": "10.0.1.51",
                "vip_addresses": ["10.20.0.100", "10.20.0.101"],
                "location": "DC-East",
                "rack": "R08-U12",
                "criticality": "critical",
                "compliance_tags": ["PCI-DSS"],
                "throughput_gbps": 40,
                "ssl_offload": False
            },
            "pools": [
                {"name": "payment-gw-pool", "members": ["10.20.10.10:8443", "10.20.10.11:8443"]},
                {"name": "core-banking-pool", "members": ["10.20.10.30:8080"]}
            ],
            "description": "Application tier load balancer. Routes traffic to payment gateway and core banking services.",
            "last_updated": now - timedelta(hours=6)
        },
        {
            "_id": ENTITY_IDS["LB-DB-01"],
            "entity_type": "load_balancer",
            "name": "LB-DB-01",
            "properties": {
                "vendor": "HAProxy",
                "model": "Virtual Appliance",
                "version": "2.8.1",
                "management_ip": "10.0.1.52",
                "vip_addresses": ["10.50.0.100"],
                "location": "DC-East",
                "criticality": "high",
                "compliance_tags": ["PCI-DSS"],
                "mode": "tcp"
            },
            "pools": [
                {"name": "oracle-rac-pool", "members": ["10.50.10.10:1521", "10.50.10.11:1521"]},
                {"name": "postgres-pool", "members": ["10.50.10.45:5432"]}
            ],
            "description": "Database tier load balancer providing connection pooling and failover for Oracle RAC and PostgreSQL databases.",
            "last_updated": now - timedelta(days=3)
        }
    ]
    entities.extend(load_balancers)
    
    # ========== APPLICATIONS ==========
    applications = [
        {
            "_id": ENTITY_IDS["APP-PAYMENT-GW"],
            "entity_type": "application",
            "name": "Payment-Gateway",
            "properties": {
                "business_unit": "Retail Banking",
                "tier": "Tier-1",
                "ports": [8443],
                "protocol": "HTTPS",
                "data_classification": "PCI",
                "rpo_minutes": 0,
                "rto_minutes": 15,
                "transactions_per_day": 2500000,
                "owner": "Payments Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "dependencies": ["Core-Banking-Service", "PostgreSQL-PaymentGW", "Visa-Network", "Mastercard-Network"],
            "description": "Core payment processing gateway handling credit/debit card transactions. Integrates with Visa, Mastercard, and internal core banking. Processes 2.5M transactions daily.",
            "last_updated": now - timedelta(hours=1)
        },
        {
            "_id": ENTITY_IDS["APP-CORE-BANKING"],
            "entity_type": "application",
            "name": "Core-Banking-Service",
            "properties": {
                "business_unit": "Retail Banking",
                "tier": "Tier-1",
                "ports": [8080, 8443],
                "protocol": "HTTPS",
                "data_classification": "PCI",
                "rpo_minutes": 0,
                "rto_minutes": 30,
                "owner": "Core Banking Team",
                "compliance_tags": ["PCI-DSS", "SOX"]
            },
            "dependencies": ["Oracle-RAC", "Fraud-Detection-Engine"],
            "description": "Central banking system managing customer accounts, balances, transactions, and fund transfers. Heart of the bank's operations.",
            "last_updated": now - timedelta(hours=2)
        },
        {
            "_id": ENTITY_IDS["APP-CUSTOMER-PORTAL"],
            "entity_type": "application",
            "name": "Customer-Portal",
            "properties": {
                "business_unit": "Digital Banking",
                "tier": "Tier-1",
                "ports": [443],
                "protocol": "HTTPS",
                "data_classification": "confidential",
                "rpo_minutes": 15,
                "rto_minutes": 60,
                "monthly_active_users": 1500000,
                "owner": "Digital Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "dependencies": ["Core-Banking-Service", "Payment-Gateway"],
            "description": "Customer-facing web portal for online banking. Allows account management, bill pay, transfers, and statement viewing. 1.5M monthly active users.",
            "last_updated": now - timedelta(hours=4)
        },
        {
            "_id": ENTITY_IDS["APP-FRAUD-DETECT"],
            "entity_type": "application",
            "name": "Fraud-Detection-Engine",
            "properties": {
                "business_unit": "Risk Management",
                "tier": "Tier-2",
                "ports": [8080, 9090],
                "protocol": "gRPC",
                "data_classification": "internal",
                "rpo_minutes": 60,
                "rto_minutes": 120,
                "owner": "Data Science Team",
                "compliance_tags": ["SOX"]
            },
            "dependencies": ["MongoDB-FraudDetection", "ML-Model-Registry"],
            "description": "Real-time fraud detection system using ML models to score transactions. Analyzes patterns, velocity checks, and behavioral anomalies.",
            "last_updated": now - timedelta(hours=3)
        },
        {
            "_id": ENTITY_IDS["APP-MOBILE-API"],
            "entity_type": "application",
            "name": "Mobile-Banking-API",
            "properties": {
                "business_unit": "Digital Banking",
                "tier": "Tier-1",
                "ports": [8443],
                "protocol": "HTTPS/REST",
                "data_classification": "confidential",
                "rpo_minutes": 15,
                "rto_minutes": 30,
                "monthly_active_users": 800000,
                "owner": "Mobile Team",
                "compliance_tags": ["PCI-DSS"]
            },
            "dependencies": ["Core-Banking-Service", "Payment-Gateway", "Push-Notification-Service"],
            "description": "REST API backend for iOS and Android mobile banking apps. Supports biometric auth, mobile check deposit, and P2P payments.",
            "last_updated": now - timedelta(hours=5)
        },
        {
            "_id": ENTITY_IDS["APP-REPORTING"],
            "entity_type": "application",
            "name": "Reporting-Analytics",
            "properties": {
                "business_unit": "Finance",
                "tier": "Tier-3",
                "ports": [443, 8080],
                "protocol": "HTTPS",
                "data_classification": "internal",
                "rpo_minutes": 240,
                "rto_minutes": 480,
                "owner": "BI Team",
                "compliance_tags": ["SOX"]
            },
            "dependencies": ["Oracle-RAC", "Data-Warehouse"],
            "description": "Business intelligence and regulatory reporting platform. Generates daily reconciliation, monthly statements, and regulatory reports.",
            "last_updated": now - timedelta(days=1)
        }
    ]
    entities.extend(applications)
    
    # ========== VLANS ==========
    vlans = [
        {
            "_id": ENTITY_IDS["VLAN-DMZ"],
            "entity_type": "vlan",
            "name": "VLAN-DMZ",
            "properties": {
                "vlan_id": 50,
                "network": "192.168.1.0/24",
                "gateway": "192.168.1.1",
                "security_zone": "dmz",
                "description": "Demilitarized zone for public-facing services",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "DMZ network segment hosting public-facing load balancers and reverse proxies. First line of defense for external traffic.",
            "last_updated": now - timedelta(days=30)
        },
        {
            "_id": ENTITY_IDS["VLAN-WEB"],
            "entity_type": "vlan",
            "name": "VLAN-WEB",
            "properties": {
                "vlan_id": 110,
                "network": "10.10.10.0/24",
                "gateway": "10.10.10.1",
                "security_zone": "web-tier",
                "description": "Web server tier for frontend applications",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Web tier network hosting customer portal and API gateway servers. Behind DMZ firewall.",
            "last_updated": now - timedelta(days=30)
        },
        {
            "_id": ENTITY_IDS["VLAN-APP"],
            "entity_type": "vlan",
            "name": "VLAN-APP",
            "properties": {
                "vlan_id": 120,
                "network": "10.20.10.0/24",
                "gateway": "10.20.10.1",
                "security_zone": "app-tier",
                "description": "Application server tier",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Application tier network for payment gateway, core banking, and business logic services.",
            "last_updated": now - timedelta(days=30)
        },
        {
            "_id": ENTITY_IDS["VLAN-DB-PROD"],
            "entity_type": "vlan",
            "name": "VLAN-DB-PROD",
            "properties": {
                "vlan_id": 150,
                "network": "10.50.10.0/24",
                "gateway": "10.50.10.1",
                "security_zone": "database-tier",
                "description": "Production database tier - highly restricted",
                "compliance_tags": ["PCI-DSS", "SOX"]
            },
            "description": "Highly secured database tier network. Contains all production databases including Oracle RAC and PostgreSQL. Strictest access controls.",
            "last_updated": now - timedelta(days=30)
        },
        {
            "_id": ENTITY_IDS["VLAN-MGMT"],
            "entity_type": "vlan",
            "name": "VLAN-MGMT",
            "properties": {
                "vlan_id": 999,
                "network": "10.0.100.0/24",
                "gateway": "10.0.100.1",
                "security_zone": "management",
                "description": "Out-of-band management network",
                "compliance_tags": ["PCI-DSS", "SOX"]
            },
            "description": "Out-of-band management network for infrastructure administration. Isolated from production traffic. Jump box access only.",
            "last_updated": now - timedelta(days=30)
        }
    ]
    entities.extend(vlans)
    
    # ========== SWITCHES ==========
    switches = [
        {
            "_id": ENTITY_IDS["SW-CORE-01"],
            "entity_type": "switch",
            "name": "SW-CORE-01",
            "properties": {
                "vendor": "Cisco",
                "model": "Nexus 9336C-FX2",
                "firmware_version": "10.2(3)",
                "management_ip": "10.0.100.100",
                "location": "DC-East",
                "rack": "R01-U40",
                "criticality": "critical",
                "port_count": 36,
                "speed": "100G",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Primary core switch providing backbone connectivity. Interconnects all distribution switches and firewalls. Redundant with SW-CORE-02.",
            "last_updated": now - timedelta(days=7)
        },
        {
            "_id": ENTITY_IDS["SW-CORE-02"],
            "entity_type": "switch",
            "name": "SW-CORE-02",
            "properties": {
                "vendor": "Cisco",
                "model": "Nexus 9336C-FX2",
                "firmware_version": "10.2(3)",
                "management_ip": "10.0.100.101",
                "location": "DC-East",
                "rack": "R02-U40",
                "criticality": "critical",
                "port_count": 36,
                "speed": "100G",
                "compliance_tags": ["PCI-DSS"]
            },
            "description": "Secondary core switch in redundant pair with SW-CORE-01. Ensures no single point of failure for network backbone.",
            "last_updated": now - timedelta(days=7)
        }
    ]
    entities.extend(switches)
    
    return entities


def generate_relationships():
    """Generate relationships between entities"""
    relationships = []
    now = datetime.utcnow()
    
    # ========== FIREWALL PROTECTS RELATIONSHIPS ==========
    firewall_protects = [
        # FW-PROD-01 protects DMZ
        {
            "_id": ObjectId(),
            "relationship_type": "PROTECTS",
            "source": {"entity_id": ENTITY_IDS["FW-PROD-01"], "entity_type": "firewall", "name": "FW-PROD-01"},
            "target": {"entity_id": ENTITY_IDS["VLAN-DMZ"], "entity_type": "vlan", "name": "VLAN-DMZ"},
            "properties": {"direction": "inbound", "inspection_type": "deep-packet"},
            "created_at": now - timedelta(days=365)
        },
        # FW-DMZ-01 protects Web tier
        {
            "_id": ObjectId(),
            "relationship_type": "PROTECTS",
            "source": {"entity_id": ENTITY_IDS["FW-DMZ-01"], "entity_type": "firewall", "name": "FW-DMZ-01"},
            "target": {"entity_id": ENTITY_IDS["VLAN-WEB"], "entity_type": "vlan", "name": "VLAN-WEB"},
            "properties": {"direction": "inbound", "inspection_type": "application-aware"},
            "created_at": now - timedelta(days=365)
        },
        # FW-INTERNAL-01 protects App and DB tiers
        {
            "_id": ObjectId(),
            "relationship_type": "PROTECTS",
            "source": {"entity_id": ENTITY_IDS["FW-INTERNAL-01"], "entity_type": "firewall", "name": "FW-INTERNAL-01"},
            "target": {"entity_id": ENTITY_IDS["VLAN-APP"], "entity_type": "vlan", "name": "VLAN-APP"},
            "properties": {"direction": "inbound", "inspection_type": "micro-segmentation"},
            "created_at": now - timedelta(days=365)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "PROTECTS",
            "source": {"entity_id": ENTITY_IDS["FW-INTERNAL-01"], "entity_type": "firewall", "name": "FW-INTERNAL-01"},
            "target": {"entity_id": ENTITY_IDS["VLAN-DB-PROD"], "entity_type": "vlan", "name": "VLAN-DB-PROD"},
            "properties": {"direction": "inbound", "inspection_type": "micro-segmentation"},
            "created_at": now - timedelta(days=365)
        },
    ]
    relationships.extend(firewall_protects)
    
    # ========== LOAD BALANCER ROUTES TO SERVERS ==========
    lb_routes = [
        # LB-WEB-01 routes to web servers
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-WEB-01"], "entity_type": "load_balancer", "name": "LB-WEB-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-WEB-001"], "entity_type": "server", "name": "SRV-WEB-001"},
            "properties": {"pool": "customer-portal-pool", "weight": 50, "health_check": "https"},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-WEB-01"], "entity_type": "load_balancer", "name": "LB-WEB-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-WEB-002"], "entity_type": "server", "name": "SRV-WEB-002"},
            "properties": {"pool": "customer-portal-pool", "weight": 50, "health_check": "https"},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-WEB-01"], "entity_type": "load_balancer", "name": "LB-WEB-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-WEB-003"], "entity_type": "server", "name": "SRV-WEB-003"},
            "properties": {"pool": "mobile-api-pool", "weight": 50, "health_check": "https"},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-WEB-01"], "entity_type": "load_balancer", "name": "LB-WEB-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-WEB-004"], "entity_type": "server", "name": "SRV-WEB-004"},
            "properties": {"pool": "mobile-api-pool", "weight": 50, "health_check": "https"},
            "created_at": now - timedelta(days=180)
        },
        # LB-APP-01 routes to app servers
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-APP-001"], "entity_type": "server", "name": "SRV-APP-001"},
            "properties": {"pool": "payment-gw-pool", "weight": 50, "health_check": "https"},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-APP-002"], "entity_type": "server", "name": "SRV-APP-002"},
            "properties": {"pool": "payment-gw-pool", "weight": 50, "health_check": "https"},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-APP-003"], "entity_type": "server", "name": "SRV-APP-003"},
            "properties": {"pool": "core-banking-pool", "weight": 100, "health_check": "tcp"},
            "created_at": now - timedelta(days=180)
        },
        # LB-DB-01 routes to database servers
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-DB-01"], "entity_type": "load_balancer", "name": "LB-DB-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-001"], "entity_type": "server", "name": "SRV-DB-001"},
            "properties": {"pool": "oracle-rac-pool", "weight": 50, "health_check": "tcp"},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-DB-01"], "entity_type": "load_balancer", "name": "LB-DB-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-002"], "entity_type": "server", "name": "SRV-DB-002"},
            "properties": {"pool": "oracle-rac-pool", "weight": 50, "health_check": "tcp"},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "ROUTES_TO",
            "source": {"entity_id": ENTITY_IDS["LB-DB-01"], "entity_type": "load_balancer", "name": "LB-DB-01"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-003"], "entity_type": "server", "name": "SRV-DB-003"},
            "properties": {"pool": "postgres-pool", "weight": 100, "health_check": "tcp"},
            "created_at": now - timedelta(days=180)
        },
    ]
    relationships.extend(lb_routes)
    
    # ========== SERVER CONNECTS_TO RELATIONSHIPS ==========
    server_connections = [
        # Web servers connect to app servers
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SRV-WEB-001"], "entity_type": "server", "name": "SRV-WEB-001"},
            "target": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "properties": {"protocol": "HTTPS", "port": 8443, "encrypted": True},
            "created_at": now - timedelta(days=200)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SRV-WEB-002"], "entity_type": "server", "name": "SRV-WEB-002"},
            "target": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "properties": {"protocol": "HTTPS", "port": 8443, "encrypted": True},
            "created_at": now - timedelta(days=200)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SRV-WEB-003"], "entity_type": "server", "name": "SRV-WEB-003"},
            "target": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "properties": {"protocol": "HTTPS", "port": 8443, "encrypted": True},
            "created_at": now - timedelta(days=200)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SRV-WEB-004"], "entity_type": "server", "name": "SRV-WEB-004"},
            "target": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "properties": {"protocol": "HTTPS", "port": 8443, "encrypted": True},
            "created_at": now - timedelta(days=200)
        },
        # App servers connect to database LB
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SRV-APP-001"], "entity_type": "server", "name": "SRV-APP-001"},
            "target": {"entity_id": ENTITY_IDS["LB-DB-01"], "entity_type": "load_balancer", "name": "LB-DB-01"},
            "properties": {"protocol": "TCP", "port": 5432, "encrypted": True, "connection_pool_size": 50},
            "created_at": now - timedelta(days=200)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SRV-APP-002"], "entity_type": "server", "name": "SRV-APP-002"},
            "target": {"entity_id": ENTITY_IDS["LB-DB-01"], "entity_type": "load_balancer", "name": "LB-DB-01"},
            "properties": {"protocol": "TCP", "port": 5432, "encrypted": True, "connection_pool_size": 50},
            "created_at": now - timedelta(days=200)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SRV-APP-003"], "entity_type": "server", "name": "SRV-APP-003"},
            "target": {"entity_id": ENTITY_IDS["LB-DB-01"], "entity_type": "load_balancer", "name": "LB-DB-01"},
            "properties": {"protocol": "TCP", "port": 1521, "encrypted": True, "connection_pool_size": 100},
            "created_at": now - timedelta(days=200)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SRV-APP-004"], "entity_type": "server", "name": "SRV-APP-004"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-004"], "entity_type": "server", "name": "SRV-DB-004"},
            "properties": {"protocol": "TCP", "port": 27017, "encrypted": True},
            "created_at": now - timedelta(days=200)
        },
    ]
    relationships.extend(server_connections)
    
    # ========== APPLICATION RUNS_ON RELATIONSHIPS ==========
    app_runs_on = [
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-PAYMENT-GW"], "entity_type": "application", "name": "Payment-Gateway"},
            "target": {"entity_id": ENTITY_IDS["SRV-APP-001"], "entity_type": "server", "name": "SRV-APP-001"},
            "properties": {"deployment_type": "containerized", "replicas": 4, "resource_allocation": "8 vCPU, 32GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-PAYMENT-GW"], "entity_type": "application", "name": "Payment-Gateway"},
            "target": {"entity_id": ENTITY_IDS["SRV-APP-002"], "entity_type": "server", "name": "SRV-APP-002"},
            "properties": {"deployment_type": "containerized", "replicas": 4, "resource_allocation": "8 vCPU, 32GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-CORE-BANKING"], "entity_type": "application", "name": "Core-Banking-Service"},
            "target": {"entity_id": ENTITY_IDS["SRV-APP-003"], "entity_type": "server", "name": "SRV-APP-003"},
            "properties": {"deployment_type": "bare-metal", "instances": 2, "resource_allocation": "32 vCPU, 128GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-CUSTOMER-PORTAL"], "entity_type": "application", "name": "Customer-Portal"},
            "target": {"entity_id": ENTITY_IDS["SRV-WEB-001"], "entity_type": "server", "name": "SRV-WEB-001"},
            "properties": {"deployment_type": "containerized", "replicas": 6, "resource_allocation": "4 vCPU, 16GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-CUSTOMER-PORTAL"], "entity_type": "application", "name": "Customer-Portal"},
            "target": {"entity_id": ENTITY_IDS["SRV-WEB-002"], "entity_type": "server", "name": "SRV-WEB-002"},
            "properties": {"deployment_type": "containerized", "replicas": 6, "resource_allocation": "4 vCPU, 16GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-FRAUD-DETECT"], "entity_type": "application", "name": "Fraud-Detection-Engine"},
            "target": {"entity_id": ENTITY_IDS["SRV-APP-004"], "entity_type": "server", "name": "SRV-APP-004"},
            "properties": {"deployment_type": "containerized", "replicas": 8, "resource_allocation": "16 vCPU, 64GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-MOBILE-API"], "entity_type": "application", "name": "Mobile-Banking-API"},
            "target": {"entity_id": ENTITY_IDS["SRV-WEB-003"], "entity_type": "server", "name": "SRV-WEB-003"},
            "properties": {"deployment_type": "containerized", "replicas": 8, "resource_allocation": "4 vCPU, 16GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-MOBILE-API"], "entity_type": "application", "name": "Mobile-Banking-API"},
            "target": {"entity_id": ENTITY_IDS["SRV-WEB-004"], "entity_type": "server", "name": "SRV-WEB-004"},
            "properties": {"deployment_type": "containerized", "replicas": 8, "resource_allocation": "4 vCPU, 16GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        # Reporting-Analytics runs on DB servers (needs direct database access)
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-REPORTING"], "entity_type": "application", "name": "Reporting-Analytics"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-001"], "entity_type": "server", "name": "SRV-DB-001"},
            "properties": {"deployment_type": "containerized", "replicas": 2, "resource_allocation": "8 vCPU, 32GB RAM"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "RUNS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-REPORTING"], "entity_type": "application", "name": "Reporting-Analytics"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-002"], "entity_type": "server", "name": "SRV-DB-002"},
            "properties": {"deployment_type": "containerized", "replicas": 2, "resource_allocation": "8 vCPU, 32GB RAM"},
            "created_at": now - timedelta(days=300)
        },
    ]
    relationships.extend(app_runs_on)
    
    # ========== APPLICATION DEPENDS_ON RELATIONSHIPS ==========
    app_depends = [
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-PAYMENT-GW"], "entity_type": "application", "name": "Payment-Gateway"},
            "target": {"entity_id": ENTITY_IDS["APP-CORE-BANKING"], "entity_type": "application", "name": "Core-Banking-Service"},
            "properties": {"dependency_type": "runtime", "criticality": "hard"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-PAYMENT-GW"], "entity_type": "application", "name": "Payment-Gateway"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-003"], "entity_type": "server", "name": "SRV-DB-003"},
            "properties": {"dependency_type": "database", "criticality": "hard"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-CUSTOMER-PORTAL"], "entity_type": "application", "name": "Customer-Portal"},
            "target": {"entity_id": ENTITY_IDS["APP-CORE-BANKING"], "entity_type": "application", "name": "Core-Banking-Service"},
            "properties": {"dependency_type": "runtime", "criticality": "hard"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-CUSTOMER-PORTAL"], "entity_type": "application", "name": "Customer-Portal"},
            "target": {"entity_id": ENTITY_IDS["APP-PAYMENT-GW"], "entity_type": "application", "name": "Payment-Gateway"},
            "properties": {"dependency_type": "runtime", "criticality": "soft"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-CORE-BANKING"], "entity_type": "application", "name": "Core-Banking-Service"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-001"], "entity_type": "server", "name": "SRV-DB-001"},
            "properties": {"dependency_type": "database", "criticality": "hard"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-CORE-BANKING"], "entity_type": "application", "name": "Core-Banking-Service"},
            "target": {"entity_id": ENTITY_IDS["APP-FRAUD-DETECT"], "entity_type": "application", "name": "Fraud-Detection-Engine"},
            "properties": {"dependency_type": "runtime", "criticality": "soft"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-FRAUD-DETECT"], "entity_type": "application", "name": "Fraud-Detection-Engine"},
            "target": {"entity_id": ENTITY_IDS["SRV-DB-004"], "entity_type": "server", "name": "SRV-DB-004"},
            "properties": {"dependency_type": "database", "criticality": "hard"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-MOBILE-API"], "entity_type": "application", "name": "Mobile-Banking-API"},
            "target": {"entity_id": ENTITY_IDS["APP-CORE-BANKING"], "entity_type": "application", "name": "Core-Banking-Service"},
            "properties": {"dependency_type": "runtime", "criticality": "hard"},
            "created_at": now - timedelta(days=300)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "DEPENDS_ON",
            "source": {"entity_id": ENTITY_IDS["APP-MOBILE-API"], "entity_type": "application", "name": "Mobile-Banking-API"},
            "target": {"entity_id": ENTITY_IDS["APP-PAYMENT-GW"], "entity_type": "application", "name": "Payment-Gateway"},
            "properties": {"dependency_type": "runtime", "criticality": "soft"},
            "created_at": now - timedelta(days=300)
        },
    ]
    relationships.extend(app_depends)
    
    # ========== BELONGS_TO RELATIONSHIPS (Servers/Load Balancers to VLANs) ==========
    belongs_to = [
        # Web servers belong to VLAN-WEB
        {"source": "SRV-WEB-001", "target": "VLAN-WEB", "source_type": "server"},
        {"source": "SRV-WEB-002", "target": "VLAN-WEB", "source_type": "server"},
        {"source": "SRV-WEB-003", "target": "VLAN-WEB", "source_type": "server"},
        {"source": "SRV-WEB-004", "target": "VLAN-WEB", "source_type": "server"},
        # App servers belong to VLAN-APP
        {"source": "SRV-APP-001", "target": "VLAN-APP", "source_type": "server"},
        {"source": "SRV-APP-002", "target": "VLAN-APP", "source_type": "server"},
        {"source": "SRV-APP-003", "target": "VLAN-APP", "source_type": "server"},
        {"source": "SRV-APP-004", "target": "VLAN-APP", "source_type": "server"},
        # DB servers belong to VLAN-DB-PROD
        {"source": "SRV-DB-001", "target": "VLAN-DB-PROD", "source_type": "server"},
        {"source": "SRV-DB-002", "target": "VLAN-DB-PROD", "source_type": "server"},
        {"source": "SRV-DB-003", "target": "VLAN-DB-PROD", "source_type": "server"},
        {"source": "SRV-DB-004", "target": "VLAN-DB-PROD", "source_type": "server"},
        # Load balancer in DMZ (entry point for external traffic)
        {"source": "LB-WEB-01", "target": "VLAN-DMZ", "source_type": "load_balancer"},
    ]
    
    for rel in belongs_to:
        relationships.append({
            "_id": ObjectId(),
            "relationship_type": "BELONGS_TO",
            "source": {
                "entity_id": ENTITY_IDS[rel["source"]], 
                "entity_type": rel.get("source_type", "server"), 
                "name": rel["source"]
            },
            "target": {
                "entity_id": ENTITY_IDS[rel["target"]], 
                "entity_type": "vlan", 
                "name": rel["target"]
            },
            "properties": {},
            "created_at": now - timedelta(days=365)
        })
    
    # ========== HA_PAIR RELATIONSHIPS ==========
    ha_pairs = [
        {
            "_id": ObjectId(),
            "relationship_type": "HA_PAIR",
            "source": {"entity_id": ENTITY_IDS["FW-PROD-01"], "entity_type": "firewall", "name": "FW-PROD-01"},
            "target": {"entity_id": ENTITY_IDS["FW-PROD-02"], "entity_type": "firewall", "name": "FW-PROD-02"},
            "properties": {"mode": "active-passive", "failover_time_ms": 500},
            "created_at": now - timedelta(days=365)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "HA_PAIR",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-01"], "entity_type": "switch", "name": "SW-CORE-01"},
            "target": {"entity_id": ENTITY_IDS["SW-CORE-02"], "entity_type": "switch", "name": "SW-CORE-02"},
            "properties": {"mode": "active-active", "protocol": "vPC"},
            "created_at": now - timedelta(days=365)
        },
    ]
    relationships.extend(ha_pairs)
    
    # ========== CORE SWITCH CONNECTIONS ==========
    # Core switches connect to firewalls
    switch_to_firewall = [
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-01"], "entity_type": "switch", "name": "SW-CORE-01"},
            "target": {"entity_id": ENTITY_IDS["FW-PROD-01"], "entity_type": "firewall", "name": "FW-PROD-01"},
            "properties": {"interface": "eth1/1", "speed": "100G", "redundant": True},
            "created_at": now - timedelta(days=365)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-01"], "entity_type": "switch", "name": "SW-CORE-01"},
            "target": {"entity_id": ENTITY_IDS["FW-INTERNAL-01"], "entity_type": "firewall", "name": "FW-INTERNAL-01"},
            "properties": {"interface": "eth1/2", "speed": "100G", "redundant": True},
            "created_at": now - timedelta(days=365)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-01"], "entity_type": "switch", "name": "SW-CORE-01"},
            "target": {"entity_id": ENTITY_IDS["FW-DMZ-01"], "entity_type": "firewall", "name": "FW-DMZ-01"},
            "properties": {"interface": "eth1/3", "speed": "40G", "redundant": True},
            "created_at": now - timedelta(days=365)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-02"], "entity_type": "switch", "name": "SW-CORE-02"},
            "target": {"entity_id": ENTITY_IDS["FW-PROD-02"], "entity_type": "firewall", "name": "FW-PROD-02"},
            "properties": {"interface": "eth1/1", "speed": "100G", "redundant": True},
            "created_at": now - timedelta(days=365)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-02"], "entity_type": "switch", "name": "SW-CORE-02"},
            "target": {"entity_id": ENTITY_IDS["FW-INTERNAL-01"], "entity_type": "firewall", "name": "FW-INTERNAL-01"},
            "properties": {"interface": "eth1/2", "speed": "100G", "redundant": True},
            "created_at": now - timedelta(days=365)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-02"], "entity_type": "switch", "name": "SW-CORE-02"},
            "target": {"entity_id": ENTITY_IDS["FW-DMZ-01"], "entity_type": "firewall", "name": "FW-DMZ-01"},
            "properties": {"interface": "eth1/3", "speed": "40G", "redundant": True},
            "created_at": now - timedelta(days=365)
        },
    ]
    relationships.extend(switch_to_firewall)
    
    # Core switches belong to management VLAN
    switch_belongs_to = [
        {
            "_id": ObjectId(),
            "relationship_type": "BELONGS_TO",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-01"], "entity_type": "switch", "name": "SW-CORE-01"},
            "target": {"entity_id": ENTITY_IDS["VLAN-MGMT"], "entity_type": "vlan", "name": "VLAN-MGMT"},
            "properties": {"management_interface": True},
            "created_at": now - timedelta(days=365)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "BELONGS_TO",
            "source": {"entity_id": ENTITY_IDS["SW-CORE-02"], "entity_type": "switch", "name": "SW-CORE-02"},
            "target": {"entity_id": ENTITY_IDS["VLAN-MGMT"], "entity_type": "vlan", "name": "VLAN-MGMT"},
            "properties": {"management_interface": True},
            "created_at": now - timedelta(days=365)
        },
    ]
    relationships.extend(switch_belongs_to)
    
    # Load balancers connect through core switches
    lb_to_switch = [
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["LB-WEB-01"], "entity_type": "load_balancer", "name": "LB-WEB-01"},
            "target": {"entity_id": ENTITY_IDS["SW-CORE-01"], "entity_type": "switch", "name": "SW-CORE-01"},
            "properties": {"interface": "eth1/10", "speed": "40G", "lacp": True},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["LB-WEB-01"], "entity_type": "load_balancer", "name": "LB-WEB-01"},
            "target": {"entity_id": ENTITY_IDS["SW-CORE-02"], "entity_type": "switch", "name": "SW-CORE-02"},
            "properties": {"interface": "eth1/10", "speed": "40G", "lacp": True},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "target": {"entity_id": ENTITY_IDS["SW-CORE-01"], "entity_type": "switch", "name": "SW-CORE-01"},
            "properties": {"interface": "eth1/11", "speed": "40G", "lacp": True},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["LB-APP-01"], "entity_type": "load_balancer", "name": "LB-APP-01"},
            "target": {"entity_id": ENTITY_IDS["SW-CORE-02"], "entity_type": "switch", "name": "SW-CORE-02"},
            "properties": {"interface": "eth1/11", "speed": "40G", "lacp": True},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["LB-DB-01"], "entity_type": "load_balancer", "name": "LB-DB-01"},
            "target": {"entity_id": ENTITY_IDS["SW-CORE-01"], "entity_type": "switch", "name": "SW-CORE-01"},
            "properties": {"interface": "eth1/12", "speed": "40G", "lacp": True},
            "created_at": now - timedelta(days=180)
        },
        {
            "_id": ObjectId(),
            "relationship_type": "CONNECTS_TO",
            "source": {"entity_id": ENTITY_IDS["LB-DB-01"], "entity_type": "load_balancer", "name": "LB-DB-01"},
            "target": {"entity_id": ENTITY_IDS["SW-CORE-02"], "entity_type": "switch", "name": "SW-CORE-02"},
            "properties": {"interface": "eth1/12", "speed": "40G", "lacp": True},
            "created_at": now - timedelta(days=180)
        },
    ]
    relationships.extend(lb_to_switch)
    
    return relationships


def generate_firewall_rules():
    """Generate firewall rules"""
    rules = []
    now = datetime.utcnow()
    
    firewall_rules = [
        # FW-PROD-01 Rules - Perimeter
        {
            "_id": ObjectId(),
            "rule_id": "ACL-1001",
            "firewall": "FW-PROD-01",
            "name": "Allow-HTTPS-Inbound",
            "source_zone": "external",
            "destination_zone": "dmz",
            "source_addresses": ["any"],
            "destination_addresses": ["192.168.1.100", "192.168.1.101"],
            "services": [{"protocol": "TCP", "port": 443}],
            "action": "allow",
            "logging": True,
            "enabled": True,
            "description": "Allow inbound HTTPS traffic from internet to web load balancer VIPs",
            "compliance_notes": "Required for customer portal and mobile app access",
            "hit_count": 15000000,
            "last_hit": now - timedelta(minutes=1),
            "last_modified": now - timedelta(days=90),
            "modified_by": "network-admin@bank.com"
        },
        {
            "_id": ObjectId(),
            "rule_id": "ACL-1002",
            "firewall": "FW-PROD-01",
            "name": "Deny-All-Inbound",
            "source_zone": "external",
            "destination_zone": "any",
            "source_addresses": ["any"],
            "destination_addresses": ["any"],
            "services": [{"protocol": "any", "port": "any"}],
            "action": "deny",
            "logging": True,
            "enabled": True,
            "description": "Default deny rule for all other inbound traffic",
            "compliance_notes": "PCI-DSS requirement - implicit deny",
            "hit_count": 500000000,
            "last_hit": now - timedelta(seconds=5),
            "last_modified": now - timedelta(days=365),
            "modified_by": "security-admin@bank.com"
        },
        
        # FW-DMZ-01 Rules - DMZ to Internal
        {
            "_id": ObjectId(),
            "rule_id": "ACL-2001",
            "firewall": "FW-DMZ-01",
            "name": "Allow-DMZ-to-Web-Tier",
            "source_zone": "dmz",
            "destination_zone": "web-tier",
            "source_addresses": ["192.168.1.100", "192.168.1.101"],
            "destination_addresses": ["10.10.10.0/24"],
            "services": [{"protocol": "TCP", "port": 443}, {"protocol": "TCP", "port": 8443}],
            "action": "allow",
            "logging": True,
            "enabled": True,
            "description": "Allow load balancer to forward traffic to web servers",
            "compliance_notes": "Traffic inspection enabled",
            "hit_count": 12000000,
            "last_hit": now - timedelta(minutes=1),
            "last_modified": now - timedelta(days=60),
            "modified_by": "network-admin@bank.com"
        },
        
        # FW-INTERNAL-01 Rules - Internal segmentation
        {
            "_id": ObjectId(),
            "rule_id": "ACL-3001",
            "firewall": "FW-INTERNAL-01",
            "name": "Allow-Web-to-App-Tier",
            "source_zone": "web-tier",
            "destination_zone": "app-tier",
            "source_addresses": ["10.10.10.0/24"],
            "destination_addresses": ["10.20.0.100", "10.20.0.101"],
            "services": [{"protocol": "TCP", "port": 8443}, {"protocol": "TCP", "port": 8080}],
            "action": "allow",
            "logging": True,
            "enabled": True,
            "description": "Allow web tier to connect to application load balancer",
            "compliance_notes": "PCI-DSS segmentation control",
            "hit_count": 8000000,
            "last_hit": now - timedelta(minutes=2),
            "last_modified": now - timedelta(days=45),
            "modified_by": "network-admin@bank.com"
        },
        {
            "_id": ObjectId(),
            "rule_id": "ACL-3002",
            "firewall": "FW-INTERNAL-01",
            "name": "Allow-App-to-DB-Tier",
            "source_zone": "app-tier",
            "destination_zone": "db-tier",
            "source_addresses": ["10.20.10.0/24"],
            "destination_addresses": ["10.50.0.100"],
            "services": [
                {"protocol": "TCP", "port": 1521},
                {"protocol": "TCP", "port": 5432},
                {"protocol": "TCP", "port": 27017}
            ],
            "action": "allow",
            "logging": True,
            "enabled": True,
            "description": "Allow application servers to connect to database load balancer",
            "compliance_notes": "PCI-DSS CDE boundary control - database access restricted to app tier only",
            "hit_count": 5000000,
            "last_hit": now - timedelta(minutes=1),
            "last_modified": now - timedelta(days=30),
            "modified_by": "dba-admin@bank.com"
        },
        {
            "_id": ObjectId(),
            "rule_id": "ACL-3003",
            "firewall": "FW-INTERNAL-01",
            "name": "Deny-Direct-Web-to-DB",
            "source_zone": "web-tier",
            "destination_zone": "db-tier",
            "source_addresses": ["10.10.10.0/24"],
            "destination_addresses": ["10.50.10.0/24"],
            "services": [{"protocol": "any", "port": "any"}],
            "action": "deny",
            "logging": True,
            "enabled": True,
            "description": "Explicitly deny direct web tier to database tier access",
            "compliance_notes": "PCI-DSS requirement - web tier cannot directly access cardholder data",
            "hit_count": 150000,
            "last_hit": now - timedelta(hours=2),
            "last_modified": now - timedelta(days=365),
            "modified_by": "security-admin@bank.com"
        },
        {
            "_id": ObjectId(),
            "rule_id": "ACL-3004",
            "firewall": "FW-INTERNAL-01",
            "name": "Allow-Payment-GW-to-External-Networks",
            "source_zone": "app-tier",
            "destination_zone": "external",
            "source_addresses": ["10.20.10.10", "10.20.10.11"],
            "destination_addresses": ["visa-network.com", "mastercard-network.com"],
            "services": [{"protocol": "TCP", "port": 443}],
            "action": "allow",
            "logging": True,
            "enabled": True,
            "description": "Allow payment gateway servers to communicate with card networks",
            "compliance_notes": "Required for payment authorization - encrypted TLS 1.3",
            "hit_count": 2500000,
            "last_hit": now - timedelta(minutes=1),
            "last_modified": now - timedelta(days=120),
            "modified_by": "payments-admin@bank.com"
        },
        {
            "_id": ObjectId(),
            "rule_id": "ACL-3005",
            "firewall": "FW-INTERNAL-01",
            "name": "Allow-Fraud-Detection-to-DB",
            "source_zone": "app-tier",
            "destination_zone": "db-tier",
            "source_addresses": ["10.20.10.50"],
            "destination_addresses": ["10.50.10.60"],
            "services": [{"protocol": "TCP", "port": 27017}],
            "action": "allow",
            "logging": True,
            "enabled": True,
            "description": "Allow fraud detection engine to access MongoDB for ML model data",
            "compliance_notes": "SOX compliance - transaction monitoring",
            "hit_count": 3000000,
            "last_hit": now - timedelta(minutes=5),
            "last_modified": now - timedelta(days=90),
            "modified_by": "datascience-admin@bank.com"
        },
    ]
    
    return firewall_rules


# Export data generators
__all__ = ['generate_entities', 'generate_relationships', 'generate_firewall_rules', 'ENTITY_IDS']

