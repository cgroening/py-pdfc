"""
Model for person data and business logic.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class CompressionMode(Enum):
    COLOR = 'color'
    GRAY = 'gray'
    BW = 'bw'


@dataclass(slots=True, frozen=True)
class CompressionSettings:
    """Data class for the compression settings."""
    _mode: Optional[str] = None
    dpi: Optional[int] = None
    jpeg_quality: Optional[int] = None
    bw_threshold: Optional[int] = None
    sharpen: Optional[bool] = None
    contrast: Optional[float] = None
    _unsharp_mask: Optional[bool] = None
    png_compression: Optional[int] = None
    _tiff_ccitt: Optional[bool] = None


    def validate(self) -> None:
        """
        Validates the compression settings.
        Raises ValueError if any setting is invalid.
        """
        if self.dpi is not None and (self.dpi <= 0):
            raise ValueError("DPI must be a positive integer.")
        if self.jpeg_quality is not None and not (1 <= self.jpeg_quality <= 100):
            raise ValueError("JPEG quality must be between 1 and 100.")
        if self.bw_threshold is not None and not (0 <= self.bw_threshold <= 255):
            raise ValueError("Threshold must be between 0 and 255.")
        if self.sharpen is not None and not (0.0 <= self.sharpen <= 3.0):
            raise ValueError("Sharpen must be between 0.0 and 3.0.")
        if self.contrast is not None and not (0.0 <= self.contrast <= 3.0):
            raise ValueError("Contrast must be between 0.0 and 3.0.")
        if self.png_compression is not None and not (0 <= self.png_compression <= 9):
            raise ValueError("PNG compression level must be between 0 and 9.")

    def get_mode(self) -> CompressionMode | None:
        """
        Returns the compression mode which can be 'color', 'gray' or 'bw.'
        """
        match self._mode:
            case 'color':
                return CompressionMode.COLOR
            case 'gray':
                return CompressionMode.GRAY
            case 'bw':
                return CompressionMode.BW
            case _:
                return CompressionMode.BW

    def get_unsharp_mask(self) -> bool:
        """
        Returns whether unsharp mask is applied.
        """
        return bool(self._unsharp_mask)

    def get_tiff_ccitt(self) -> bool:
        """
        Returns whether TIFF CCITT compression is applied.
        """
        return bool(self._tiff_ccitt)

