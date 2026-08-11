import dropbox

from nsdigest.config import settings


def get_dropbox_client() -> dropbox.Dropbox:
    return dropbox.Dropbox(
        oauth2_refresh_token=settings.dropbox_refresh_token,
        app_key=settings.dropbox_app_key,
        app_secret=settings.dropbox_app_secret,
    )


def _normalize_path(path: str) -> str:
    path = path.replace("\\", "/").strip()

    if not path:
        raise ValueError("Dropbox path cannot be empty")

    if not path.startswith("/"):
        path = "/" + path

    # Collapse accidental duplicate slashes.
    while "//" in path:
        path = path.replace("//", "/")

    return path


class DropboxStorage:
    def __init__(self) -> None:
        self.client = dropbox.Dropbox(
            oauth2_refresh_token=settings.dropbox_refresh_token,
            app_key=settings.dropbox_app_key,
            app_secret=settings.dropbox_app_secret,
        )

        self.root = settings.dropbox_root.strip("/")

    def _path(self, path: str) -> str:
        # Apply the optional DROPBOX_ROOT prefix, then normalize. This keeps
        # the Python writer and the Netlify reader (news.mjs) pointed at the
        # same folder for any value of DROPBOX_ROOT.
        path = path.lstrip("/")

        if self.root:
            path = f"/{self.root}/{path}"
        else:
            path = f"/{path}"

        return _normalize_path(path)

    def write_text(self, path: str, content: str) -> None:
        self.client.files_upload(
            content.encode("utf-8"),
            self._path(path),
            mode=dropbox.files.WriteMode.overwrite,
        )

    def read_text(self, path: str) -> str:
        _, response = self.client.files_download(
            self._path(path)
        )

        return response.content.decode("utf-8")

    def delete(self, path: str) -> None:
        self.client.files_delete_v2(
            self._path(path)
        )

    def exists(self, path: str) -> bool:
        try:
            self.client.files_get_metadata(self._path(path))
            return True
        except dropbox.exceptions.ApiError:
            return False
