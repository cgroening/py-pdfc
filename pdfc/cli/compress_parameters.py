from dataclasses import dataclass
from pathlib import Path
from pdfc.domain.models import CompressionSettings


@dataclass
class CompressRequest:
    interactive_mode: bool
    input_path: Path
    compression_settings: CompressionSettings
    output_path: Path | None = None
    no_skip: bool = False


    def input_path_is_directory(self) -> bool:
        return self.input_path.is_dir()
