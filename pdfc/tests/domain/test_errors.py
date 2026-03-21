import pytest
from pathlib import Path
from pdfc.domain.errors import CompressionError
from pdfc.domain.models import CompressionSettings


def make_error(message: str = 'something went wrong') -> CompressionError:
    return CompressionError(
        input_path=Path('/in.pdf'),
        output_path=Path('/out.pdf'),
        compression_settings=CompressionSettings(),
        error_message=message,
    )


class TestCompressionError:
    def test_is_exception(self):
        assert isinstance(make_error(), Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(CompressionError):
            raise make_error()

    def test_can_be_caught_as_base_exception(self):
        with pytest.raises(Exception):
            raise make_error()

    def test_str_contains_error_message(self):
        assert 'bad things happened' in str(make_error('bad things happened'))

    def test_str_contains_input_path(self):
        assert '/in.pdf' in str(make_error())

    def test_str_contains_output_path(self):
        assert '/out.pdf' in str(make_error())

    def test_stores_input_path(self):
        assert make_error()._input_path == Path('/in.pdf')

    def test_stores_output_path(self):
        assert make_error()._output_path == Path('/out.pdf')

    def test_stores_error_message(self):
        assert make_error('oops')._error_message == 'oops'

    def test_stores_compression_settings(self):
        settings = CompressionSettings(_dpi=150)
        err = CompressionError(Path('/a'), Path('/b'), settings, 'x')
        assert err._compression_settings is settings
