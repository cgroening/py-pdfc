from pdfc.domain.models import CompressionSettings


class CompressionService:
    """
    Handles the business logic for PDF compression.

    Receives compression settings from the CLI layer, validates them and
    executes the compression. Knows the storage layer only via interfaces
    (not yet implemented).
    """

    def process(self, settings: CompressionSettings) -> None:
        """
        Validates the settings and compresses the PDF.

        Parameters
        ----------
        settings : CompressionSettings
            The compression settings to use.

        Raises
        ------
        ValueError
            If the settings are invalid.
        """
        settings.validate()
        # TODO: Implement actual PDF compression
