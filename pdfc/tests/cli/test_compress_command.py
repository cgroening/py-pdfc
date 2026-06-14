import pytest
from pathlib import Path
from unittest.mock import MagicMock
from pdfc.cli.commands.compress import CompressCommand
from pdfc.cli.commands.compress_input import InputView
from pdfc.cli.compress_parameters import CompressRequest
from pdfc.domain.errors import CompressionError
from pdfc.domain.models import CompressionSettings
from pdfc.services.compression import CompressionService


def make_command(service=None, input_view=None):
    return CompressCommand(
        service=service or MagicMock(spec=CompressionService),
        input_view=input_view or MagicMock(spec=InputView),
    )


def make_request(
    input_path=None,
    output_path=None,
    settings=None,
    interactive=False,
    tmp_path=None,
):
    return CompressRequest(
        interactive_mode=interactive,
        input_path=input_path or Path('/fake/in.pdf'),
        compression_settings=settings or CompressionSettings(),
        output_path=output_path,
    )


class TestValidateCompressionSettings:
    def test_exits_with_code_1_on_value_error(self, tmp_path):
        service = MagicMock(spec=CompressionService)
        service.validate.side_effect = ValueError('invalid DPI')
        cmd = make_command(service=service)
        cmd._compress_request = make_request()

        with pytest.raises(SystemExit) as exc_info:
            cmd._validate_compression_settings()
        assert exc_info.value.code == 1

    def test_does_not_exit_on_valid_settings(self):
        service = MagicMock(spec=CompressionService)
        service.validate.return_value = None
        cmd = make_command(service=service)
        cmd._compress_request = make_request()
        cmd._validate_compression_settings()  # no exception


class TestFindPdfFilesInInputPath:
    def test_exits_with_code_1_on_value_error(self, tmp_path):
        service = MagicMock(spec=CompressionService)
        service.get_pdf_files.side_effect = ValueError('not a PDF')
        cmd = make_command(service=service)
        cmd._compress_request = make_request()

        with pytest.raises(SystemExit) as exc_info:
            cmd._find_pdf_files_in_input_path()
        assert exc_info.value.code == 1

    def test_exits_with_code_1_when_no_pdfs_found(self):
        service = MagicMock(spec=CompressionService)
        service.get_pdf_files.return_value = []
        cmd = make_command(service=service)
        cmd._compress_request = make_request()

        with pytest.raises(SystemExit) as exc_info:
            cmd._find_pdf_files_in_input_path()
        assert exc_info.value.code == 1

    def test_stores_pdf_files_on_success(self, tmp_path):
        pdf = tmp_path / 'a.pdf'
        service = MagicMock(spec=CompressionService)
        service.get_pdf_files.return_value = [pdf]
        cmd = make_command(service=service)
        cmd._compress_request = make_request()
        cmd._find_pdf_files_in_input_path()
        assert cmd._pdf_files == [pdf]


class TestValidateOutputPath:
    def test_clears_output_path_when_input_is_directory(self, tmp_path):
        service = MagicMock(spec=CompressionService)
        cmd = make_command(service=service)
        cmd._compress_request = make_request(
            input_path=tmp_path,
            output_path=tmp_path / 'out.pdf',
        )
        cmd._validate_output_path()
        assert cmd._compress_request.output_path is None

    def test_keeps_output_path_when_input_is_file(self, tmp_path):
        pdf = tmp_path / 'in.pdf'
        pdf.touch()
        explicit_out = tmp_path / 'out.pdf'
        service = MagicMock(spec=CompressionService)
        cmd = make_command(service=service)
        cmd._compress_request = make_request(
            input_path=pdf, output_path=explicit_out
        )
        cmd._validate_output_path()
        assert cmd._compress_request.output_path == explicit_out

    def test_no_change_when_output_path_is_none(self, tmp_path):
        service = MagicMock(spec=CompressionService)
        cmd = make_command(service=service)
        cmd._compress_request = make_request(input_path=tmp_path, output_path=None)
        cmd._validate_output_path()
        assert cmd._compress_request.output_path is None


class TestPrintCompressionResult:
    def test_computes_savings_percentage(self, tmp_path):
        original = tmp_path / 'original.pdf'
        compressed = tmp_path / 'compressed.pdf'
        original.write_bytes(b'x' * 1000)
        compressed.write_bytes(b'x' * 600)

        # Should not raise - savings = 40%
        CompressCommand._print_compression_result(original, compressed)

    def test_handles_zero_original_size(self, tmp_path):
        original = tmp_path / 'original.pdf'
        compressed = tmp_path / 'compressed.pdf'
        original.write_bytes(b'')
        compressed.write_bytes(b'')
        # savings should be 0.0 - no ZeroDivisionError
        CompressCommand._print_compression_result(original, compressed)


class TestCompressSingleFile:
    def test_does_not_exit_on_compression_error(self, tmp_path):
        """Compression errors should be logged but not abort the run."""
        pdf = tmp_path / 'in.pdf'
        pdf.write_bytes(b'x' * 100)
        out = tmp_path / 'out.pdf'

        service = MagicMock(spec=CompressionService)
        service.compress_file.side_effect = CompressionError(
            pdf, out, CompressionSettings(), 'some error'
        )
        cmd = make_command(service=service)
        cmd._compress_request = make_request(input_path=pdf)

        # Should not raise SystemExit - loop continues
        cmd._compress_single_file(pdf, out)

    def test_does_not_exit_on_unexpected_exception(self, tmp_path):
        pdf = tmp_path / 'in.pdf'
        pdf.write_bytes(b'x' * 100)
        out = tmp_path / 'out.pdf'

        service = MagicMock(spec=CompressionService)
        service.compress_file.side_effect = RuntimeError('unexpected')
        cmd = make_command(service=service)
        cmd._compress_request = make_request(input_path=pdf)

        cmd._compress_single_file(pdf, out)  # should not raise

    def test_calls_service_with_correct_args(self, tmp_path):
        pdf = tmp_path / 'in.pdf'
        pdf.write_bytes(b'x' * 100)
        out = tmp_path / 'out.pdf'
        out.write_bytes(b'x' * 80)

        service = MagicMock(spec=CompressionService)
        settings = CompressionSettings()
        cmd = make_command(service=service)
        cmd._compress_request = make_request(input_path=pdf, settings=settings)
        cmd._compress_single_file(pdf, out)

        service.compress_file.assert_called_once_with(pdf, out, settings)


class TestCompressRequest:
    def test_input_path_is_directory_returns_true(self, tmp_path):
        req = make_request(input_path=tmp_path)
        assert req.input_path_is_directory() is True

    def test_input_path_is_directory_returns_false_for_file(self, tmp_path):
        pdf = tmp_path / 'file.pdf'
        pdf.touch()
        req = make_request(input_path=pdf)
        assert req.input_path_is_directory() is False
