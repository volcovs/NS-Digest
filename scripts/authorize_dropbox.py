import os

import dropbox  # noqa: F401  (imported for side-effect parity / availability check)
from dotenv import load_dotenv
from dropbox.oauth import DropboxOAuth2FlowNoRedirect


def main() -> None:
    load_dotenv()

    app_key = os.environ["DROPBOX_APP_KEY"]
    app_secret = os.environ["DROPBOX_APP_SECRET"]

    auth_flow = DropboxOAuth2FlowNoRedirect(
        app_key,
        app_secret,
        token_access_type="offline",
    )

    authorize_url = auth_flow.start()

    print("\nOpen this URL in your browser:\n")
    print(authorize_url)

    print("\nAfter authorizing the application, copy the authorization code here.")
    code = input("\nAuthorization code: ").strip()

    result = auth_flow.finish(code)

    print("\nAuthentication successful!")
    print("\nAdd this to your .env:\n")
    print(f"DROPBOX_REFRESH_TOKEN={result.refresh_token}")


if __name__ == "__main__":
    main()
