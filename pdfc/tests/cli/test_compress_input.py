from unittest.mock import patch, MagicMock
from pdfc.cli.commands.compress_input import InputView


def mock_select(answer):
    """Returns a mock for questionary.select(...).ask() that returns `answer`."""
    select_mock = MagicMock()
    select_mock.return_value.ask.return_value = answer
    return select_mock


class TestPromptMode:
    def test_returns_bw_for_bw_answer(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('B&W')
        ):
            assert InputView().prompt_mode() == 'bw'

    def test_returns_gray_for_grayscale_answer(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('Grayscale')
        ):
            assert InputView().prompt_mode() == 'gray'

    def test_returns_color_for_color_answer(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('Color')
        ):
            assert InputView().prompt_mode() == 'color'

    def test_increments_prompt_counter(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('B&W')
        ):
            view = InputView()
            view.prompt_mode()
            assert view.number_of_executed_prompts == 1


class TestPromptDpi:
    def test_returns_int(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('300')
        ):
            result = InputView().prompt_dpi()
        assert result == 300
        assert isinstance(result, int)

    def test_increments_prompt_counter(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('150')
        ):
            view = InputView()
            view.prompt_dpi()
            assert view.number_of_executed_prompts == 1


class TestPromptImageFormat:
    def test_returns_lowercase_jpeg(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('JPEG')
        ):
            assert InputView().prompt_image_format() == 'jpeg'

    def test_returns_lowercase_png(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('PNG')
        ):
            assert InputView().prompt_image_format() == 'png'


class TestPromptJpegQuality:
    def test_returns_int(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('70')
        ):
            result = InputView().prompt_jpeg_quality()
        assert result == 70
        assert isinstance(result, int)


class TestPromptPngCompression:
    def test_returns_int(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('5')
        ):
            result = InputView().prompt_png_compression()
        assert result == 5
        assert isinstance(result, int)


class TestPromptBwThreshold:
    def test_returns_int(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('150')
        ):
            result = InputView().prompt_bw_threshold()
        assert result == 150
        assert isinstance(result, int)


class TestPromptSharpen:
    def test_returns_float(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('1.5')
        ):
            result = InputView().prompt_sharpen()
        assert result == 1.5
        assert isinstance(result, float)


class TestPromptContrast:
    def test_returns_float(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('2.0')
        ):
            result = InputView().prompt_contrast()
        assert result == 2.0
        assert isinstance(result, float)


class TestPromptUnsharpMask:
    def test_returns_true_for_yes(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('Yes')
        ):
            assert InputView().prompt_unsharp_mask() is True

    def test_returns_false_for_no(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('No')
        ):
            assert InputView().prompt_unsharp_mask() is False


class TestPromptTiffCcitt:
    def test_returns_true_for_yes(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('Yes')
        ):
            assert InputView().prompt_tiff_ccitt() is True

    def test_returns_false_for_no(self):
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select',
            mock_select('No')
        ):
            assert InputView().prompt_tiff_ccitt() is False


class TestNumberOfExecutedPrompts:
    def test_counter_accumulates_across_prompts(self):
        select = mock_select('B&W')
        with patch(
            'pdfc.cli.commands.compress_input.questionary.select', select
        ):
            view = InputView()
            view.prompt_mode()
            view.prompt_mode()
            view.prompt_mode()
            assert view.number_of_executed_prompts == 3
