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
        """
        Validates the compression settings.
        Raises ValueError if any setting is invalid.
        """
        if self._dpi is not None and (self._dpi <= 0):
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
        Returns whether to use TIFF with CCITT Group 4.
        """
        return bool(self._tiff_ccitt)

    @property
    def mode(self) -> CompressionMode:
        match self._mode:
            case 'color':
                return CompressionMode.COLOR
            case 'gray':
                return CompressionMode.GRAY
            case 'bw':
                return CompressionMode.BW
            case _:
                return CompressionMode.BW

    @property
    def dpi(self) -> int:
        if self._dpi is None:
            return 300
        return self._dpi

    @property
    def jpeg_quality(self) -> int | None:
        if not self._png_compression:
            return self._jpeg_quality
        return None

    @property
    def png_compression(self) -> int | None:
        if not self._png_compression and not self._jpeg_quality:
            return 9
        return self._png_compression

    @property
    def bw_threshold(self) -> int:
        if not self._bw_threshold:
            return 150
        return self._bw_threshold

    @property
    def sharpen(self) -> float:
        if self._sharpen is None:
            return 1.5
        return self._sharpen

    @property
    def contrast(self) -> float:
        if not self._contrast:
            return 1.5
        return self._contrast

    @property
    def unsharp_mask(self) -> bool:
        return bool(self._unsharp_mask)

    @property
    def tiff_ccitt(self) -> bool:
        return bool(self._tiff_ccitt)

    def to_dict(self) -> dict[str, str]:
        """
        Converts the compression settings to a dictionary representation.
        This is useful for displaying settings in tabular format.

        Returns
        -------
        dict[str, str]
            A dictionary with setting names as keys and their string-values.
        """
        return {
            'Mode': self.mode.value,
            'DPI': str(self.dpi),
            'JPEG Quality': str(self.jpeg_quality)
                if self.jpeg_quality is not None else '-',
            'PNG Level': str(self.png_compression)
                if self.png_compression is not None else '-',
            'BW Threshold': str(self.bw_threshold),
            'Sharpen': str(self.sharpen),
            'Contrast': str(self.contrast),
            'Unsharp Mask': 'Yes' if self.unsharp_mask else 'No',
            'TIFF CCITT': 'Yes' if self.tiff_ccitt else 'No'
        }
