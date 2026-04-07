import os

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agent import research
from config import MEMORY_MODE

console = Console()


def main():
    console.print(Panel(
        "[bold cyan]Deep Research - 智能研究助手[/bold cyan]\n"
        "[dim]基于 LangChain ReAct Agent，支持自主决策研究流程[/dim]",
        expand=False
    ))
    console.print()
    
    # 显示当前配置
    console.print(f"[dim]记忆模式: {MEMORY_MODE}[/dim]")
    console.print()
    
    def on_status(msg):
        if msg == "initializing":
            console.print("[dim]⚙️  初始化研究环境...[/dim]")
        elif msg == "thinking":
            console.print("[dim]🤔 Agent 开始思考...[/dim]")
        elif msg == "done":
            pass  # 最后统一显示
        elif msg == "error":
            console.print("[red]❌ 出现错误[/red]")
        elif isinstance(msg, tuple):
            if msg[0] == "tool_start":
                tool_name = msg[1]
                tool_input = msg[2] if len(msg) > 2 else ""
                # 简化工具名显示
                tool_display = {
                    "search_tool": "🔍 搜索",
                    "scrape_tool": "📄 抓取网页",
                    "rag_retrieve_tool": "🗂️  检索知识库",
                    "analyze_tool": "📊 分析内容"
                }.get(tool_name, tool_name)
                console.print(f"[cyan]{tool_display}[/cyan]: [dim]{tool_input}[/dim]")
            elif msg[0] == "tool_end":
                console.print(f"[green]   ✓ 完成[/green]")
            elif msg[0] == "step":
                console.print(f"[yellow]▶ {msg[1]}[/yellow]")

    while True:
        question = console.input("[bold green]请输入你的研究问题('quit'退出):[/bold green] ")
        if not question.strip():
            console.print("[red]问题不能为空[/red]")
            continue
        
        if question.strip().lower() in ['quit', 'exit', 'q']:
            console.print("[yellow]再见！👋[/yellow]")
            return

        console.print()

        console.print("[yellow]🔍 开始研究...[/yellow]")
        console.print("[dim]Agent 将自主决定搜索策略和研究深度[/dim]")
        console.print()
        
        report = research(question, on_status=on_status)

        console.print()
        console.print("[green]✓ 研究完成![/green]")
        console.print()
        
        # 显示报告
        console.print(Markdown(report))
        console.print()

        # 保存到文件
        os.makedirs("reports", exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "_ -" else "_" for c in question[:50])
        filepath = f"reports/{safe_name}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        console.print(f"[green]报告已保存到 {filepath}[/green]")


if __name__ == "__main__":
    main()
