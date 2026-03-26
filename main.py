import os

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agent import research

console = Console()


def main():
    console.print(Panel("[bold cyan]Deep Research - 智能研究助手[/bold cyan]", expand=False))
    console.print()

    question = console.input("[bold green]请输入你的研究问题:[/bold green] ")
    if not question.strip():
        console.print("[red]问题不能为空[/red]")
        return

    console.print()

    def on_status(msg):
        if msg == "decompose":
            console.print("[yellow]正在拆解问题...[/yellow]")
        elif isinstance(msg, tuple) and msg[0] == "sub_questions":
            for i, sq in enumerate(msg[1], 1):
                console.print(f"  [cyan]{i}. {sq}[/cyan]")
            console.print()
        elif isinstance(msg, tuple) and msg[0] == "searching":
            console.print(f"[yellow]正在搜索:[/yellow] {msg[1]}")
        elif isinstance(msg, tuple) and msg[0] == "search_done":
            console.print(f"  [dim]找到 {msg[1]} 条结果，正在抓取前 3 个网页...[/dim]")
        elif msg == "generating":
            console.print()
            console.print("[yellow]正在生成研究报告...[/yellow]")
            console.print()
        elif msg == "no_materials":
            console.print()
            console.print("[red]所有搜索均失败，未获取到资料。[/red]")

    report = research(question, on_status=on_status)

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
