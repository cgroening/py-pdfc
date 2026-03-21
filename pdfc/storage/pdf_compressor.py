import os
import tempfile
from enum import Enum
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import img2pdf
from pdfc.domain.models import CompressionSettings, CompressionMode


class ImageFormat(Enum):
    TIFF_CCITT = 'TIFF_CCITT'
    PNG = 'PNG'
    JPEG = 'JPEG'


class PdfCompressor:
    """
    Compresses a PDF file by rasterising each page, applying image enhancements
    and re-encoding with the chosen format (JPEG, PNG or TIFF CCITT Group 4).
    """

    def compress(
        self,
        input_path: Path,
        output_path: Path,
        compression_settings: CompressionSettings
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
        images = convert_from_path(
            str(input_path), dpi=compression_settings.dpi
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            processed = [
                self._process_page(image, page_number, compression_settings, tmp_dir)
                for page_number, image in enumerate(images, 1)
            ]
            pdf_data = img2pdf.convert(processed)
            if pdf_data is None:
                raise ValueError('Failed to convert images to PDF.')
            with open(output_path, 'wb') as f:
                f.write(pdf_data)

    def _process_page(
        self,
        image: Image.Image,
        page_number: int,
        compression_settings: CompressionSettings,
        tmp_dir: str,
    ) -> str:
        """Processes one page and returns the path of the temp image file."""
        # Enchance image based on compression mode
        match compression_settings.mode:
            case CompressionMode.BW:
                converted_image = self._prepare_bw_image(
                    image, compression_settings
                )
            case CompressionMode.GRAY:
                converted_image = image.convert('L')
                converted_image = self._apply_enhancements(
                    converted_image, compression_settings
                )
            case _:  # COLOR
                converted_image = image.convert('RGB')
                converted_image = self._apply_enhancements(
                    converted_image, compression_settings
                )

        # Save the processed image in the desired format
        args = (converted_image, tmp_dir, page_number, compression_settings)
        if compression_settings.tiff_ccitt:
            path = self._save_image(*args, ImageFormat.TIFF_CCITT)
        elif compression_settings.use_png:
            path = self._save_image(*args, ImageFormat.PNG)
        else:
            path = self._save_image(*args, ImageFormat.JPEG)

        return path

    def _apply_enhancements(
        self, image: Image.Image, compression_settings: CompressionSettings
    ) -> Image.Image:
        """Applies contrast enhancement, unsharp mask and sharpening."""
        cs = compression_settings
        if cs.contrast != 1.0:
            image = ImageEnhance.Contrast(image).enhance(cs.contrast)
        if cs.unsharp_mask:
            image = image.filter(
                ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
            )
        if cs.sharpen > 0:
            image = ImageEnhance.Sharpness(image).enhance(cs.sharpen)
        return image

    def _prepare_bw_image(
        self, image: Image.Image, cs: CompressionSettings
    ) -> Image.Image:
        """
        Converts the image to grayscale, applies enhancements and thresholds
        back to black and white.

        The intermediate grayscale step is required so that contrast and
        sharpness filters can operate on continuous pixel values (0–255) - on a
        1-bit image these operations would have no effect.
        """
        gray = image.convert('L')
        gray = self._apply_enhancements(gray, cs)
        threshold = cs.bw_threshold

        def to_bw(pixel: int) -> int:
            return 255 if pixel > threshold else 0

        return gray.point(to_bw, mode='1')

    @staticmethod
    def _save_image(
        image: Image.Image,
        tmp_dir: str,
        page_number: int,
        compression_settings: CompressionSettings,
        image_format: ImageFormat
    ) -> str:
        """Saves the image in the specified format and returns the file path."""
        path = PdfCompressor._generate_image_path(
            tmp_dir, page_number, image_format
        )
        dpi = (compression_settings.dpi, compression_settings.dpi)

        match image_format:
            case ImageFormat.TIFF_CCITT:
                image.save(
                    path, 'TIFF',
                    compression='group4',
                    dpi=dpi
                )
            case ImageFormat.PNG:
                image.save(
                    path, 'PNG',
                    optimize=True,
                    compress_level=compression_settings.png_compression,
                    dpi=dpi
                )
            case _:  # JPEG
                image.convert('RGB').save(
                    path, 'JPEG',
                    quality=compression_settings.jpeg_quality,
                    optimize=True,
                    dpi=dpi
                )

        return path

    @staticmethod
    def _generate_image_path(
        tmp_dir: str,
        page_number: int,
        image_format: ImageFormat
    ) -> str:
        """
        Generates a file path for a processed image based on the page number
        and the image format.
        """
        match image_format:
            case ImageFormat.TIFF_CCITT:
                file_extension = 'tif'
            case ImageFormat.PNG:
                file_extension = 'png'
            case _:  # JPEG
                file_extension = 'jpg'
        return os.path.join(tmp_dir, f'page_{page_number}.{file_extension}')
