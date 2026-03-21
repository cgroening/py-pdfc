import pytest
from pdfc.domain.models import CompressionSettings, CompressionMode


class TestCompressionSettingsDefaults:
    def test_mode_default_is_bw(self):
        s = CompressionSettings()
        assert s.mode == CompressionMode.BW

    def test_mode_color(self):
        s = CompressionSettings(_mode='color')
        assert s.mode == CompressionMode.COLOR

    def test_mode_gray(self):
        s = CompressionSettings(_mode='gray')
        assert s.mode == CompressionMode.GRAY

    def test_mode_bw(self):
        s = CompressionSettings(_mode='bw')
        assert s.mode == CompressionMode.BW

    def test_dpi_default(self):
        assert CompressionSettings().dpi == 300

    def test_dpi_custom(self):
        assert CompressionSettings(_dpi=150).dpi == 150

    def test_jpeg_quality_default(self):
        assert CompressionSettings().jpeg_quality == 30

    def test_png_compression_default(self):
        assert CompressionSettings().png_compression == 6

    def test_bw_threshold_default(self):
        assert CompressionSettings().bw_threshold == 150

    def test_sharpen_default(self):
        assert CompressionSettings().sharpen == 0.0

    def test_contrast_default(self):
        assert CompressionSettings().contrast == 1.0

    def test_unsharp_mask_default(self):
        assert CompressionSettings().unsharp_mask is False

    def test_tiff_ccitt_default(self):
        assert CompressionSettings().tiff_ccitt is False


class TestUsePng:
    def test_true_when_png_compression_set(self):
        assert CompressionSettings(_png_compression=6).use_png is True

    def test_false_when_tiff_ccitt_takes_priority(self):
        assert CompressionSettings(
            _png_compression=6, _tiff_ccitt=True
        ).use_png is False

    def test_false_by_default(self):
        assert CompressionSettings().use_png is False


class TestFormatAsStr:
    def test_jpeg_format(self):
        assert CompressionSettings().format_as_str == 'JPEG'

    def test_png_format(self):
        assert CompressionSettings(_png_compression=6).format_as_str == 'PNG'

    def test_tiff_format(self):
        assert CompressionSettings(
            _tiff_ccitt=True
        ).format_as_str == 'TIFF CCITT'


class TestDisplayStrings:
    def test_jpeg_quality_as_str_when_jpeg(self):
        assert CompressionSettings(_jpeg_quality=80).jpeg_quality_as_str == '80'

    def test_jpeg_quality_as_str_dash_when_png(self):
        assert CompressionSettings(
            _png_compression=6).jpeg_quality_as_str == '-'

    def test_jpeg_quality_as_str_dash_when_tiff(self):
        assert CompressionSettings(_tiff_ccitt=True).jpeg_quality_as_str == '-'

    def test_png_level_as_str_when_png(self):
        assert CompressionSettings(_png_compression=3).png_level_as_str == '3'

    def test_png_level_as_str_dash_when_jpeg(self):
        assert CompressionSettings().png_level_as_str == '-'

    def test_bw_threshold_as_str_when_bw(self):
        assert CompressionSettings(
            _mode='bw', _bw_threshold=128
        ).bw_threshold_as_str == '128'

    def test_bw_threshold_as_str_dash_when_color(self):
        assert CompressionSettings(_mode='color').bw_threshold_as_str == '-'

    def test_unsharp_mask_as_str_yes(self):
        assert CompressionSettings(
            _unsharp_mask=True
        ).unsharp_mask_as_str == 'Yes'

    def test_unsharp_mask_as_str_no(self):
        assert CompressionSettings().unsharp_mask_as_str == 'No'

    def test_tiff_ccitt_as_str_yes(self):
        assert CompressionSettings(_tiff_ccitt=True).tiff_ccitt_as_str == 'Yes'

    def test_tiff_ccitt_as_str_no(self):
        assert CompressionSettings().tiff_ccitt_as_str == 'No'


class TestValidate:
    def test_valid_settings_pass(self):
        CompressionSettings(_dpi=300, _jpeg_quality=80).validate()

    def test_invalid_dpi_zero(self):
        with pytest.raises(ValueError, match='DPI'):
            CompressionSettings(_dpi=0).validate()

    def test_invalid_dpi_negative(self):
        with pytest.raises(ValueError, match='DPI'):
            CompressionSettings(_dpi=-1).validate()

    def test_invalid_jpeg_quality_zero(self):
        with pytest.raises(ValueError, match='JPEG quality'):
            CompressionSettings(_jpeg_quality=0).validate()

    def test_invalid_jpeg_quality_101(self):
        with pytest.raises(ValueError, match='JPEG quality'):
            CompressionSettings(_jpeg_quality=101).validate()

    def test_valid_jpeg_quality_boundary(self):
        CompressionSettings(_jpeg_quality=1).validate()
        CompressionSettings(_jpeg_quality=100).validate()

    def test_invalid_png_compression_negative(self):
        with pytest.raises(ValueError, match='PNG compression'):
            CompressionSettings(_png_compression=-1).validate()

    def test_invalid_png_compression_10(self):
        with pytest.raises(ValueError, match='PNG compression'):
            CompressionSettings(_png_compression=10).validate()

    def test_valid_png_compression_boundary(self):
        CompressionSettings(_png_compression=0).validate()
        CompressionSettings(_png_compression=9).validate()

    def test_invalid_bw_threshold_negative(self):
        with pytest.raises(ValueError, match='Threshold'):
            CompressionSettings(_bw_threshold=-1).validate()

    def test_invalid_bw_threshold_256(self):
        with pytest.raises(ValueError, match='Threshold'):
            CompressionSettings(_bw_threshold=256).validate()

    def test_valid_bw_threshold_boundary(self):
        CompressionSettings(_bw_threshold=0).validate()
        CompressionSettings(_bw_threshold=255).validate()

    def test_invalid_sharpen_negative(self):
        with pytest.raises(ValueError, match='Sharpen'):
            CompressionSettings(_sharpen=-0.1).validate()

    def test_invalid_sharpen_too_high(self):
        with pytest.raises(ValueError, match='Sharpen'):
            CompressionSettings(_sharpen=3.1).validate()

    def test_invalid_contrast_negative(self):
        with pytest.raises(ValueError, match='Contrast'):
            CompressionSettings(_contrast=-0.1).validate()

    def test_invalid_contrast_too_high(self):
        with pytest.raises(ValueError, match='Contrast'):
            CompressionSettings(_contrast=3.1).validate()


class TestToDict:
    def test_has_all_expected_keys(self):
        d = CompressionSettings().to_dict()
        assert list(d.keys()) == [
            'Mode', 'DPI', 'Format', 'JPEG Quality', 'PNG Level',
            'BW Threshold', 'Sharpen', 'Contrast', 'Unsharp Mask', 'TIFF CCITT',
        ]

    def test_bw_jpeg_defaults(self):
        d = CompressionSettings().to_dict()
        assert d['Mode'] == 'B&W'
        assert d['DPI'] == '300'
        assert d['Format'] == 'JPEG'
        assert d['JPEG Quality'] == '30'
        assert d['PNG Level'] == '-'
        assert d['BW Threshold'] == '150'
        assert d['Unsharp Mask'] == 'No'
        assert d['TIFF CCITT'] == 'No'

    def test_color_png_settings(self):
        d = CompressionSettings(_mode='color', _png_compression=5).to_dict()
        assert d['Mode'] == 'Color'
        assert d['Format'] == 'PNG'
        assert d['PNG Level'] == '5'
        assert d['JPEG Quality'] == '-'
        assert d['BW Threshold'] == '-'
