from pathlib import Path
import yaml


DEFAULT_PATH = Path.home() / '.config' / 'pdfc' / 'presets.yaml'

# Maps YAML field names to CompressionSettings constructor keyword arguments.
_FIELD_MAP: dict[str, str] = {
    'mode':            '_mode',
    'dpi':             '_dpi',
    'threshold':       '_bw_threshold',
    'jpeg_quality':    '_jpeg_quality',
    'png_compression': '_png_compression',
    'sharpen':         '_sharpen',
    'contrast':        '_contrast',
    'unsharp_mask':    '_unsharp_mask',
    'tiff_ccitt':      '_tiff_ccitt',
}


class PresetsStorage:
    """Reads presets from a YAML file and returns them as settings dicts."""

    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self._path = path

    def load(self) -> list[dict]:
        """
        Loads all presets from the YAML file.

        Returns
        -------
        list[dict]
            Each dict contains 'name' and CompressionSettings kwargs
            (keys prefixed with '_').

        Raises
        ------
        FileNotFoundError
            If the presets file does not exist.
        ValueError
            If the YAML is malformed or missing the 'presets' key.
        """
        if not self._path.exists():
            raise FileNotFoundError(
                f'Presets file not found: {self._path}\n'
                f'Create it to use the compare command.'
            )

        with open(self._path) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict) or 'presets' not in data:
            raise ValueError(
                f'Presets file must contain a top-level "presets" list:\n'
                f'{self._path}'
            )

        result: list[dict] = []
        for i, preset in enumerate(data['presets']):
            if 'name' not in preset:
                raise ValueError(
                    f'Preset at index {i} is missing a "name" field.'
                )
            entry: dict = {'name': preset['name']}
            for yaml_key, settings_key in _FIELD_MAP.items():
                if yaml_key in preset:
                    entry[settings_key] = preset[yaml_key]
            result.append(entry)

        return result
