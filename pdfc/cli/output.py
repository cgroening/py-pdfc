import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pdfc.domain.models import CompressionSettings


console = Console()


def print_error(message: str) -> None:
    """Prints an error message in a red panel using Rich."""
    print_panel(f'✗ {message}', 'red')


def print_warning(message: str) -> None:
    """Prints a warning message in a yellow panel using Rich."""
    print_panel(f'⚠ {message}', 'yellow')


def print_success(message: str) -> None:
    """Prints a success message in a green panel using Rich."""
    print_panel(f'✓ {message}', 'green')


def print_info(message: str) -> None:
    """Prints an info message in a cyan panel using Rich."""
    print_panel(f'ℹ {message}', 'cyan')


def print_panel(message: str, color: str) -> None:
    """Prints a message in a red panel with the given color using Rich."""
    formatted_message = f'[{color} bold]{message}[/{color} bold]'
    print_custom_panel(formatted_message, color)


def print_custom_panel(formatted_message: str, panel_color: str) -> None:
    """
    Prints a custom formatted message in a panel with the given color
    using Rich.
    """
    console.print(Panel(
        formatted_message,
        border_style=panel_color,
        padding=(1, 2)
    ))


def clear_lines(count: int) -> None:
    """Move cursor up `count` lines and clear everything below."""
    sys.stdout.write(f'\033[{count}A\033[0J')
    sys.stdout.flush()


def print_skipped_files(title: str, files: list[str]) -> None:
    """Prints a yellow panel with a title and an indented list of filenames."""
    items = '\n'.join(f'  - {f}' for f in files)
    message = f'[yellow bold]⚠ {title}[/yellow bold]\n{items}'
    print_custom_panel(message, 'yellow')


def get_arrow_depending_on_sign(
    value: int | float, round_decimals: int = 0
) -> str:
    """Returns an arrow symbol based on the sign of the value. The value is
    rounded to the specified number of decimals before determining the sign.

     - '↑' for negative values
     - '↓' for positive values
     - ' ' for zero
    """
    value = round(value, round_decimals)
    if value < 0:
        return '[red]↑[/red]'
    elif value > 0:
        return '[green]↓[/green]'
    else:
        return ' '


def print_file_section_header(file_path: Path, file_size_bytes: int) -> None:
    """Prints a horizontal rule with the filename and size in KB."""
    size_kb = file_size_bytes / 1024
    console.print()
    console.rule(
        f'[cyan bold]{file_path.name}[/cyan bold] '
        f'[cyan]([/cyan][green]{size_kb:.0f} KB[/green][cyan])[/cyan]'
    )


def print_file_paths(
    source: Path, target: Path, target_is_generated: bool = False
) -> None:
    """Prints source and target paths as indented text lines."""
    console.print(f'  [dim]Source:[/dim] {source}')
    if target_is_generated:
        console.print(
            f'  [dim]Target:[/dim] {target} [yellow](auto-generated)[/yellow]'
        )
    else:
        console.print(f'  [dim]Target:[/dim] {target}')


def print_result_ok(name: str, size_kb: float, savings: float) -> None:
    """Prints a success result line: ✓  name  size KB  (arrow savings %)"""
    console.print(
        f'  [green]✓[/green]  [cyan]{name:<45}[/cyan] '
        f'[green]{size_kb:>8.0f} KB[/green]  '
        f'({get_arrow_depending_on_sign(savings)}{abs(savings):.0f} %)'
    )


def print_result_error(name: str, error: str) -> None:
    """Prints an error result line: ✗  name  error message"""
    console.print(
        f'  [red]✗[/red]  [cyan]{name:<45}[/cyan] '
        f'[red]{error}[/red]'
    )


def print_summary(items: list[tuple[str, str]]) -> None:
    """Prints a summary table after a horizontal rule."""
    console.rule()
    table = Table(show_header=False, box=None)
    table.add_column('', style='dim')
    table.add_column('', style='bold')
    for label, value in items:
        table.add_row(label, value)
    console.print(table)


def print_presets_table(
    presets: list[tuple[str, CompressionSettings]], input_path: Path
) -> None:
    """
    Prints all presets in a table like view. Shows the input path first (if
    given), then a header row, a separator and for each preset its name followed
    by its settings values - all separated by `|`with aligned column widths.

    Columns: Mode, DPI, FMT, Q/L, BW Thr, Sharp, Cont, Unsharp, CCITT

    The Q/L column shows JPEG quality for JPEG format, PNG level for PNG
    format or `-` for TIFF CCITT - denpending on what is applicable.

    Example
    -------
    Input: /path/to/folder

    Mode      | DPI | FMT  | Q/L | BW Thr | Sharp | Cont | Unsh. | CCITT
    ──────────────────────────────────────────────────────────────────────
    bw-300-sharp:
    B&W       | 300 | JPEG |  20 | 128    | 0.5   | 1.2  | Yes   | No
    gray-150dpi:
    Grayscale | 150 | JPEG |  60 | -      | 0.0   | 1.0  | No    | No
    """
    headers = [
        'Mode', 'DPI', 'FMT', 'Q/L', 'BW Thr', 'Sharp', 'Cont', 'Unsh.', 'CCITT'
    ]
    rows = _create_row_for_presets_table(presets)
    col_widths = _calculate_column_widths_for_presets_table(headers, rows)
    header_str = _fmt_row_for_presets_table(headers, col_widths)

    _print_header_of_presets_table(header_str, input_path)
    _print_rows_of_presets_table(col_widths, rows)


def _create_row_for_presets_table(
    presets: list[tuple[str, CompressionSettings]]
) -> list[tuple[str, list[str]]]:
    """
    Creates a row for each preset in the presets table. Each row contains the
    preset name and a list of its settings values as strings. The Q/L value is
    determined based on the format - it shows JPEG quality for JPEG format, PNG
    level for PNG format or `-` for TIFF CCITT - denpending on what is
    applicable.
    """
    rows: list[tuple[str, list[str]]] = []
    for name, preset_settings in presets:
        preset_settings: CompressionSettings
        quality_or_level = (
            preset_settings.jpeg_quality_as_str
            if preset_settings.jpeg_quality_as_str != '-'
            else preset_settings.png_level_as_str
        )
        rows.append(
            (
                name,
                [
                    preset_settings.mode_as_str,
                    preset_settings.dpi_as_str,
                    preset_settings.format_as_str,
                    quality_or_level,
                    preset_settings.bw_threshold_as_str,
                    preset_settings.sharpen_as_str,
                    preset_settings.contrast_as_str,
                    preset_settings.unsharp_mask_as_str,
                    preset_settings.tiff_ccitt_as_str,
                ]
            )
        )
    return rows


def _calculate_column_widths_for_presets_table(headers, rows) -> list[int]:
    """
    Calculates the maximum width for each column in the presets table based on
    the header and the values in each row. This is used to align the columns
    when printing the table.
    """
    column_widths = [len(h) for h in headers]
    for _, values in rows:
        for i, v in enumerate(values):
            display_value = '-' if v == 'TIFF CCITT' else v
            column_widths[i] = max(column_widths[i], len(display_value))
    return column_widths


def _fmt_row_for_presets_table(cells: list[str], col_widths: list[int]) -> str:
    """
    Formats a row for the presets table by padding each cell to the
    corresponding column width and applying color based on the cell value.
    """
    parts = []
    for i, value in enumerate(cells):
        display_value = '-' if value == 'TIFF CCITT' else value
        padded_value = display_value.ljust(col_widths[i])
        if is_number(value):
            parts.append(f'[blue]{padded_value}[/blue]')
        elif value == 'Yes':
            parts.append(f'[green dim]{padded_value}[/green dim]')
        elif value == 'No':
            parts.append(f'[dim]{padded_value}[/dim]')
        else:
            parts.append(padded_value)
    return ' | '.join(parts)


def _print_header_of_presets_table(header_str, input_path: Path):
    console.print(f'[dim]Input:[/dim] {input_path}\n')
    console.print(f'[bold]{header_str}[/bold]')
    print('─' * len(header_str))


def _print_rows_of_presets_table(col_widths, rows):
    for name, values in rows:
        console.print(f'[dim]{name}:[/dim]')
        console.print(
            f'{_fmt_row_for_presets_table(values, col_widths)}',
            highlight=False  # Prevent numbers from being formatted as bold
        )
    console.print()


# TODO: Move this to util layer
def is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False
