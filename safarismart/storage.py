"""
Custom storage backend for static files that ignores missing source maps
"""
from whitenoise.storage import CompressedManifestStaticFilesStorage


class ForgivingManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    Custom storage that doesn't fail on missing source map files.
    Source maps (.map files) are used for debugging and aren't critical for production.
    """
    
    def hashed_name(self, name, content=None, filename=None):
        """
        Override to catch missing file errors for source maps and other non-critical files.
        """
        try:
            return super().hashed_name(name, content, filename)
        except ValueError as e:
            # If it's a missing source map file, just return the original name
            if '.map' in name or 'sourceMappingURL' in str(e):
                return name
            # For other missing files, re-raise the error
            raise
    
    manifest_strict = False  # Don't fail on missing files in manifest
