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
        """True if PNG should be used as intermediate format (tiff_ccitt takes priority)."""
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

    def to_dict(self) -> dict[str, str]:
        """Returns settings as a display dictionary."""
        if self.tiff_ccitt:
            img_format = 'TIFF CCITT'
        elif self.use_png:
            img_format = 'PNG'
        else:
            img_format = 'JPEG'

        d: dict[str, str] = {
            'Mode': self.mode.value,
            'DPI': str(self.dpi),
            'Format': img_format,
        }
        if not self.tiff_ccitt:
            if self.use_png:
                d['PNG Level'] = str(self.png_compression)
            else:
                d['JPEG Quality'] = str(self.jpeg_quality)
        if self.mode == CompressionMode.BW:
            d['BW Threshold'] = str(self.bw_threshold)
        d['Sharpen'] = str(self.sharpen)
        d['Contrast'] = str(self.contrast)
        d['Unsharp Mask'] = 'Yes' if self.unsharp_mask else 'No'
        d['TIFF CCITT'] = 'Yes' if self.tiff_ccitt else 'No'
        return d
