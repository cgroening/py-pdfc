import pytest
from unittest.mock import MagicMock
from pdfc.domain.errors import CompressionError
from pdfc.domain.models import CompressionSettings
from pdfc.services.compression import CompressionService
from pdfc.storage.pdf_compressor import PdfCompressor
from pdfc.storage.presets_storage import PresetsStorage


def make_service(
    compressor: PdfCompressor | None = None,
    presets: PresetsStorage | None = None,
) -> CompressionService:
    return CompressionService(
        compressor=compressor or MagicMock(spec=PdfCompressor),
        presets_storage=presets or MagicMock(spec=PresetsStorage),
    )


class TestValidate:
    def test_raises_when_settings_is_none(self):
        with pytest.raises(ValueError, match='required'):
            make_service().validate(None)

    def test_passes_for_valid_settings(self):
        make_service().validate(CompressionSettings(_dpi=300))

    def test_raises_for_invalid_dpi(self):
        with pytest.raises(ValueError):
            make_service().validate(CompressionSettings(_dpi=-1))

    def test_raises_for_invalid_jpeg_quality(self):
        with pytest.raises(ValueError):
            make_service().validate(CompressionSettings(_jpeg_quality=0))


class TestGetPdfFiles:
    def test_returns_single_pdf_file(self, tmp_path):
        pdf = tmp_path / 'test.pdf'
        pdf.touch()
        assert make_service().get_pdf_files(pdf) == [pdf]

    def test_raises_for_non_pdf_file(self, tmp_path):
        txt = tmp_path / 'test.txt'
        txt.touch()
        with pytest.raises(ValueError, match='not a PDF'):
            make_service().get_pdf_files(txt)

    def test_raises_for_nonexistent_path(self, tmp_path):
        with pytest.raises(ValueError, match='does not exist'):
            make_service().get_pdf_files(tmp_path / 'missing.pdf')

    def test_returns_pdfs_from_directory(self, tmp_path):
        (tmp_path / 'a.pdf').touch()
        (tmp_path / 'b.pdf').touch()
        (tmp_path / 'ignore.txt').touch()
        result = make_service().get_pdf_files(tmp_path)
        assert len(result) == 2
        assert all(f.suffix == '.pdf' for f in result)

    def test_returns_empty_list_for_empty_directory(self, tmp_path):
        assert make_service().get_pdf_files(tmp_path) == []

    def test_finds_pdfs_recursively(self, tmp_path):
        sub = tmp_path / 'sub'
        sub.mkdir()
        (sub / 'nested.pdf').touch()
        result = make_service().get_pdf_files(tmp_path)
        assert len(result) == 1

    def test_no_duplicates_in_result(self, tmp_path):
        (tmp_path / 'a.pdf').touch()
        result = make_service().get_pdf_files(tmp_path)
        assert len(result) == result.count(tmp_path / 'a.pdf') == 1


class TestGetOutputPath:
    def test_returns_explicit_output_path(self, tmp_path):
        explicit = tmp_path / 'custom.pdf'
        result = make_service().get_output_path(tmp_path / 'in.pdf', explicit)
        assert result == explicit

    def test_generates_compressed_suffix_when_none(self, tmp_path):
        result = make_service().get_output_path(tmp_path / 'report.pdf', None)
        assert result == tmp_path / 'report-compressed.pdf'

    def test_generated_path_is_in_same_directory(self, tmp_path):
        result = make_service().get_output_path(tmp_path / 'doc.pdf', None)
        assert result.parent == tmp_path


class TestGetCompareOutputDir:
    def test_returns_dir_named_after_stem(self, tmp_path):
        result = make_service().get_compare_output_dir(
            tmp_path / 'document.pdf'
        )
        assert result == tmp_path / 'document'


class TestCompressFile:
    def test_delegates_to_compressor(self, tmp_path):
        compressor = MagicMock(spec=PdfCompressor)
        service = make_service(compressor=compressor)
        settings = CompressionSettings()
        inp, out = tmp_path / 'in.pdf', tmp_path / 'out.pdf'
        service.compress_file(inp, out, settings)
        compressor.compress.assert_called_once_with(inp, out, settings)

    def test_wraps_exception_as_compression_error(self, tmp_path):
        compressor = MagicMock(spec=PdfCompressor)
        compressor.compress.side_effect = RuntimeError('disk full')
        service = make_service(compressor=compressor)
        with pytest.raises(CompressionError):
            service.compress_file(
                tmp_path / 'in.pdf', tmp_path / 'out.pdf', CompressionSettings()
            )

    def test_compression_error_str_contains_original_message(self, tmp_path):
        compressor = MagicMock(spec=PdfCompressor)
        compressor.compress.side_effect = RuntimeError('disk full')
        service = make_service(compressor=compressor)
        with pytest.raises(CompressionError) as exc_info:
            service.compress_file(
                tmp_path / 'in.pdf', tmp_path / 'out.pdf', CompressionSettings()
            )
        assert 'disk full' in str(exc_info.value)

    def test_compression_error_stores_paths(self, tmp_path):
        compressor = MagicMock(spec=PdfCompressor)
        compressor.compress.side_effect = RuntimeError('oops')
        inp, out = tmp_path / 'in.pdf', tmp_path / 'out.pdf'
        with pytest.raises(CompressionError) as exc_info:
            make_service(compressor=compressor).compress_file(
                inp, out, CompressionSettings()
            )
        assert exc_info.value._input_path == inp
        assert exc_info.value._output_path == out


class TestGetCompareConfigs:
    def test_returns_name_settings_pairs(self):
        presets = MagicMock(spec=PresetsStorage)
        presets.load.return_value = [
            {'name': 'preset-a', '_mode': 'bw', '_jpeg_quality': 20}
        ]
        result = make_service(presets=presets).get_compare_configs(dpi=200)
        assert len(result) == 1
        name, settings = result[0]
        assert name == 'preset-a'
        assert isinstance(settings, CompressionSettings)

    def test_applies_dpi_fallback_when_not_in_preset(self):
        presets = MagicMock(spec=PresetsStorage)
        presets.load.return_value = [{'name': 'p', '_mode': 'color'}]
        _, settings = make_service(presets=presets).get_compare_configs(dpi=72)[0]
        assert settings.dpi == 72

    def test_does_not_override_preset_dpi(self):
        presets = MagicMock(spec=PresetsStorage)
        presets.load.return_value = [{'name': 'p', '_mode': 'color', '_dpi': 600}]
        _, settings = make_service(presets=presets).get_compare_configs(dpi=72)[0]
        assert settings.dpi == 600

    def test_returns_multiple_configs(self):
        presets = MagicMock(spec=PresetsStorage)
        presets.load.return_value = [
            {'name': 'a', '_mode': 'bw'},
            {'name': 'b', '_mode': 'gray'},
            {'name': 'c', '_mode': 'color'},
        ]
        result = make_service(presets=presets).get_compare_configs(dpi=300)
        assert len(result) == 3
        assert [name for name, _ in result] == ['a', 'b', 'c']

    def test_propagates_file_not_found(self):
        presets = MagicMock(spec=PresetsStorage)
        presets.load.side_effect = FileNotFoundError('no file')
        with pytest.raises(FileNotFoundError):
            make_service(presets=presets).get_compare_configs(dpi=300)

    def test_propagates_value_error(self):
        presets = MagicMock(spec=PresetsStorage)
        presets.load.side_effect = ValueError('bad yaml')
        with pytest.raises(ValueError):
            make_service(presets=presets).get_compare_configs(dpi=300)
