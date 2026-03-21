from enum import Enum
from dataclasses import dataclass
from typing import Optional


class CompressionMode(Enum):
    COLOR = 'Color'
    GRAY = 'Grayscale'
    BW = 'B&W'


@dataclass(slots=True, frozen=True)
class CompressionSettings:
    _mode: Optional[str] = None
    _dpi: Optional[int] = None
    _jpeg_quality: Optional[int] = None
    _png_compression: Optional[int] = None
    _bw_threshold: Optional[int] = None
    _sharpen: Optional[float] = None
    _contrast: Optional[float] = None
    _unsharp_mask: Optional[bool] = None
    _tiff_ccitt: Optional[bool] = None


    def validate(self) -> None:
        """Validates the compression settings. Raises ValueError if invalid."""
        if self._dpi is not None and self._dpi <= 0:
            raise ValueError('DPI must be a positive integer.')
        if self._jpeg_quality is not None and not (1 <= self._jpeg_quality <= 100):
            raise ValueError('JPEG quality must be between 1 and 100.')
        if self._png_compression is not None and not (0 <= self._png_compression <= 9):
            raise ValueError('PNG compression level must be between 0 and 9.')
        if self._bw_threshold is not None and not (0 <= self._bw_threshold <= 255):
            raise ValueError('Threshold must be between 0 and 255.')
        if self._sharpen is not None and not (0.0 <= self._sharpen <= 3.0):
            raise ValueError('Sharpen must be between 0.0 and 3.0.')
        if self._contrast is not None and not (0.0 <= self._contrast <= 3.0):
            raise ValueError('Contrast must be between 0.0 and 3.0.')

    @property
    def mode(self) -> CompressionMode:
        match self._mode:
            case 'color':
                return CompressionMode.COLOR
            case 'gray':
                return CompressionMode.GRAY
            case _:
                return CompressionMode.BW

    @property
    def dpi(self) -> int:
        return self._dpi if self._dpi is not None else 300

    @property
    def use_png(self) -> bool:
        """
        True if PNG should be used as intermediate format (tiff_ccitt takes
        priority).
        """
        return self._png_compression is not None and not self._tiff_ccitt

    @property
    def jpeg_quality(self) -> int:
        """JPEG quality (1–100). Default: 30."""
        return self._jpeg_quality if self._jpeg_quality is not None else 30

    @property
    def png_compression(self) -> int:
        """PNG compression level (0–9). Default: 6."""
        return self._png_compression if self._png_compression is not None else 6

    @property
    def bw_threshold(self) -> int:
        return self._bw_threshold if self._bw_threshold is not None else 150

    @property
    def sharpen(self) -> float:
        return self._sharpen if self._sharpen is not None else 0.0

    @property
    def contrast(self) -> float:
        return self._contrast if self._contrast is not None else 1.0

    @property
    def unsharp_mask(self) -> bool:
        return bool(self._unsharp_mask)

    @property
    def tiff_ccitt(self) -> bool:
        return bool(self._tiff_ccitt)

    @property
    def mode_as_str(self) -> str:
        return self.mode.value

    @property
    def dpi_as_str(self) -> str:
        return str(self.dpi)

    @property
    def format_as_str(self) -> str:
        if self.tiff_ccitt:
            return 'TIFF CCITT'
        elif self.use_png:
            return 'PNG'
        else:
            return 'JPEG'

    @property
    def jpeg_quality_as_str(self) -> str:
        if not self.use_png and not self.tiff_ccitt:
            return str(self.jpeg_quality)
        else:
            return '-'

    @property
    def png_level_as_str(self) -> str:
        if self.use_png:
            return str(self.png_compression)
        else:
            return '-'

    @property
    def bw_threshold_as_str(self) -> str:
        if self.mode == CompressionMode.BW:
            return str(self.bw_threshold)
        else:
            return '-'

    @property
    def sharpen_as_str(self) -> str:
        return str(self.sharpen)

    @property
    def contrast_as_str(self) -> str:
        return str(self.contrast)

    @property
    def unsharp_mask_as_str(self) -> str:
        return 'Yes' if self.unsharp_mask else 'No'

    @property
    def tiff_ccitt_as_str(self) -> str:
        return 'Yes' if self.tiff_ccitt else 'No'


    def to_dict(self) -> dict[str, str]:
        """
        Returns all 10 settings as a display dictionary.
        Non-applicable fields are shown as '-'.
        Order: Mode, DPI, Format, JPEG Quality, PNG Level (left column),
               BW Threshold, Sharpen, Contrast, Unsharp Mask, TIFF CCITT (right).
        """
        return {
            'Mode':         self.mode_as_str,
            'DPI':          self.dpi_as_str,
            'Format':       self.format_as_str,
            'JPEG Quality': self.jpeg_quality_as_str,
            'PNG Level':    self.png_level_as_str,
            'BW Threshold': self.bw_threshold_as_str,
            'Sharpen':      self.sharpen_as_str,
            'Contrast':     self.contrast_as_str,
            'Unsharp Mask': self.unsharp_mask_as_str,
            'TIFF CCITT':   self.tiff_ccitt_as_str,
        }
