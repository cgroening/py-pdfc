import pytest
import yaml
from pdfc.storage.presets_storage import PresetsStorage


class TestPresetsStorageLoad:
    def test_raises_file_not_found_when_missing(self, tmp_path):
        storage = PresetsStorage(path=tmp_path / 'nonexistent.yaml')
        with pytest.raises(FileNotFoundError, match='Presets file not found'):
            storage.load()

    def test_raises_value_error_when_presets_key_missing(self, tmp_path):
        f = tmp_path / 'presets.yaml'
        f.write_text('something: else\n')
        with pytest.raises(ValueError, match='presets'):
            PresetsStorage(path=f).load()

    def test_raises_value_error_when_preset_missing_name(self, tmp_path):
        data = {'presets': [{'mode': 'bw', 'dpi': 300}]}
        f = tmp_path / 'presets.yaml'
        f.write_text(yaml.dump(data))
        with pytest.raises(ValueError, match='name'):
            PresetsStorage(path=f).load()

    def test_returns_list_for_valid_file(self, tmp_path):
        data = {'presets': [{'name': 'preset-a', 'mode': 'bw', 'dpi': 300}]}
        f = tmp_path / 'presets.yaml'
        f.write_text(yaml.dump(data))
        result = PresetsStorage(path=f).load()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_maps_yaml_keys_to_settings_keys(self, tmp_path):
        data = {'presets': [{
            'name': 'preset1',
            'mode': 'gray',
            'dpi': 150,
            'jpeg_quality': 60,
            'threshold': 128,
            'png_compression': 4,
            'sharpen': 1.5,
            'contrast': 1.2,
            'unsharp_mask': True,
            'tiff_ccitt': False,
        }]}
        f = tmp_path / 'presets.yaml'
        f.write_text(yaml.dump(data))
        entry = PresetsStorage(path=f).load()[0]
        assert entry['name'] == 'preset1'
        assert entry['_mode'] == 'gray'
        assert entry['_dpi'] == 150
        assert entry['_jpeg_quality'] == 60
        assert entry['_bw_threshold'] == 128
        assert entry['_png_compression'] == 4
        assert entry['_sharpen'] == 1.5
        assert entry['_contrast'] == 1.2
        assert entry['_unsharp_mask'] is True
        assert entry['_tiff_ccitt'] is False

    def test_multiple_presets_are_returned_in_order(self, tmp_path):
        data = {'presets': [
            {'name': 'alpha', 'mode': 'bw'},
            {'name': 'beta', 'mode': 'color'},
        ]}
        f = tmp_path / 'presets.yaml'
        f.write_text(yaml.dump(data))
        result = PresetsStorage(path=f).load()
        assert len(result) == 2
        assert result[0]['name'] == 'alpha'
        assert result[1]['name'] == 'beta'

    def test_ignores_unknown_yaml_keys(self, tmp_path):
        data = {'presets': [{'name': 'p', 'unknown_key': 'value'}]}
        f = tmp_path / 'presets.yaml'
        f.write_text(yaml.dump(data))
        entry = PresetsStorage(path=f).load()[0]
        assert 'unknown_key' not in entry
        assert '_unknown_key' not in entry

    def test_partial_preset_only_maps_present_keys(self, tmp_path):
        data = {'presets': [{'name': 'minimal', 'mode': 'bw'}]}
        f = tmp_path / 'presets.yaml'
        f.write_text(yaml.dump(data))
        entry = PresetsStorage(path=f).load()[0]
        assert '_mode' in entry
        assert '_dpi' not in entry
        assert '_jpeg_quality' not in entry
