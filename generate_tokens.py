import os
import json
import requests
import urllib3

urllib3.disable_warnings()

JWT_API = "https://ob55-jwt-guest.vercel.app/token"
OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"

def get_access_token(uid, password):
    payload = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }

    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(SM-M526B;Android 13;pt;BR;)",
        "Connection": "Keep-Alive"
    }

    try:
        resp = requests.post(
            OAUTH_URL,
            data=payload,
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("access_token")
    except (requests.RequestException, ValueError):
        return None


def get_jwt(uid, password):
    try:
        response = requests.get(
            JWT_API,
            params={"uid": uid, "password": password},
            headers={"Accept": "application/json"},
            timeout=20
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if isinstance(data, dict):
            token = (
                data.get("token")
                or data.get("jwt")
                or data.get("jwt_token")
                or data.get("access_token")
            )

            if not token and isinstance(data.get("data"), dict):
                token = (
                    data["data"].get("token")
                    or data["data"].get("jwt")
                )

            return token.replace("Bearer ", "").strip() if token else None

        if isinstance(data, str) and data.startswith("eyJ"):
            return data.strip()

    except (requests.RequestException, ValueError):
        return None

    return None


def main():
    print("Starting Auto-Generator...")

    if not os.path.exists("accounts.json"):
        print("ERROR: accounts.json not found.")
        return

    with open("accounts.json", "r") as f:
        accounts = json.load(f)

    print(f"Found {len(accounts)} accounts")
    new_tokens = []

    for i, acc in enumerate(accounts, 1):
        uid = str(acc.get("uid", "")).strip()
        pwd = str(acc.get("password", "")).strip()

        if not uid or not pwd:
            continue

        print(f"[{i}/{len(accounts)}] Processing UID: {uid}")

        jwt = get_jwt(uid, pwd)

        if jwt:
            new_tokens.append({"token": jwt})
            print("  OK JWT Generated")
        else:
            print("  FAILED JWT")

    if new_tokens:
        with open("token_ind.json", "w") as f:
            json.dump(new_tokens, f, indent=2)

        print(f"\nSaved {len(new_tokens)} tokens to token_ind.json")
    else:
        print("\nNo tokens generated.")


if __name__ == "__main__":
    main()
