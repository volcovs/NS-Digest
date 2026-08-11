from nsdigest.storage.dropbox import DropboxStorage


def test_dropbox_write_read_delete():
    storage = DropboxStorage()

    path = "test/test.txt"
    content = "NS-Digest Dropbox integration works."

    storage.write_text(path, content)

    assert storage.exists(path)

    result = storage.read_text(path)

    assert result == content

    storage.delete(path)

    assert not storage.exists(path)
