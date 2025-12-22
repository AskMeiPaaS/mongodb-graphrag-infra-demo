#!/usr/bin/env python3
"""
Interactive Demo Script for Infrastructure GraphRAG
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint

from src.graphrag_chain import InfrastructureAssistant, query_infrastructure
from src.database import get_db, get_collection_stats

console = Console()


# Sample queries for demo
DEMO_QUERIES = [
    {
        "category": "Impact Analysis",
        "queries": [
            "What would be the impact if FW-PROD-01 goes offline?",
            "What systems are affected if SRV-DB-003 fails?",
            "What happens if LB-WEB-01 needs maintenance?"
        ]
    },
    {
        "category": "Network Paths",
        "queries": [
            "Show me all firewall rules between DMZ and the database tier",
            "What network path does traffic take from the internet to Payment-Gateway?",
            "How does the web tier communicate with the application tier?"
        ]
    },
    {
        "category": "Dependency Mapping",
        "queries": [
            "What are all the dependencies of the Payment-Gateway application?",
            "What applications run on SRV-APP-001?",
            "What does Core-Banking-Service depend on?"
        ]
    },
    {
        "category": "Compliance",
        "queries": [
            "List all PCI-DSS scoped infrastructure components",
            "What firewall rules are required for PCI-DSS compliance?",
            "Show me all critical systems with SOX compliance requirements"
        ]
    },
    {
        "category": "Security Analysis",
        "queries": [
            "What firewall rules allow traffic to database servers?",
            "Is there any direct path from web tier to database tier?",
            "What security zones protect the Payment-Gateway?"
        ]
    }
]


def display_welcome():
    """Display welcome message"""
    console.print(Panel.fit(
        "[bold blue]MongoDB Atlas GraphRAG Demo[/bold blue]\n"
        "[dim]Infrastructure Knowledge Graph for Banking[/dim]",
        border_style="blue"
    ))


def display_stats():
    """Display database statistics"""
    db = get_db()
    stats = get_collection_stats(db)
    
    table = Table(title="📊 Database Statistics")
    table.add_column("Collection", style="cyan")
    table.add_column("Documents", style="green", justify="right")
    
    for collection, count in stats.items():
        table.add_row(collection, str(count))
    
    console.print(table)


def display_sample_queries():
    """Display sample queries by category"""
    console.print("\n[bold]📝 Sample Queries[/bold]\n")
    
    for i, category in enumerate(DEMO_QUERIES):
        console.print(f"[bold cyan]{i+1}. {category['category']}[/bold cyan]")
        for j, query in enumerate(category['queries']):
            console.print(f"   {chr(97+j)}) {query}")
        console.print()


def run_query(question: str):
    """Run a query and display results"""
    console.print(f"\n[bold yellow]🔍 Query:[/bold yellow] {question}\n")
    
    with console.status("[bold green]Processing query..."):
        assistant = InfrastructureAssistant()
        result = assistant.ask(question)
    
    # Display answer
    console.print(Panel(
        Markdown(result['answer']),
        title="📋 Answer",
        border_style="green"
    ))
    
    # Display source documents summary
    console.print(f"\n[dim]Retrieved {len(result['source_documents'])} context documents[/dim]")
    for doc in result['source_documents']:
        source = doc.metadata.get('source', 'unknown')
        console.print(f"  [dim]• {source}[/dim]")


def interactive_mode():
    """Run in interactive mode"""
    console.print("\n[bold green]Interactive Mode[/bold green]")
    console.print("[dim]Enter your questions about the infrastructure.[/dim]")
    console.print("[dim]Type 'quit' to exit, 'samples' to see sample queries.[/dim]\n")
    
    assistant = InfrastructureAssistant()
    
    while True:
        try:
            question = console.input("[bold blue]Question: [/bold blue]")
            
            if question.lower() in ['quit', 'exit', 'q']:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            
            if question.lower() == 'samples':
                display_sample_queries()
                continue
            
            if not question.strip():
                continue
            
            with console.status("[bold green]Processing..."):
                result = assistant.ask(question)
            
            console.print(Panel(
                Markdown(result['answer']),
                title="📋 Answer",
                border_style="green"
            ))
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Goodbye! 👋[/yellow]")
            break


def demo_mode():
    """Run pre-defined demo queries"""
    console.print("\n[bold green]Demo Mode[/bold green]")
    console.print("[dim]Running sample queries from each category...[/dim]\n")
    
    for category in DEMO_QUERIES:
        console.print(f"\n[bold cyan]━━━ {category['category']} ━━━[/bold cyan]\n")
        
        # Run first query from each category
        query = category['queries'][0]
        run_query(query)
        
        console.print("\n[dim]Press Enter to continue or 'q' to quit...[/dim]")
        response = input()
        if response.lower() == 'q':
            break


def main():
    display_welcome()
    
    console.print("\n[bold]Checking database connection...[/bold]")
    try:
        display_stats()
    except Exception as e:
        console.print(f"[red]Error connecting to database: {e}[/red]")
        console.print("[yellow]Please ensure MongoDB Atlas is configured correctly.[/yellow]")
        return
    
    console.print("\n[bold]Select mode:[/bold]")
    console.print("  1) Interactive - Ask your own questions")
    console.print("  2) Demo - Run sample queries")
    console.print("  3) Quick query - Run a single query and exit")
    console.print("  4) Show sample queries")
    
    choice = console.input("\n[bold blue]Choice (1/2/3/4): [/bold blue]")
    
    if choice == '1':
        interactive_mode()
    elif choice == '2':
        demo_mode()
    elif choice == '3':
        question = console.input("[bold blue]Enter your question: [/bold blue]")
        run_query(question)
    elif choice == '4':
        display_sample_queries()
        interactive_mode()
    else:
        console.print("[yellow]Invalid choice. Starting interactive mode...[/yellow]")
        interactive_mode()


if __name__ == "__main__":
    main()

