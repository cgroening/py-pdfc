from pathlib import Path
from pdfc.domain.models import CompressionSettings
from pdfc.storage.pdf_compressor import PdfCompressor


# ---------------------------------------------------------------------------
# Compare configurations (non-commented configs from both reference scripts)
# ---------------------------------------------------------------------------

# Each dict maps directly to CompressionSettings keyword arguments.
# 'name' is used as the output filename stem.
_COMPARE_CONFIGS: list[dict] = [
    # --- B&W · PNG ---
    {'name': 'bw-png-thresh150',
     '_mode': 'bw', '_bw_threshold': 150, '_png_compression': 6},
    {'name': 'bw-png-thresh180',
     '_mode': 'bw', '_bw_threshold': 180, '_png_compression': 6},
    {'name': 'bw-png-thresh180-sharp',
     '_mode': 'bw', '_bw_threshold': 180, '_png_compression': 6, '_sharpen': 1.5},
    {'name': 'bw-png-thresh180-contrast',
     '_mode': 'bw', '_bw_threshold': 180, '_png_compression': 6, '_contrast': 1.5},
    {'name': 'bw-png-thresh180-unsharp',
     '_mode': 'bw', '_bw_threshold': 180, '_png_compression': 6, '_unsharp_mask': True},
    {'name': 'bw-png-thresh180-sharp-contrast',
     '_mode': 'bw', '_bw_threshold': 180, '_png_compression': 6,
     '_sharpen': 1.5, '_contrast': 1.5},
    {'name': 'bw-png-thresh180-sharp-unsharp',
     '_mode': 'bw', '_bw_threshold': 180, '_png_compression': 6,
     '_sharpen': 1.5, '_unsharp_mask': True},
    {'name': 'bw-png-thresh180-sharp-contrast-unsharp',
     '_mode': 'bw', '_bw_threshold': 180, '_png_compression': 6,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    {'name': 'bw-png-thresh150-sharp-contrast-unsharp',
     '_mode': 'bw', '_bw_threshold': 150, '_png_compression': 6,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    {'name': 'bw-png-thresh150-sharp-contrast2-unsharp',
     '_mode': 'bw', '_bw_threshold': 150, '_png_compression': 6,
     '_sharpen': 1.5, '_contrast': 2.0, '_unsharp_mask': True},
    # --- B&W · JPEG ---
    {'name': 'bw-jpeg30-thresh150-sharp-contrast2-unsharp',
     '_mode': 'bw', '_bw_threshold': 150, '_jpeg_quality': 30,
     '_sharpen': 1.5, '_contrast': 2.0, '_unsharp_mask': True},
    {'name': 'bw-jpeg20-thresh180-sharp-contrast2-unsharp',
     '_mode': 'bw', '_bw_threshold': 180, '_jpeg_quality': 20,
     '_sharpen': 1.5, '_contrast': 2.0, '_unsharp_mask': True},
    # --- B&W · TIFF CCITT Group 4 ---
    {'name': 'bw-tiff-thresh150-minimal',
     '_mode': 'bw', '_bw_threshold': 150, '_tiff_ccitt': True},
    {'name': 'bw-tiff-thresh150-sharp-contrast2-unsharp',
     '_mode': 'bw', '_bw_threshold': 150, '_tiff_ccitt': True,
     '_sharpen': 1.5, '_contrast': 2.0, '_unsharp_mask': True},
    {'name': 'bw-tiff-thresh180-minimal',
     '_mode': 'bw', '_bw_threshold': 180, '_tiff_ccitt': True},
    {'name': 'bw-tiff-thresh180-sharp-contrast2-unsharp',
     '_mode': 'bw', '_bw_threshold': 180, '_tiff_ccitt': True,
     '_sharpen': 1.5, '_contrast': 2.0, '_unsharp_mask': True},
    {'name': 'bw-tiff-thresh190-sharp-contrast2-unsharp',
     '_mode': 'bw', '_bw_threshold': 190, '_tiff_ccitt': True,
     '_sharpen': 1.5, '_contrast': 2.0, '_unsharp_mask': True},
    # --- Grayscale ---
    {'name': 'gray-baseline',
     '_mode': 'gray', '_jpeg_quality': 30},
    {'name': 'gray-jpeg20-sharp-contrast-unsharp',
     '_mode': 'gray', '_jpeg_quality': 20,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    {'name': 'gray-jpeg35-sharp-contrast-unsharp',
     '_mode': 'gray', '_jpeg_quality': 35,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    {'name': 'gray-jpeg50-sharp-contrast-unsharp',
     '_mode': 'gray', '_jpeg_quality': 50,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    {'name': 'gray-png-sharp-contrast-unsharp',
     '_mode': 'gray', '_png_compression': 6,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    # --- Color ---
    {'name': 'color-baseline',
     '_mode': 'color', '_jpeg_quality': 30},
    {'name': 'color-jpeg20-sharp-contrast-unsharp',
     '_mode': 'color', '_jpeg_quality': 20,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    {'name': 'color-jpeg35-sharp-contrast-unsharp',
     '_mode': 'color', '_jpeg_quality': 35,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    {'name': 'color-jpeg50-sharp-contrast-unsharp',
     '_mode': 'color', '_jpeg_quality': 50,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
    {'name': 'color-jpeg70',
     '_mode': 'color', '_jpeg_quality': 70},
    {'name': 'color-png-sharp-contrast-unsharp',
     '_mode': 'color', '_png_compression': 6,
     '_sharpen': 1.5, '_contrast': 1.5, '_unsharp_mask': True},
]


class CompressionService:
    """
    Orchestrates compression and comparison workflows.

    Knows the storage layer only via the PdfCompressor interface; does not
    depend on CLI layer or domain validation details.
    """

    def __init__(self, compressor: PdfCompressor) -> None:
        self._compressor = compressor

    # ------------------------------------------------------------------
    # Compression
    # ------------------------------------------------------------------

    def validate(self, settings: CompressionSettings) -> None:
        """Delegates validation to the domain model."""
        settings.validate()

    def compress_file(
        self,
        input_path: Path,
        output_path: Path,
        settings: CompressionSettings,
    ) -> None:
        """Compresses a single PDF file."""
        self._compressor.compress(input_path, output_path, settings)

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def get_pdf_files(self, path: Path) -> list[Path]:
        """
        Returns all PDF files at *path*.

        If *path* is a file, returns ``[path]``.
        If *path* is a directory, returns all PDFs found recursively.

        Raises
        ------
        ValueError
            If the path does not exist or is not a PDF file.
        """
        if path.is_file():
            if path.suffix.lower() != '.pdf':
                raise ValueError(f'File is not a PDF: {path}')
            return [path]
        if path.is_dir():
            files = sorted(path.rglob('*.pdf')) + sorted(path.rglob('*.PDF'))
            # Remove duplicates that differ only in case on case-insensitive FSes
            seen: set[Path] = set()
            unique: list[Path] = []
            for f in files:
                if f not in seen:
                    seen.add(f)
                    unique.append(f)
            return unique
        raise ValueError(f'Path does not exist: {path}')

    def get_compress_output_path(
        self,
        pdf_path: Path,
        explicit_output: Path | None,
    ) -> Path:
        """
        Returns the output path for a single-file compress operation.

        Uses *explicit_output* when provided; otherwise appends
        ``-compressed`` to the stem of *pdf_path*.
        """
        if explicit_output is not None:
            return explicit_output
        return pdf_path.parent / f'{pdf_path.stem}-compressed.pdf'

    def get_compare_output_dir(self, pdf_path: Path) -> Path:
        """Returns the comparison output directory for *pdf_path*."""
        return pdf_path.parent / pdf_path.stem

    # ------------------------------------------------------------------
    # Compare
    # ------------------------------------------------------------------

    def get_compare_configs(self, dpi: int) -> list[tuple[str, CompressionSettings]]:
        """
        Returns all comparison configurations as (name, settings) pairs
        with the given DPI applied to each.
        """
        result: list[tuple[str, CompressionSettings]] = []
        for cfg in _COMPARE_CONFIGS:
            params = {k: v for k, v in cfg.items() if k != 'name'}
            params['_dpi'] = dpi
            result.append((cfg['name'], CompressionSettings(**params)))
        return result
