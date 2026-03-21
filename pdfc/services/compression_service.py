from pathlib import Path
from pdfc.domain.models import CompressionSettings
from pdfc.storage.pdf_compressor import PdfCompressor
from pdfc.storage.presets_storage import PresetsStorage


class CompressionService:
    """
    Orchestrates compression and comparison workflows.
    """

    def __init__(
        self, compressor: PdfCompressor, presets_storage: PresetsStorage,
    ) -> None:
        self._compressor = compressor
        self._presets = presets_storage

    def validate(self, settings: CompressionSettings | None) -> None:
        """Delegates validation to the domain model."""
        if not settings:
            raise ValueError('Compression settings are required.')
        else:
            settings.validate()

    def compress_file(
        self, input_path: Path, output_path: Path,
        compression_settings: CompressionSettings,
    ) -> None:
        """Compresses a single PDF file."""
        self._compressor.compress(input_path, output_path, compression_settings)

    def get_pdf_files(self, path: Path) -> list[Path]:
        """
        Returns a list of all PDF files at `path`. If `path` is a file, the list
        will contain just that file.

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
            seen: set[Path] = set()
            unique: list[Path] = []
            for f in files:
                if f not in seen:
                    seen.add(f)
                    unique.append(f)
            return unique
        raise ValueError(f'Path does not exist: {path}')

    def get_output_path(
        self, input_path: Path, output_path: Path | None,
    ) -> Path:
        """
        Returns `output_path` as is if not `None`, otherwise returns a path in
        the same directory as `input_path` with '-compressed' appended to the
        input file name.
        """
        if isinstance(output_path, Path):
            return output_path
        return input_path.parent / f'{input_path.stem}-compressed.pdf'

    def get_compare_output_dir(self, pdf_input_path: Path) -> Path:
        """Returns the comparison output directory for `pdf_path`."""
        return pdf_input_path.parent / pdf_input_path.stem

    def get_compare_configs(self, dpi: int) -> list[tuple[str, CompressionSettings]]:
        """
        Loads presets from storage and returns them as (name, settings) pairs
        with the given DPI applied to each (if DPI is not defined in config).

        Raises
        ------
        FileNotFoundError
            If the presets file does not exist.
        ValueError
            If the presets file is malformed.
        """
        raw = self._presets.load()
        result: list[tuple[str, CompressionSettings]] = []
        for cfg in raw:
            params = {k: v for k, v in cfg.items() if k != 'name'}
            if '_dpi' not in params:   # CLI --dpi is only a fallback
                params['_dpi'] = dpi
            result.append((cfg['name'], CompressionSettings(**params)))
        return result

