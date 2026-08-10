# SNSOC Backend Review — Findings & Fixes

## 🔴 Critical — fix these regardless of anything else

1. **Live secrets are committed to the public repo (`.env`).**
   This file contains a real AbuseIPDB API key, admin login credentials, and
   the Flask `SECRET_KEY`. Anyone can see them right now on GitHub.
   → **Rotate the AbuseIPDB key and change the admin password immediately.**
   Removing the file from a future commit is not enough — it's still in
   git history. See "Scrubbing history" below.

2. **`app.py` also hardcoded a real admin email + password** in `seed_db()`
   (`sivachaitanya72@gmail.com` / `siva2580`), independent of the `.env` file.
   Fixed: the app now reads `ADMIN_USER`/`ADMIN_PASS` from the environment,
   and if neither is set, generates a random one-time password and prints
   it once via a warning instead of using a fixed value.

3. **`/api/intel/config` had no authentication.** Any unauthenticated
   request could overwrite the live AbuseIPDB API key used by the whole
   server. Fixed: now requires login (`@login_required`).

4. **`snsoc.db` (668 KB) and `__pycache__/` directories are committed.**
   A database file shouldn't be version-controlled, and pycache is just
   build noise. Added a `.gitignore` and instructions to untrack them.

## 🟠 Real bugs

5. **Duplicate/unused `SocketIO` instance.** `extensions.py` defines a
   shared `socketio` and a `limiter` (Flask-Limiter, i.e. rate limiting),
   but `app.py` never imported either — it created its own separate
   `SocketIO()` instead. The practical effect: **Flask-Limiter is installed,
   configured, and completely inert — there is currently no rate limiting
   anywhere in the app.** Fixed: `app.py` now imports and initializes both
   from `extensions.py`.

6. **CORS was wide open** (`Access-Control-Allow-Origin: *`) while also
   allowing the `Authorization` header — a permissive combination for an
   app that handles login sessions. Fixed: origins are now driven by an
   `ALLOWED_ORIGINS` env var (comma-separated); nothing is allowed by
   default until you set it.

7. **`auth.py` login would 500-error on a missing username/password**
   instead of showing "Invalid credentials" (`None.encode()` throws).
   Fixed with a null check.

## 🟡 Worth knowing about (not changed — needs a decision from you)

8. **The `firewall/` module (iptables/netsh backends) is fully built but
   never used anywhere.** `api/block.py`'s "block IP" endpoint only writes
   to the database — it doesn't actually call the firewall to block
   traffic. If blocking is supposed to be a real feature, `add_block`/
   `remove_block` need to call into `firewall/base.py`'s backend.

9. **The mobile app calls `/api/telemetry/*` and `/api/intel/lookup` with
   no authentication at all** (confirmed in `src/screens/*.js` — no
   session cookie, no token). I only locked down `/api/intel/config`
   (the one that overwrites your live API key) since it was the most
   severe and least likely to be relied on by mobile. Properly securing
   the rest means adding a real mobile auth mechanism (e.g. an API token
   per device) — that's a bigger design change I didn't want to make
   silently, since it could break the app until the client is updated.

## Files changed
- `app.py`
- `auth.py`
- `config.py`
- `extensions.py`
- `api/intel.py`
- `render.yaml`
- `.env.example` (placeholder values only)
- `.gitignore` (new)

## How to apply this to your repo

From inside your local clone of `SNSOC`:

```bash
# 1. Copy the fixed files over your existing ones (adjust the path to
#    wherever you extracted this download)
cp path/to/fixed/app.py app.py
cp path/to/fixed/auth.py auth.py
cp path/to/fixed/config.py config.py
cp path/to/fixed/extensions.py extensions.py
cp path/to/fixed/api/intel.py api/intel.py
cp path/to/fixed/render.yaml render.yaml
cp path/to/fixed/.env.example .env.example
cp path/to/fixed/.gitignore .gitignore

# 2. Stop tracking secrets/build artifacts (keeps them on disk, just untracks them)
git rm --cached .env
git rm --cached snsoc.db
git rm -r --cached __pycache__ api/__pycache__ engine/__pycache__ appium_tests/__pycache__ 2>/dev/null

# 3. Commit
git add .
git commit -m "Security fixes: remove hardcoded secrets, lock down /api/intel/config, fix CORS, wire up rate limiter, add .gitignore"

# 4. Push
git push origin main
```

### Scrubbing the leaked secrets from git history (do this too)

Untracking `.env` only stops *future* commits from including it — the real
API key and password are still visible in old commits. After rotating the
key/password (step 0, do this first regardless), you can scrub history with:

```bash
pip install git-filter-repo
git filter-repo --path .env --path snsoc.db --invert-paths --force
git push origin --force --all
```

This rewrites history, so anyone else with a clone will need to re-clone.
Since this is a personal public repo, that's usually fine — just make sure
no one else is depending on the current commit hashes.

### After pulling this in

Set real values via environment variables (not committed):
```
SECRET_KEY=<random value, e.g. python -c "import secrets; print(secrets.token_hex(32))">
ADMIN_USER=<your choice>
ADMIN_PASS=<your choice>
ABUSEIPDB_API_KEY=<your NEW rotated key>
ALLOWED_ORIGINS=https://your-dashboard-domain,https://your-mobile-app-origin
```
