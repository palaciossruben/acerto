from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class MyManifestStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False
    ignore_patterns = ['test.js', 'start.js']  # your custom ignore list

