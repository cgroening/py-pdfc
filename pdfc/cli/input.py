"""
Interactive input view using Questionary.
"""
import questionary


class InputView:
    """Handles interactive input using Questionary."""

    POINTER = '⮕'

    MODE_CHOICES = ['B&W', 'Grayscale', 'Color']
    MODE_DEFAULT = 'B&W'
    DPI_VALUES = [72, 150, 200, 300, 400, 600]
    DPI_DEFAULT = 300
    FORMAT_CHOICES = ['JPEG', 'PNG']
    JPEG_QUALITY_VALUES = [20, 35, 50, 70, 90]
    JPEG_QUALITY_DEFAULT = 20
    PNG_COMPRESSION_VALUES = [1, 3, 5, 7, 9]
    PNG_COMPRESSION_DEFAULT = 5
    BW_THRESHOLD_VALUES = [110, 130, 150, 180, 200]
    BW_THRESHOLD_DEFAULT = 150
    SHARPEN_VALUES = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    SHARPEN_DEFAULT = 0.0
    CONTRAST_VALUES = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    CONTRAST_DEFAULT = 1.0
    UNSHARP_MASK_VALUES = ['Yes', 'No']
    UNSHARP_MASK_DEFAULT = 'No'
    TIFF_CCITT_VALUES = ['Yes', 'No']
    TIFF_CCITT_DEFAULT = 'No'


    def prompt_mode(self) -> str:
        """
        Prompt for the compression mode.

        Returns
        -------
        str
            One of 'bw', 'gray', 'color'.
        """
        answer = questionary.select(
            'Select the compression mode:',
            choices=self.MODE_CHOICES,
            default=self.MODE_DEFAULT,
            pointer=self.POINTER,
        ).ask()
        match answer:
            case 'Color':
                return 'color'
            case 'Grayscale':
                return 'gray'
            case _:
                return 'bw'

    def prompt_dpi(self) -> int:
        """Prompt for the DPI setting."""
        answer = questionary.select(
            'Select the DPI (dots per inch):',
            choices=[str(d) for d in self.DPI_VALUES],
            default=str(self.DPI_DEFAULT),
            pointer=self.POINTER,
        ).ask()
        return int(answer)

    def prompt_image_format(self) -> str:
        """
        Prompt for the image format (JPEG or PNG).

        Returns
        -------
        str
            'jpeg' or 'png'.
        """
        answer = questionary.select(
            'Select the image format:',
            choices=self.FORMAT_CHOICES,
            default='JPEG',
            pointer=self.POINTER,
        ).ask()
        return answer.lower()

    def prompt_jpeg_quality(self) -> int:
        """Prompt for the JPEG quality setting."""
        answer = questionary.select(
            'Select the JPEG quality (1–100):',
            choices=[str(q) for q in self.JPEG_QUALITY_VALUES],
            default=str(self.JPEG_QUALITY_DEFAULT),
            pointer=self.POINTER,
        ).ask()
        return int(answer)

    def prompt_png_compression(self) -> int:
        """Prompt for the PNG compression level."""
        answer = questionary.select(
            'Select the PNG compression level (0–9):',
            choices=[str(c) for c in self.PNG_COMPRESSION_VALUES],
            default=str(self.PNG_COMPRESSION_DEFAULT),
            pointer=self.POINTER,
        ).ask()
        return int(answer)

    def prompt_bw_threshold(self) -> int:
        """Prompt for the black-and-white threshold."""
        answer = questionary.select(
            'Select the threshold for B&W conversion (0–255):',
            choices=[str(t) for t in self.BW_THRESHOLD_VALUES],
            default=str(self.BW_THRESHOLD_DEFAULT),
            pointer=self.POINTER,
        ).ask()
        return int(answer)

    def prompt_sharpen(self) -> float:
        """Prompt for the sharpening factor."""
        answer = questionary.select(
            'Select the sharpening factor (0.0 = off):',
            choices=[str(s) for s in self.SHARPEN_VALUES],
            default=str(self.SHARPEN_DEFAULT),
            pointer=self.POINTER,
        ).ask()
        return float(answer)

    def prompt_contrast(self) -> float:
        """Prompt for the contrast factor."""
        answer = questionary.select(
            'Select the contrast factor (1.0 = no change):',
            choices=[str(c) for c in self.CONTRAST_VALUES],
            default=str(self.CONTRAST_DEFAULT),
            pointer=self.POINTER,
        ).ask()
        return float(answer)

    def prompt_unsharp_mask(self) -> bool:
        """Prompt for unsharp mask application."""
        answer = questionary.select(
            'Apply unsharp mask filter?',
            choices=self.UNSHARP_MASK_VALUES,
            default=self.UNSHARP_MASK_DEFAULT,
            pointer=self.POINTER,
        ).ask()
        return answer == 'Yes'

    def prompt_tiff_ccitt(self) -> bool:
        """Prompt for TIFF CCITT Group 4 compression (B&W only)."""
        answer = questionary.select(
            'Use TIFF CCITT Group 4 compression? (best file size for B&W)',
            choices=self.TIFF_CCITT_VALUES,
            default=self.TIFF_CCITT_DEFAULT,
            pointer=self.POINTER,
        ).ask()
        return answer == 'Yes'
