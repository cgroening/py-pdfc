from pathlib import Path
from pdfc.domain.models import CompressionSettings


class CompressionError(Exception):
    """Raised when compression fails."""
    _input_path: Path
    _output_path: Path
    _compression_settings: CompressionSettings
    _error_message: str

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        compression_settings: CompressionSettings,
        error_message: str
    ) -> None:
        self._input_path = input_path
        self._output_path = output_path
        self._compression_settings = compression_settings
        self._error_message = error_message
        super().__init__(str(self))

    def __str__(self) -> str:
        return (
            f'An error occurred while compressing\n\n{self._input_path} to\n\n'
            f'{self._output_path} with settings:\n\n '
            f'{self._compression_settings}\n\nError Message:\n\n'
            f'{self._error_message}'
    )
