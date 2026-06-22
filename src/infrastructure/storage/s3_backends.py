from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from storages.backends.s3 import S3ManifestStaticStorage

from config.storage import TolerantManifestMixin


class StaticStorage(TolerantManifestMixin, S3ManifestStaticStorage):
    """S3 storage for collected static files.

    Filenames are content-hashed, so a 1-year immutable cache is safe: a changed
    asset gets a new hash (and a new URL), so clients never see a stale file.
    Put CloudFront in front of the bucket for edge caching + compression.
    """

    def __init__(self, *args, **kwargs):
        kwargs["bucket_name"] = getattr(settings, "AWS_S3_BUCKET_STATIC", None)
        kwargs["region_name"] = getattr(settings, "AWS_S3_REGION_NAME", "us-east-1")
        kwargs["querystring_auth"] = False
        kwargs["object_parameters"] = {"CacheControl": "max-age=31536000, immutable"}
        kwargs["location"] = getattr(settings, "BUCKET_PREFIX", "") or ""
        custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN_STATIC", None)
        if custom_domain:
            kwargs["custom_domain"] = custom_domain
        super().__init__(*args, **kwargs)


class PublicMediaStorage(S3Boto3Storage):
    """Storage for public media files (Wagtail images & uploaded videos).

    ``file_overwrite=False`` means a replaced upload gets a new key (and URL),
    so a moderate cache is safe and never serves a stale file.
    """

    def __init__(self, *args, **kwargs):
        kwargs["bucket_name"] = getattr(settings, "AWS_S3_BUCKET_PUBLIC", None)
        kwargs["region_name"] = getattr(settings, "AWS_S3_REGION_NAME", "us-east-1")
        kwargs["querystring_auth"] = False
        kwargs["file_overwrite"] = False
        kwargs["object_parameters"] = {"CacheControl": "max-age=86400"}  # 1 day
        kwargs["location"] = getattr(settings, "BUCKET_PREFIX", "") or ""
        # Optional: CDN hostname (Cloudflare) in front of the media bucket
        custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN_MEDIA", None)
        if custom_domain:
            kwargs["custom_domain"] = custom_domain
        super().__init__(*args, **kwargs)
