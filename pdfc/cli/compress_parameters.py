from dataclasses import dataclass
from pathlib import Path
from pdfc.domain.models import CompressionSettings


@dataclass
class CompressRequest:
    interactive_mode: bool
    input_path: Path
    output_path: Path | None = None
    compression_settings: CompressionSettings | None = None
