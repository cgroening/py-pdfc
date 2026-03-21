import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from pdfc.domain.models import CompressionSettings
from pdfc.storage.pdf_compressor import PdfCompressor


def make_settings(**kwargs) -> CompressionSettings:
    return CompressionSettings(**kwargs)


def make_mock_image() -> MagicMock:
    """Minimal PIL Image mock that survives _process_page for all modes."""
    img = MagicMock()
    img.convert.return_value = img
    img.point.return_value = img
    img.filter.return_value = img
    img.save.return_value = None
    return img


class TestPdfCompressorCompress:
    @patch('pdfc.storage.pdf_compressor.img2pdf.convert')
    @patch('pdfc.storage.pdf_compressor.convert_from_path')
    def test_calls_convert_from_path_with_correct_dpi(
        self, mock_convert, mock_img2pdf, tmp_path
    ):
        mock_convert.return_value = [make_mock_image()]
        mock_img2pdf.return_value = b'%PDF'
        PdfCompressor().compress(
            Path('/in.pdf'), tmp_path / 'out.pdf', make_settings(_dpi=150)
        )
        mock_convert.assert_called_once_with('/in.pdf', dpi=150)

    @patch('pdfc.storage.pdf_compressor.img2pdf.convert')
    @patch('pdfc.storage.pdf_compressor.convert_from_path')
    def test_writes_output_file(self, mock_convert, mock_img2pdf, tmp_path):
        mock_convert.return_value = [make_mock_image()]
        mock_img2pdf.return_value = b'%PDF-data'
        out = tmp_path / 'out.pdf'
        PdfCompressor().compress(Path('/in.pdf'), out, make_settings())
        assert out.exists()
        assert out.read_bytes() == b'%PDF-data'

    @patch('pdfc.storage.pdf_compressor.img2pdf.convert')
    @patch('pdfc.storage.pdf_compressor.convert_from_path')
    def test_processes_each_page(self, mock_convert, mock_img2pdf, tmp_path):
        mock_convert.return_value = [
            make_mock_image(), make_mock_image(), make_mock_image()
        ]
        mock_img2pdf.return_value = b'%PDF'
        PdfCompressor().compress(
            Path('/in.pdf'), tmp_path / 'out.pdf', make_settings()
        )
        # img2pdf receives 3 processed image paths
        args, _ = mock_img2pdf.call_args
        assert len(args[0]) == 3

    @patch('pdfc.storage.pdf_compressor.convert_from_path')
    def test_raises_when_convert_from_path_fails(self, mock_convert, tmp_path):
        mock_convert.side_effect = RuntimeError('poppler not found')
        with pytest.raises(Exception, match='poppler not found'):
            PdfCompressor().compress(
                Path('/in.pdf'), tmp_path / 'out.pdf', make_settings()
            )

    @patch('pdfc.storage.pdf_compressor.img2pdf.convert')
    @patch('pdfc.storage.pdf_compressor.convert_from_path')
    def test_raises_value_error_when_img2pdf_returns_none(
        self, mock_convert, mock_img2pdf, tmp_path
    ):
        mock_convert.return_value = [make_mock_image()]
        mock_img2pdf.return_value = None
        with pytest.raises(ValueError, match='Failed to convert'):
            PdfCompressor().compress(
                Path('/in.pdf'), tmp_path / 'out.pdf', make_settings()
            )

    @patch('pdfc.storage.pdf_compressor.img2pdf.convert')
    @patch('pdfc.storage.pdf_compressor.convert_from_path')
    def test_uses_default_dpi_300_when_not_set(
        self, mock_convert, mock_img2pdf, tmp_path
    ):
        mock_convert.return_value = [make_mock_image()]
        mock_img2pdf.return_value = b'%PDF'
        PdfCompressor().compress(
            Path('/in.pdf'), tmp_path / 'out.pdf', make_settings()
        )
        mock_convert.assert_called_once_with('/in.pdf', dpi=300)
