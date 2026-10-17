import os
import json
import requests

JWT_API = "https://ff-jwt-gen-api.lovable.app/api/public/token"


def get_jwt(access_token):
    try:
        r = requests.get(
            JWT_API,
            params={"access_token": access_token},
            headers={"Accept": "application/json"},
            timeout=20
        )
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}")
            return None
        try:
            data = r.json()
        except ValueError:
            if r.text.strip().startswith("eyJ"):
                return r.text.strip()
            return None

        if isinstance(data, dict):
            token = (
                data.get("token") or
                data.get("jwt") or
                data.get("jwt_token") or
                data.get("access_token")
            )
            if not token and isinstance(data.get("data"), dict):
                token = data["data"].get("token") or data["data"].get("jwt")
            if not token and isinstance(data.get("data"), str):
                token = data["data"]
            if token:
                return token.replace("Bearer ", "").strip()

        if isinstance(data, str) and data.startswith("eyJ"):
            return data.strip()
        return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None


def parse_tokens(raw):
    raw = raw.strip()
    if not raw:
        return []
    try:
        p = json.loads(raw)
        if isinstance(p, list):
            return [str(t).strip() for t in p if t]
        if isinstance(p, str):
            return [p.strip()]
    except (json.JSONDecodeError, ValueError):
        pass
    return [t.strip() for t in raw.replace(",", "\n").split("\n") if t.strip()]


def main():
    print("Starting...")
    raw = os.environ.get("ACCESS_TOKENS", "").strip()
    if not raw:
        print("ERROR: ACCESS_TOKENS secret not set")
        return

    tokens = parse_tokens(raw)
    if not tokens:
        print("No valid tokens")
        return

    print(f"Found {len(tokens)} access token(s)")

    new_tokens = []
    for i, at in enumerate(tokens, 1):
        print(f"[{i}/{len(tokens)}] Generating...")
        jwt = get_jwt(at)
        if jwt:
            new_tokens.append({"token": jwt})
            print(f"  OK ({jwt[:30]}...)")
        else:
            print(f"  FAILED")

    print(f"Success: {len(new_tokens)}/{len(tokens)}")

    if not new_tokens:
        print("No new tokens - keeping old file")
        return

    if os.path.exists("token_ind.json"):
        try:
            with open("token_ind.json", "r") as f:
                old = f.read()
            with open("token_ind.json.bak", "w") as f:
                f.write(old)
            print("Old file backed up")
        except Exception as e:
            print(f"Backup failed: {e}")

    with open("token_ind.json", "w") as f:
        json.dump(new_tokens, f, indent=2)
    print(f"Saved {len(new_tokens)} tokens to token_ind.json")


if __name__ == "__main__":
    main()
