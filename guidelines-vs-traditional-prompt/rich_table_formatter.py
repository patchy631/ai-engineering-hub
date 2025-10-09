"""Rich table formatter for comparison results."""
from rich.console import Console
from rich.table import Table
from rich import box

def print_comparison_rich(headers: list[str], rows: list[list[str]]) -> None:
    """Render a beautiful comparison table using Rich library."""
    console = Console()
    
    # Create the main table
    table = Table(
            title="🤖 Parlant Guidelines vs Traditional Prompt: Life Insurance Agent Comparison",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        title_style="bold blue",
        show_lines=True
    )
    
    # Add columns with different styles
    table.add_column("📝 Query", style="cyan", width=30, no_wrap=False, overflow="fold")
    table.add_column("🤖 Traditional LLM", style="dim red", width=50, no_wrap=False, overflow="fold")
    table.add_column("🎯 Parlant Agent", style="green", width=50, no_wrap=False, overflow="fold")
    table.add_column("🧠 Reasoning", style="yellow1", width=35, no_wrap=False, overflow="fold")
    
    for row in rows:
        query, traditional, parlant, reasoning = row
        
        # Format reasoning with better styling
        if reasoning and reasoning != "(no explicit tools/guidelines recorded)":
            parts = reasoning.split(" | ")
            reasoning_text = ""
            for part in parts:
                if part.startswith("Guidelines:"):
                    guideline_text = part.replace("Guidelines: ", "")
                    reasoning_text += f"[bold green]📋 Guidelines:[/bold green]\n[dim]{guideline_text}[/dim]\n\n"
                elif part.startswith("Tools:"):
                    tool_text = part.replace("Tools: ", "")
                    reasoning_text += f"[bold blue]🔧 Tools:[/bold blue]\n[dim]{tool_text}[/dim]"
        else:
            reasoning_text = "[dim]No explicit guidelines/tools recorded[/dim]"
        
        # Format text based on column type for optimal display
        def format_query_text(text):
            """Format query text - keep it concise and readable."""
            text = text.strip()
            if len(text) > 50:
                words = text.split()
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) > 50:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                    else:
                        current_line += " " + word if current_line else word
                if current_line:
                    lines.append(current_line)
                return '\n'.join(lines)
            return text

        def format_traditional_text(text):
            """Format traditional LLM response - handle verbose content."""
            text = text.strip()
            
            # Break at natural sentence boundaries first
            text = text.replace('. ', '.\n').replace('! ', '!\n').replace('? ', '?\n')
            text = text.replace('\n\n', '\n')
            
            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            # Format each line to fit column width
            formatted_lines = []
            for line in lines:
                if len(line) > 45:  # Shorter lines for traditional column
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + " " + word) > 45:
                            if current_line and len(current_line) > 15:
                                formatted_lines.append(current_line)
                                current_line = word
                            else:
                                current_line += " " + word if current_line else word
                        else:
                            current_line += " " + word if current_line else word
                    if current_line:
                        formatted_lines.append(current_line)
                else:
                    formatted_lines.append(line)
            
            return '\n'.join(formatted_lines)

        def format_parlant_text(text):
            """Format Parlant response - handle structured content."""
            text = text.strip()
            
            # Break at natural sentence boundaries
            text = text.replace('. ', '.\n').replace('! ', '!\n').replace('? ', '?\n')
            text = text.replace('\n\n', '\n')
            
            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            # Format each line to fit column width
            formatted_lines = []
            for line in lines:
                if len(line) > 45:  # Shorter lines for Parlant column
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + " " + word) > 45:
                            if current_line and len(current_line) > 15:
                                formatted_lines.append(current_line)
                                current_line = word
                            else:
                                current_line += " " + word if current_line else word
                        else:
                            current_line += " " + word if current_line else word
                    if current_line:
                        formatted_lines.append(current_line)
                else:
                    formatted_lines.append(line)
            
            return '\n'.join(formatted_lines)

        def format_reasoning_text(text):
            """Format reasoning text - handle structured guidelines and tools."""
            text = text.strip()
            
            # Handle structured reasoning content
            if "📋 Guidelines:" in text and "🔧 Tools:" in text:
                # Split guidelines and tools
                parts = text.split("🔧 Tools:")
                guidelines_part = parts[0].replace("📋 Guidelines:", "").strip()
                tools_part = parts[1].strip() if len(parts) > 1 else ""
                
                formatted = []
                if guidelines_part:
                    formatted.append(f"📋 Guidelines: {guidelines_part}")
                if tools_part:
                    formatted.append(f"🔧 Tools: {tools_part}")
                return '\n'.join(formatted)
            
            # For other reasoning content
            if len(text) > 35:  # Shorter lines for reasoning column
                words = text.split()
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) > 35:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                    else:
                        current_line += " " + word if current_line else word
                if current_line:
                    lines.append(current_line)
                return '\n'.join(lines)
            return text
        
        table.add_row(
            format_query_text(query),
            format_traditional_text(traditional),
            format_parlant_text(parlant),
            format_reasoning_text(reasoning_text)
        )
    
    console.print(table)
