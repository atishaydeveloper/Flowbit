import sqlite3
import json
from tabulate import tabulate
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

def connect_db():
    return sqlite3.connect("flowbit.db")

@app.command()
def view_inputs():
    """View all stored inputs"""
    conn = connect_db()
    cursor = conn.execute("SELECT input_id, input_text, timestamp, input_type FROM inputs")
    data = cursor.fetchall()
    
    table = Table(title="Stored Inputs")
    table.add_column("ID", style="cyan")
    table.add_column("Text", style="green")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Type", style="yellow")
    
    for row in data:
        table.add_row(str(row[0]), str(row[1])[:50] + "...", str(row[2]), str(row[3]))
    
    console.print(table)

@app.command()
def view_classifications():
    """View all classifications"""
    conn = connect_db()
    cursor = conn.execute("""
        SELECT c.input_id, c.format, c.intent, c.reasoning, c.timestamp 
        FROM classifications c
        JOIN inputs i ON c.input_id = i.input_id
    """)
    data = cursor.fetchall()
    
    table = Table(title="Classifications")
    table.add_column("ID", style="cyan")
    table.add_column("Format", style="green")
    table.add_column("Intent", style="blue")
    table.add_column("Reasoning", style="yellow")
    table.add_column("Timestamp", style="magenta")
    
    for row in data:
        table.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3])[:50] + "...", str(row[4]))
    
    console.print(table)

@app.command()
def view_results():
    """View processing results"""
    conn = connect_db()
    cursor = conn.execute("SELECT input_id, result_data, timestamp FROM results")
    data = cursor.fetchall()
    
    table = Table(title="Processing Results")
    table.add_column("ID", style="cyan")
    table.add_column("Result", style="green")
    table.add_column("Timestamp", style="magenta")
    
    for row in data:
        result_preview = json.dumps(json.loads(row[1]), indent=2)[:50] + "..."
        table.add_row(str(row[0]), result_preview, str(row[2]))
    
    console.print(table)

@app.command()
def view_full_record(input_id: str):
    """View complete processing record for a specific input"""
    conn = connect_db()
    
    # Get input
    cursor = conn.execute("SELECT * FROM inputs WHERE input_id = ?", (input_id,))
    input_data = cursor.fetchone()
    
    # Get classification
    cursor = conn.execute("SELECT * FROM classifications WHERE input_id = ?", (input_id,))
    classification = cursor.fetchone()
    
    # Get result
    cursor = conn.execute("SELECT * FROM results WHERE input_id = ?", (input_id,))
    result = cursor.fetchone()
    
    if input_data:
        console.print(f"\n[cyan]Input Record[/cyan] (ID: {input_id})")
        console.print(f"Text: {input_data[1]}")
        console.print(f"Type: {input_data[3]}")
        console.print(f"Timestamp: {input_data[2]}")
        
        if classification:
            console.print("\n[green]Classification[/green]")
            console.print(f"Format: {classification[1]}")
            console.print(f"Intent: {classification[2]}")
            console.print(f"Reasoning: {classification[3]}")
            
        if result:
            console.print("\n[yellow]Processing Result[/yellow]")
            console.print(json.dumps(json.loads(result[1]), indent=2))
    else:
        console.print(f"[red]No record found for ID: {input_id}[/red]")

if __name__ == "__main__":
    app()