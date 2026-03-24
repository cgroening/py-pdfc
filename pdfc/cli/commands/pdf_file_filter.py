from pathlib import Path

from pdfc.cli.output import print_skipped_files


def filter_already_compressed_files(pdf_files: list[Path]) -> list[Path]:
    """
    Filters out PDF files that are already compressed, i.e. files whose name
    ends with `-compressed` or that reside inside a directory ending with
    `-compressed`. Prints a warning panel for each group of skipped items.
    """
    filtered = []
    skipped_files = []
    skipped_dir_files = []
    for f in pdf_files:
        if f.stem.endswith('-compressed'):
            skipped_files.append(f.name)
        elif any(part.endswith('-compressed') for part in f.parts[:-1]):
            dir_name = next(
                p for p in f.parts[:-1] if p.endswith('-compressed')
            )
            if dir_name not in skipped_dir_files:
                skipped_dir_files.append(dir_name)
        else:
            filtered.append(f)
    if skipped_files:
        print_skipped_files('Skipping already compressed files:', skipped_files)
    if skipped_dir_files:
        print_skipped_files(
            'Skipping directories with already compressed files:',
            skipped_dir_files
        )
    return filtered
