"""Custom static files storage.

``CompressedManifestStaticFilesStorage`` hashes asset filenames and rewrites
references (``url(...)`` in CSS, ``sourceMappingURL`` in JS) to the hashed
names. Many third-party bundles (Bootstrap, lightbox, ...) ship dangling
references to source-map / asset files they don't actually include, which makes
strict manifest hashing abort ``collectstatic`` with ``MissingFileError``.

This subclass keeps full hashing + compression but tolerates those dangling
references instead of failing the whole build.
"""
from whitenoise.storage import CompressedManifestStaticFilesStorage


class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
    # Don't raise at runtime if a name is missing from the manifest.
    manifest_strict = False

    def post_process(self, *args, **kwargs):
        for name, hashed_name, processed in super().post_process(*args, **kwargs):
            # Swallow "file could not be found" errors from dangling references
            # (e.g. unbundled .map files) so they don't abort collectstatic.
            if isinstance(processed, Exception) and "could not be found" in str(processed):
                continue
            yield name, hashed_name, processed
