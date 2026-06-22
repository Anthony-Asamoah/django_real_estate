"""Storage backends.

Production (``STORAGE_BACKEND=s3``) serves static files and public media from
S3 via the classes in :mod:`infrastructure.storage.s3_backends`, wired through
Django's ``STORAGES`` setting.
"""
