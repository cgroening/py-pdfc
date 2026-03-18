import questionary
from pdfc.domain.models import CompressionMode


class InputView:
    """Handles interactive input using Questionary."""

    POINTER = '⮕'

    MODE_VALUES = [mode.value for mode in CompressionMode]
    MODE_DEFAULT = 'B&W'
    DPI_VALUES = [72, 150, 200, 300, 400, 600]
    DPI_DEFAULT = 300
    JPEG_QUALITY_VALUES = [20, 35, 50, 70, 90]
    JPEG_QUALITY_DEFAULT = 20
    PNG_COMPRESSION_VALUES = [1, 3, 5, 7, 9]
    PNG_COMPRESSION_DEFAULT = 5
    BW_THRESHOLD_VALUES = [110, 130, 150, 180, 200]
    BW_THRESHOLD_DEFAULT = 150
    SHARPEN_VALUES = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    SHARPEN_DEFAULT = 1.0
    CONTRAST_VALUES = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    CONTRAST_DEFAULT = 1.0
    UNSHARP_MASK_VALUES = ['Yes', 'No']
    UNSHARP_MASK_DEFAULT = 'Yes'
    TIFF_CCITT_VALUES = ['Yes', 'No']
    TIFF_CCITT_DEFAULT = 'Yes'


    def prompt_mode(self) -> CompressionMode:
        """
        Prompt for the compression mode (Color, Grayscale or B&W).

        Returns
        -------
        CompressionMode
            Selected mode (Color, Grayscale or B&W)
        """
        answer = questionary.select(
            'Select the compression mode:',
            choices=self.MODE_VALUES,
            pointer=self.POINTER
        ).ask()

        match answer:
            case 'Color':
                return CompressionMode.COLOR
            case 'Grayscale':
                return CompressionMode.GRAY
            case 'B&W':
                return CompressionMode.BW
            case _:
                return CompressionMode.BW

    def prompt_dpi(self) -> int:
        """
        Prompt for the DPI setting.

        Returns
        -------
        int
            Selected DPI value
        """
        answer = questionary.select(
            'Select the DPI (dots per inch):',
            choices=[str(dpi) for dpi in self.DPI_VALUES],
            pointer=self.POINTER,
            default=str(self.DPI_DEFAULT)
        ).ask()

        return int(answer)

    def prompt_jpeg_quality(self) -> int:
        """
        Prompt for the JPEG quality setting.

        Returns
        -------
        int
            Selected JPEG quality value
        """
        answer = questionary.select(
            'Select the JPEG quality (1-100):',
            choices=[str(q) for q in self.JPEG_QUALITY_VALUES],
            pointer=self.POINTER,
            default=str(self.JPEG_QUALITY_DEFAULT)
        ).ask()

        return int(answer)

    def prompt_png_compression(self) -> int:
        """
        Prompt for the PNG compression level.

        Returns
        -------
        int
            Selected PNG compression level
        """
        answer = questionary.select(
            'Select the PNG compression level (0-9):',
            choices=[str(c) for c in self.PNG_COMPRESSION_VALUES],
            pointer=self.POINTER,
            default=str(self.PNG_COMPRESSION_DEFAULT)
        ).ask()

        return int(answer)

    def prompt_bw_threshold(self) -> int:
        """
        Prompt for the black and white threshold.

        Returns
        -------
        int
            Selected threshold value
        """
        answer = questionary.select(
            'Select the threshold for black and white conversion (0-255):',
            choices=[str(t) for t in self.BW_THRESHOLD_VALUES],
            pointer=self.POINTER,
            default=str(self.BW_THRESHOLD_DEFAULT)
        ).ask()

        return int(answer)

    def prompt_sharpen(self) -> float:
        """
        Prompt for the sharpen setting.

        Returns
        -------
        float
            Selected sharpen value
        """
        answer = questionary.select(
            'Select the sharpening filter (0.0 to 3.0):',
            choices=[str(s) for s in self.SHARPEN_VALUES],
            pointer=self.POINTER,
            default=str(self.SHARPEN_DEFAULT)
        ).ask()

        return float(answer)

    def prompt_contrast(self) -> float:
        """
        Prompt for the contrast setting.

        Returns
        -------
        float
            Selected contrast value
        """
        answer = questionary.select(
            'Select the contrast (0.0 to 3.0):',
            choices=[str(c) for c in self.CONTRAST_VALUES],
            pointer=self.POINTER,
            default=str(self.CONTRAST_DEFAULT)
        ).ask()

        return float(answer)

    def prompt_unsharp_mask(self) -> bool:
        """
        Prompt for unsharp mask application.

        Returns
        -------
        bool
            True if unsharp mask is to be applied
        """
        answer = questionary.select(
            'Apply unsharp mask filter to enhance sharpness?',
            choices=self.UNSHARP_MASK_VALUES,
            pointer=self.POINTER,
            default=self.UNSHARP_MASK_DEFAULT
        ).ask()

        return answer == 'Yes'

    def prompt_tiff_ccitt(self) -> bool:
        """
        Prompt for TIFF CCITT compression application.

        Returns
        -------
        bool
            True if TIFF CCITT compression is to be applied
        """
        answer = questionary.select(
            'Apply CCITT Group 4 compression for B&W images in TIFF format?',
            choices=self.TIFF_CCITT_VALUES,
            pointer=self.POINTER,
            default=self.TIFF_CCITT_DEFAULT
        ).ask()

        return answer == 'Yes'
