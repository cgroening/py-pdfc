import os
import tempfile
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import img2pdf
from pdfc.domain.models import CompressionSettings, CompressionMode


class PdfCompressor:
    """
    Compresses a PDF file by rasterising each page, applying image enhancements
    and re-encoding with the chosen format (JPEG, PNG or TIFF CCITT Group 4).
    """

    def compress(
        self, input_path: Path, output_path: Path, settings: CompressionSettings
    ) -> None:
        """
        Compresses a single PDF file.

        Parameters
        ----------
        input_path : Path
            Path to the source PDF.
        output_path : Path
            Path where the compressed PDF will be written.
        settings : CompressionSettings
            Compression settings to apply.
        """
        images = convert_from_path(str(input_path), dpi=settings.dpi)

        with tempfile.TemporaryDirectory() as tmp_dir:
            processed = [
                self._process_page(image, i, settings, tmp_dir)
                for i, image in enumerate(images, 1)
            ]
            with open(output_path, 'wb') as f:
                f.write(img2pdf.convert(processed))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _process_page(
        self,
        image: Image.Image,
        page_num: int,
        settings: CompressionSettings,
        tmp_dir: str,
    ) -> str:
        """Processes one page and returns the path of the temp image file."""
        match settings.mode:
            case CompressionMode.BW:
                return self._process_bw(image, page_num, settings, tmp_dir)
            case CompressionMode.GRAY:
                return self._process_gray(image, page_num, settings, tmp_dir)
            case _:  # COLOR
                return self._process_color(image, page_num, settings, tmp_dir)

    def _apply_enhancements(
        self,
        image: Image.Image,
        settings: CompressionSettings,
    ) -> Image.Image:
        """Applies contrast enhancement, unsharp mask and sharpening."""
        if settings.contrast != 1.0:
            image = ImageEnhance.Contrast(image).enhance(settings.contrast)
        if settings.unsharp_mask:
            image = image.filter(
                ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
            )
        if settings.sharpen > 0:
            image = ImageEnhance.Sharpness(image).enhance(settings.sharpen)
        return image

    def _process_bw(
        self,
        image: Image.Image,
        page_num: int,
        settings: CompressionSettings,
        tmp_dir: str,
    ) -> str:
        gray = image.convert('L')
        gray = self._apply_enhancements(gray, settings)
        bw = gray.point(lambda x: 255 if x > settings.bw_threshold else 0, mode='1')

        if settings.tiff_ccitt:
            path = os.path.join(tmp_dir, f'page_{page_num}.tif')
            bw.save(path, 'TIFF', compression='group4', dpi=(settings.dpi, settings.dpi))
        elif settings.use_png:
            path = os.path.join(tmp_dir, f'page_{page_num}.png')
            bw.save(
                path, 'PNG',
                optimize=True,
                compress_level=settings.png_compression,
                dpi=(settings.dpi, settings.dpi),
            )
        else:
            path = os.path.join(tmp_dir, f'page_{page_num}.jpg')
            bw.convert('RGB').save(
                path, 'JPEG',
                quality=settings.jpeg_quality,
                optimize=True,
                dpi=(settings.dpi, settings.dpi),
            )
        return path

    def _process_gray(
        self,
        image: Image.Image,
        page_num: int,
        settings: CompressionSettings,
        tmp_dir: str,
    ) -> str:
        gray = image.convert('L')
        gray = self._apply_enhancements(gray, settings)

        if settings.use_png:
            path = os.path.join(tmp_dir, f'page_{page_num}.png')
            gray.save(
                path, 'PNG',
                optimize=True,
                compress_level=settings.png_compression,
                dpi=(settings.dpi, settings.dpi),
            )
        else:
            path = os.path.join(tmp_dir, f'page_{page_num}.jpg')
            gray.convert('RGB').save(
                path, 'JPEG',
                quality=settings.jpeg_quality,
                optimize=True,
                dpi=(settings.dpi, settings.dpi),
            )
        return path

    def _process_color(
        self,
        image: Image.Image,
        page_num: int,
        settings: CompressionSettings,
        tmp_dir: str,
    ) -> str:
        rgb = image.convert('RGB')
        rgb = self._apply_enhancements(rgb, settings)

        if settings.use_png:
            path = os.path.join(tmp_dir, f'page_{page_num}.png')
            rgb.save(
                path, 'PNG',
                optimize=True,
                compress_level=settings.png_compression,
                dpi=(settings.dpi, settings.dpi),
            )
        else:
            path = os.path.join(tmp_dir, f'page_{page_num}.jpg')
            rgb.save(
                path, 'JPEG',
                quality=settings.jpeg_quality,
                optimize=True,
                dpi=(settings.dpi, settings.dpi),
            )
        return path
