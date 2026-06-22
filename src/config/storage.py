"""Custom static files storage.

Manifest static storage hashes asset filenames and rewrites references
(``url(...)`` in CSS, ``sourceMappingURL`` in JS) to the hashed names. Many
third-party bundles (Bootstrap, lightbox, ...) ship dangling references to
source-map / asset files they don't actually include, which makes strict
manifest hashing abort ``collectstatic`` with ``MissingFileError``.

``TolerantManifestMixin`` keeps full hashing but tolerates those dangling
references instead of failing the whole build. It is shared by the local
(WhiteNoise) and S3 static backends so behaviour is identical in dev and prod.
"""
from whitenoise.storage import CompressedManifestStaticFilesStorage


class TolerantManifestMixin:
    """Make manifest hashing tolerant of dangling asset references."""

    # Don't raise at runtime if a name is missing from the manifest.
    manifest_strict = False

    def post_process(self, *args, **kwargs):
        for name, hashed_name, processed in super().post_process(*args, **kwargs):
            # Swallow "file could not be found" errors from dangling references
            # (e.g. unbundled .map files) so they don't abort collectstatic.
            if isinstance(processed, Exception) and "could not be found" in str(processed):
                continue
            yield name, hashed_name, processed


class WhiteNoiseStaticFilesStorage(TolerantManifestMixin, CompressedManifestStaticFilesStorage):
    """Local/dev static storage: hashed names + brotli/gzip, served by WhiteNoise."""
