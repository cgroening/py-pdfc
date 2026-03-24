import pytest
from pathlib import Path
from unittest.mock import MagicMock
from pdfc.cli.commands.compare import CompareCommand
from pdfc.domain.errors import CompressionError
from pdfc.domain.models import CompressionSettings
from pdfc.services.compression import CompressionService


def make_command(service=None):
    return CompareCommand(service=service or MagicMock(spec=CompressionService))


class TestFindPdfFilesInPath:
    def test_exits_with_code_1_on_value_error(self):
        service = MagicMock(spec=CompressionService)
        service.get_pdf_files.side_effect = ValueError('not a PDF')
        cmd = make_command(service=service)

        with pytest.raises(SystemExit) as exc_info:
            cmd._find_pdf_files_in_path(Path('/fake'))
        assert exc_info.value.code == 1

    def test_exits_with_code_1_when_no_pdfs_found(self):
        service = MagicMock(spec=CompressionService)
        service.get_pdf_files.return_value = []
        cmd = make_command(service=service)

        with pytest.raises(SystemExit) as exc_info:
            cmd._find_pdf_files_in_path(Path('/fake'))
        assert exc_info.value.code == 1

    def test_stores_files_and_total_on_success(self, tmp_path):
        pdfs = [tmp_path / 'a.pdf', tmp_path / 'b.pdf']
        service = MagicMock(spec=CompressionService)
        service.get_pdf_files.return_value = pdfs
        cmd = make_command(service=service)
        cmd._find_pdf_files_in_path(tmp_path)
        assert cmd._pdf_files == pdfs
        assert cmd._total_files == 2


class TestGetPresets:
    def test_exits_with_code_1_on_file_not_found(self):
        service = MagicMock(spec=CompressionService)
        service.get_presets.side_effect = FileNotFoundError('no file')
        cmd = make_command(service=service)

        with pytest.raises(SystemExit) as exc_info:
            cmd._get_presets(dpi=300)
        assert exc_info.value.code == 1

    def test_exits_with_code_1_on_value_error(self):
        service = MagicMock(spec=CompressionService)
        service.get_presets.side_effect = ValueError('bad yaml')
        cmd = make_command(service=service)

        with pytest.raises(SystemExit) as exc_info:
            cmd._get_presets(dpi=300)
        assert exc_info.value.code == 1

    def test_stores_presets_and_total_on_success(self):
        presets = [('a', CompressionSettings()), ('b', CompressionSettings())]
        service = MagicMock(spec=CompressionService)
        service.get_presets.return_value = presets
        cmd = make_command(service=service)
        cmd._get_presets(dpi=300)
        assert cmd._presets == presets
        assert cmd._total_presets == 2


class TestRunPresetsForFile:
    def test_increments_successful_counter(self, tmp_path):
        pdf = tmp_path / 'in.pdf'
        pdf.write_bytes(b'x' * 100)
        out_dir = tmp_path / 'out'
        out_dir.mkdir()

        settings = CompressionSettings()
        presets = [('preset-a', settings), ('preset-b', settings)]

        service = MagicMock(spec=CompressionService)

        def fake_compress(inp, out, s):
            out.write_bytes(b'x' * 80)

        service.compress_file.side_effect = fake_compress

        cmd = make_command(service=service)
        cmd._presets = presets
        cmd._successful = 0
        cmd._failed = 0
        cmd._run_presets_for_file(pdf, pdf.stat().st_size, out_dir)

        assert cmd._successful == 2
        assert cmd._failed == 0

    def test_increments_failed_counter_on_exception(self, tmp_path):
        pdf = tmp_path / 'in.pdf'
        pdf.write_bytes(b'x' * 100)
        out_dir = tmp_path / 'out'
        out_dir.mkdir()

        # Pre-create the output file for the successful preset so that
        # output_path.stat() inside the command works after the mock returns.
        (out_dir / 'first.pdf').write_bytes(b'x' * 80)

        settings = CompressionSettings()
        presets = [('first', settings), ('second', settings)]

        service = MagicMock(spec=CompressionService)
        service.compress_file.side_effect = [
            None,  # first succeeds
            CompressionError(pdf, out_dir / 'second.pdf', settings, 'oops'),
        ]

        cmd = make_command(service=service)
        cmd._presets = presets
        cmd._successful = 0
        cmd._failed = 0
        cmd._run_presets_for_file(pdf, pdf.stat().st_size, out_dir)

        assert cmd._successful == 1
        assert cmd._failed == 1

    def test_continues_after_failure(self, tmp_path):
        """A failed preset must not abort remaining presets."""
        pdf = tmp_path / 'in.pdf'
        pdf.write_bytes(b'x' * 100)
        out_dir = tmp_path / 'out'
        out_dir.mkdir()

        (out_dir / 'second.pdf').write_bytes(b'x' * 80)

        settings = CompressionSettings()
        presets = [('first', settings), ('second', settings)]

        service = MagicMock(spec=CompressionService)
        service.compress_file.side_effect = [
            RuntimeError('first fails'),
            None,  # second succeeds
        ]

        cmd = make_command(service=service)
        cmd._presets = presets
        cmd._successful = 0
        cmd._failed = 0
        cmd._run_presets_for_file(pdf, pdf.stat().st_size, out_dir)

        assert service.compress_file.call_count == 2
        assert cmd._successful == 1
        assert cmd._failed == 1

    def test_uses_correct_output_path_per_preset(self, tmp_path):
        pdf = tmp_path / 'in.pdf'
        pdf.write_bytes(b'x' * 100)
        out_dir = tmp_path / 'out'
        out_dir.mkdir()

        settings = CompressionSettings()
        presets = [('preset-one', settings)]

        service = MagicMock(spec=CompressionService)

        def fake_compress(inp, out, s):
            out.write_bytes(b'x' * 80)

        service.compress_file.side_effect = fake_compress

        cmd = make_command(service=service)
        cmd._presets = presets
        cmd._successful = 0
        cmd._failed = 0
        cmd._run_presets_for_file(pdf, pdf.stat().st_size, out_dir)

        expected_out = out_dir / 'preset-one.pdf'
        service.compress_file.assert_called_once_with(
            pdf, expected_out, settings
        )
