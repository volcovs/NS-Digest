from nsdigest.storage.dropbox import get_dropbox_client


def test_dropbox_connection():
    dbx = get_dropbox_client()

    account = dbx.users_get_current_account()

    assert account.name.display_name
