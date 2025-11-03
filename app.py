#!/usr/bin/env python3
"""
imgtool_cli.py - Interactive CLI for batch image processing
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Optional
import glob
import shlex
import argparse

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Run: pip install prompt-toolkit pygments rich")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


# ============= Core Image Processing Functions =============

def parse_hex_color(hex_str: str) -> Tuple[int, int, int]:
    """Parse HEX color (#RGB or #RRGGBB) to (R, G, B) tuple."""
    hex_str = hex_str.strip().upper()
    if hex_str.startswith('#'):
        hex_str = hex_str[1:]

    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])

    if len(hex_str) != 6:
        raise ValueError(f"Invalid HEX color: #{hex_str}")

    return (
        int(hex_str[0:2], 16),
        int(hex_str[2:4], 16),
        int(hex_str[4:6], 16)
    )


def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """Calculate RGB Euclidean distance."""
    return ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2) ** 0.5


def remove_colors(
    img: Image.Image,
    colors: List[Tuple[int, int, int]],
    tolerance: int
) -> Image.Image:
    """Remove colors by setting alpha to 0."""
    if not colors:
        return img

    img = img.convert('RGBA')
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            for target_color in colors:
                if color_distance((r, g, b), target_color) <= tolerance:
                    pixels[x, y] = (r, g, b, 0)
                    break

    return img


def resize_image(img: Image.Image, size: Optional[int], keep_aspect: bool) -> Image.Image:
    """Resize image. If size is None, return original image."""
    if size is None:
        return img

    if not keep_aspect:
        return img.resize((size, size), Image.LANCZOS)

    img.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    offset_x = (size - img.width) // 2
    offset_y = (size - img.height) // 2
    canvas.paste(img, (offset_x, offset_y), img if img.mode == 'RGBA' else None)
    return canvas


def process_image(
    input_path: Path,
    output_dir: Path,
    size: Optional[int],
    colors_to_remove: List[Tuple[int, int, int]],
    tolerance: int,
    keep_aspect: bool,
    suffix: str,
    overwrite: bool
) -> bool:
    """Process single image."""
    try:
        img = Image.open(input_path).convert('RGBA')
        img = resize_image(img, size, keep_aspect)
        img = remove_colors(img, colors_to_remove, tolerance)

        output_name = input_path.stem + suffix + '.png'
        output_path = output_dir / output_name

        if output_path.exists() and not overwrite:
            return False

        img.save(output_path, 'PNG', optimize=True, compress_level=6)
        return True
    except Exception:
        return False


# ============= Interactive CLI =============

class ImgToolCLI:
    def __init__(self):
        self.console = Console()
        self.commands = {
            'magic': 'All-in-one: resize + remove colors + optimize (shortcut)',
            'process': 'Process images with all options (advanced)',
            'resize': 'Quick resize only',
            'remove-color': 'Quick remove color only',
            'preview': 'Preview files matching pattern',
            'help': 'Show available commands',
            'examples': 'Show usage examples',
            'clear': 'Clear screen',
            'exit': 'Exit CLI',
            'quit': 'Exit CLI'
        }

        self.style = Style.from_dict({
            'prompt': '#00d7ff bold',
            'command': '#00ff87',
        })

        command_completer = WordCompleter(
            list(self.commands.keys()) +
            ['--input', '--output', '--size', '--remove-color', '--tolerance',
             '--keep-aspect', '--suffix', '--overwrite'],
            ignore_case=True
        )

        # Try to create prompt session, fallback to basic input if fails
        try:
            self.session = PromptSession(
                completer=command_completer,
                style=self.style,
                enable_history_search=True,
                auto_suggest=AutoSuggestFromHistory()  # Hiện gợi ý mờ mờ từ history
            )
            self.use_prompt_toolkit = True
        except Exception:
            self.session = None
            self.use_prompt_toolkit = False

    def print_banner(self):
        """Print welcome banner with gradient ASCII art."""
        logo = r"""
[bold #FF1493]  ___                 [/][bold #FF69B4] _____           [/][bold #FFB6C1]_
[bold #FF1493] |_ _|_ __ ___   __ _ [/][bold #FF69B4]|_   _|__   ___ [/][bold #FFB6C1]| |
[bold #FF1493]  | || '_ ` _ \ / _` |[/][bold #FF69B4]  | |/ _ \ / _ \[/][bold #FFB6C1]| |
[bold #FF1493]  | || | | | | | (_| |[/][bold #FF69B4]  | | (_) | (_) |[/][bold #FFB6C1]|_|
[bold #FF1493] |___|_| |_| |_|\__, |[/][bold #FF69B4]  |_|\___/ \___/[/][bold #FFB6C1](_)
[bold #FF1493]                |___/ [/]
"""

        self.console.print(logo)
        self.console.print("[dim]" + "=" * 60 + "[/dim]")
        self.console.print("[bold cyan]Interactive Image Processor[/bold cyan] - Batch resize & remove colors\n")

        tips = Panel(
            "[dim]1. Type [cyan]help[/cyan] for available commands\n"
            "2. Type [cyan]examples[/cyan] for usage examples\n"
            "3. Press [yellow]Tab[/yellow] for autocomplete\n"
            "4. Press [yellow]Right Arrow[/yellow] to accept gray suggestions[/dim]",
            title="[bold green]Tips for getting started[/bold green]",
            border_style="dim",
            padding=(0, 1)
        )
        self.console.print(tips)
        self.console.print()

    def print_help(self):
        """Print help table."""
        table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", width=20)
        table.add_column("Description", style="white")

        for cmd, desc in self.commands.items():
            table.add_row(cmd, desc)

        self.console.print(table)

        flags_table = Table(title="\nCommon Flags", show_header=True, header_style="bold yellow")
        flags_table.add_column("Flag", style="green")
        flags_table.add_column("Description", style="white")

        flags = [
            ("--input", "Input pattern (e.g., ./icons/*.png)"),
            ("--output", "Output directory"),
            ("--size", "Target size (default: 48)"),
            ("--remove-color", "HEX colors to remove"),
            ("--tolerance", "Color tolerance 0-255 (default: 0)"),
            ("--keep-aspect", "Keep aspect ratio"),
            ("--suffix", "Filename suffix (e.g., _48)"),
            ("--overwrite", "Overwrite existing files"),
        ]

        for flag, desc in flags:
            flags_table.add_row(flag, desc)

        self.console.print(flags_table)

    def print_examples(self):
        """Print usage examples."""
        examples = [
            ("MAGIC: All-in-one (resize + remove colors + optimize)",
             "magic ./icons/*.png ./output 64 #FFFFFF,#000000 10"),

            ("MAGIC: Single file only",
             "magic ./photo.png ./output 512 #FFFFFF 10"),

            ("Preview files before processing",
             "preview ./images/**/*.png"),

            ("Quick resize to 64x64",
             "resize ./icons/*.png ./output 64"),

            ("Quick remove white background",
             "remove-color ./images/*.png ./output #FFFFFF"),

            ("Advanced: Resize with all options",
             "process --input ./icons/*.png --output ./output --size 48 --keep-aspect"),

            ("Advanced: Remove multiple colors with tolerance",
             "process --input ./raw/*.png --output ./output --remove-color #FF00FF,#000000 --tolerance 10"),
        ]

        self.console.print("\n[bold cyan]Usage Examples:[/bold cyan]\n")

        for i, (desc, cmd) in enumerate(examples, 1):
            panel = Panel(
                f"[yellow]{cmd}[/yellow]",
                title=f"[green]{i}. {desc}[/green]",
                border_style="blue"
            )
            self.console.print(panel)

    def preview_files(self, pattern: str):
        """Preview files matching pattern."""
        files = [Path(p) for p in glob.glob(pattern, recursive=True) if Path(p).is_file()]

        if not files:
            self.console.print(f"[yellow]No files found matching:[/yellow] {pattern}")
            return

        table = Table(title=f"Found {len(files)} file(s)", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Dimensions", style="magenta")

        for f in files[:20]:  # Limit to 20 for display
            try:
                size_kb = f.stat().st_size / 1024
                img = Image.open(f)
                dims = f"{img.width}x{img.height}"
                table.add_row(f.name, f"{size_kb:.1f} KB", dims)
            except:
                table.add_row(f.name, "?", "?")

        if len(files) > 20:
            table.add_row("...", f"+ {len(files)-20} more", "...")

        self.console.print(table)

    def parse_process_args(self, args_str: str) -> Optional[dict]:
        """Parse process command arguments."""
        try:
            parts = shlex.split(args_str)
            args = {}
            i = 0

            while i < len(parts):
                part = parts[i]

                if part == '--input' and i+1 < len(parts):
                    args['input'] = parts[i+1]
                    i += 2
                elif part == '--output' and i+1 < len(parts):
                    args['output'] = parts[i+1]
                    i += 2
                elif part == '--size' and i+1 < len(parts):
                    args['size'] = int(parts[i+1])
                    i += 2
                elif part == '--remove-color' and i+1 < len(parts):
                    args.setdefault('remove_colors', []).append(parts[i+1])
                    i += 2
                elif part == '--tolerance' and i+1 < len(parts):
                    args['tolerance'] = int(parts[i+1])
                    i += 2
                elif part == '--suffix' and i+1 < len(parts):
                    args['suffix'] = parts[i+1]
                    i += 2
                elif part == '--keep-aspect':
                    args['keep_aspect'] = True
                    i += 1
                elif part == '--overwrite':
                    args['overwrite'] = True
                    i += 1
                else:
                    i += 1

            # Set defaults
            args.setdefault('size', 48)
            args.setdefault('tolerance', 0)
            args.setdefault('suffix', '')
            args.setdefault('keep_aspect', False)
            args.setdefault('overwrite', False)
            args.setdefault('remove_colors', [])

            if 'input' not in args or 'output' not in args:
                self.console.print("[red]Error:[/red] --input and --output are required")
                return None

            return args

        except Exception as e:
            self.console.print(f"[red]Error parsing arguments:[/red] {e}")
            return None

    def execute_process(self, args: dict):
        """Execute batch processing."""
        # Parse colors
        colors_to_remove = []
        for color_arg in args['remove_colors']:
            for color_str in color_arg.split(','):
                color_str = color_str.strip()
                if color_str:
                    try:
                        colors_to_remove.append(parse_hex_color(color_str))
                    except ValueError as e:
                        self.console.print(f"[red]X Error:[/red] {e}")
                        return

        # Find files
        input_files = [Path(p) for p in glob.glob(args['input'], recursive=True) if Path(p).is_file()]

        if not input_files:
            self.console.print(f"[yellow]! No files found matching:[/yellow] {args['input']}")
            return

        # Create output dir
        output_dir = Path(args['output'])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Show processing info in a nice panel
        info_lines = [
            f"[cyan]Files found:[/cyan] {len(input_files)}",
            f"[cyan]Target size:[/cyan] {args['size']}x{args['size']}",
        ]
        if colors_to_remove:
            color_strs = [f"#{r:02X}{g:02X}{b:02X}" for r,g,b in colors_to_remove]
            info_lines.append(f"[magenta]Removing colors:[/magenta] {', '.join(color_strs)}")
        if args['keep_aspect']:
            info_lines.append("[yellow]Mode:[/yellow] Keep aspect ratio")

        info_panel = Panel(
            "\n".join(info_lines),
            title="[bold]Processing Configuration[/bold]",
            border_style="cyan",
            padding=(0, 1)
        )
        self.console.print(info_panel)

        success_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Processing...", total=len(input_files))

            for input_path in input_files:
                if process_image(
                    input_path,
                    output_dir,
                    args['size'],
                    colors_to_remove,
                    args['tolerance'],
                    args['keep_aspect'],
                    args['suffix'],
                    args['overwrite']
                ):
                    success_count += 1
                    progress.update(task, advance=1, description=f"[green]OK[/green] {input_path.name}")
                else:
                    progress.update(task, advance=1, description=f"[yellow]SKIP[/yellow] {input_path.name}")

        # Summary
        panel = Panel(
            f"[green]Success:[/green] {success_count}/{len(input_files)} files\n"
            f"[cyan]Output:[/cyan] {output_dir.absolute()}",
            title="[bold green]Complete[/bold green]",
            border_style="green"
        )
        self.console.print(panel)

    def run(self):
        """Run interactive CLI."""
        self.print_banner()

        if not self.use_prompt_toolkit:
            self.console.print("[yellow]Note: Running in basic mode (autocomplete disabled)[/yellow]\n")

        while True:
            try:
                # Use prompt_toolkit if available, else fallback to input()
                if self.use_prompt_toolkit:
                    prompt_text = HTML('<prompt>> </prompt>')
                    user_input = self.session.prompt(prompt_text).strip()
                else:
                    self.console.print("[bold #00d7ff]>[/bold #00d7ff] ", end="")
                    user_input = input().strip()

                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args_str = parts[1] if len(parts) > 1 else ''

                if command in ['exit', 'quit']:
                    self.console.print("\n[bold cyan]Thanks for using ImgTool![/bold cyan]\n")
                    break

                elif command == 'help':
                    self.console.print()
                    self.print_help()
                    self.console.print()

                elif command == 'examples':
                    self.print_examples()

                elif command == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.print_banner()

                elif command == 'preview':
                    if args_str:
                        self.console.print()
                        self.preview_files(args_str)
                        self.console.print()
                    else:
                        self.console.print("[yellow]Usage:[/yellow] preview <pattern>")

                elif command == 'process':
                    args = self.parse_process_args(args_str)
                    if args:
                        self.execute_process(args)

                elif command == 'resize':
                    # Quick resize: resize <input> <output> <size>
                    quick_parts = shlex.split(args_str)
                    if len(quick_parts) >= 3:
                        args = {
                            'input': quick_parts[0],
                            'output': quick_parts[1],
                            'size': int(quick_parts[2]),
                            'tolerance': 0,
                            'suffix': '',
                            'keep_aspect': False,
                            'overwrite': True,
                            'remove_colors': []
                        }
                        self.execute_process(args)
                    else:
                        self.console.print("[yellow]Usage:[/yellow] resize <input> <output> <size>")

                elif command == 'remove-color':
                    # Quick color removal: remove-color <input> <output> <hex>
                    quick_parts = shlex.split(args_str)
                    if len(quick_parts) >= 3:
                        args = {
                            'input': quick_parts[0],
                            'output': quick_parts[1],
                            'size': 48,
                            'tolerance': 0,
                            'suffix': '',
                            'keep_aspect': False,
                            'overwrite': True,
                            'remove_colors': [quick_parts[2]]
                        }
                        self.execute_process(args)
                    else:
                        self.console.print("[yellow]Usage:[/yellow] remove-color <input> <output> <hex>")

                elif command == 'magic':
                    # All-in-one magic command: magic <input> <output> <size> <hex_colors> [tolerance]
                    # Example: magic ./in/*.png ./out 64 #FFFFFF,#000000 10
                    quick_parts = shlex.split(args_str)
                    if len(quick_parts) >= 4:
                        tolerance = int(quick_parts[4]) if len(quick_parts) >= 5 else 10
                        args = {
                            'input': quick_parts[0],
                            'output': quick_parts[1],
                            'size': int(quick_parts[2]),
                            'tolerance': tolerance,
                            'suffix': '',
                            'keep_aspect': True,  # Keep aspect by default for magic
                            'overwrite': True,
                            'remove_colors': [quick_parts[3]]
                        }
                        self.console.print("\n[bold magenta]* Magic processing...[/bold magenta]")
                        self.execute_process(args)
                    else:
                        self.console.print("[yellow]Usage:[/yellow] magic <input> <output> <size> <hex_colors> [tolerance]")
                        self.console.print("[dim]Example:[/dim] magic ./in/*.png ./out 64 #FFFFFF,#000000 10")

                else:
                    self.console.print(f"\n[red]X Unknown command:[/red] [bold]{command}[/bold]")
                    self.console.print("[dim]Type [green]help[/green] for available commands[/dim]\n")

            except KeyboardInterrupt:
                self.console.print("\n[yellow]! Interrupted. Type 'exit' to quit[/yellow]")
            except EOFError:
                self.console.print("\n[cyan]Goodbye![/cyan]")
                break
            except Exception as e:
                self.console.print(f"\n[red]X Error:[/red] {e}\n")


def parse_cli_args():
    """Parse command-line arguments for direct CLI mode."""
    parser = argparse.ArgumentParser(
        description='ImgTool - Batch image processor (resize & remove colors)',
        epilog='Run without arguments to enter interactive mode.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-i', '--input',
                        help='Input file pattern (e.g., "*.png" or "image.jpg")')
    parser.add_argument('-o', '--output',
                        help='Output directory (default: ./output)')
    parser.add_argument('-s', '--size', type=int,
                        help='Target size in pixels (max width/height)')
    parser.add_argument('-c', '--colors', nargs='+',
                        help='HEX colors to remove (e.g., #FFFFFF #000000)')
    parser.add_argument('-t', '--tolerance', type=int, default=10,
                        help='Color matching tolerance 0-255 (default: 10)')
    parser.add_argument('-k', '--keep-aspect', action='store_true',
                        help='Keep aspect ratio with transparent padding')
    parser.add_argument('--suffix', default='',
                        help='Suffix for output filenames (default: none)')
    parser.add_argument('--overwrite', action='store_true',
                        help='Overwrite existing files without asking')

    return parser.parse_args()


def run_direct_mode(args):
    """Run in direct CLI mode with arguments."""
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel

    console = Console()

    # Validate required arguments
    if not args.input:
        console.print("[red]Error:[/red] --input is required in direct mode")
        console.print("Run [cyan]python app.py --help[/cyan] for usage")
        return False

    # Set defaults
    output_dir = Path(args.output) if args.output else Path('./output')
    output_dir.mkdir(exist_ok=True)

    # In direct mode, default to overwrite=True for convenience
    # User can still opt-out by NOT using --overwrite flag (but that's counterintuitive)
    # So we always overwrite in direct mode
    overwrite = True

    # Parse colors if provided
    colors_to_remove = []
    if args.colors:
        try:
            colors_to_remove = [parse_hex_color(c) for c in args.colors]
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            return False

    # Find input files
    input_pattern = args.input
    if '*' in input_pattern or '?' in input_pattern:
        input_files = [Path(f) for f in glob.glob(input_pattern)]
    else:
        input_files = [Path(input_pattern)]

    if not input_files:
        console.print(f"[yellow]Warning:[/yellow] No files found matching: {input_pattern}")
        return False

    # Process files
    console.print(f"\n[bold cyan]Processing {len(input_files)} file(s)...[/bold cyan]\n")

    success_count = 0
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Processing...", total=len(input_files))

        for input_path in input_files:
            if process_image(
                input_path,
                output_dir,
                args.size,
                colors_to_remove,
                args.tolerance,
                args.keep_aspect,
                args.suffix,
                overwrite  # Use local variable with default True
            ):
                success_count += 1
                progress.update(task, advance=1, description=f"[green]OK[/green] {input_path.name}")
            else:
                progress.update(task, advance=1, description=f"[yellow]SKIP[/yellow] {input_path.name}")

    # Summary
    panel = Panel(
        f"[green]Success:[/green] {success_count}/{len(input_files)} files\n"
        f"[cyan]Output:[/cyan] {output_dir.absolute()}",
        title="[bold green]Complete[/bold green]",
        border_style="green"
    )
    console.print(panel)

    return True


def main():
    """Entry point - supports both interactive and direct CLI modes."""
    args = parse_cli_args()

    # If any argument is provided, run in direct mode
    if args.input or args.output or args.size or args.colors:
        run_direct_mode(args)
    else:
        # No arguments = interactive mode
        cli = ImgToolCLI()
        cli.run()


if __name__ == '__main__':
    main()