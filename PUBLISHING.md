# Publishing JLDiff to PyPI

Step-by-step guide for releasing a new version of JLDiff.

---

## One-Time Setup (first release only)

### 1. Register a Trusted Publisher on PyPI

1. Create a PyPI account at <https://pypi.org/account/register/> if you don't have one
2. Go to <https://pypi.org/manage/account/publishing/>
3. Under **"Add a new pending publisher"**, fill in:
   - **PyPI project name:** `JLDiff`
   - **Owner:** `JEdward7777`
   - **Repository:** `JLDiff`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`
4. Click **Add**

This tells PyPI to trust the GitHub Actions workflow — no API tokens needed.

### 2. Create the `pypi` environment on GitHub

1. Go to <https://github.com/JEdward7777/JLDiff/settings/environments>
2. Click **New environment**, name it `pypi`
3. (Optional) Enable **"Required reviewers"** for manual approval before each publish

---

## Release Process

### Step 1: Update the version

Edit `pyproject.toml` and bump the `version` field:

```toml
version = "1.0.1"  # change this to the new version
```

### Step 2: Test the build locally

```bash
rm -rf dist/
uv build
```

Verify both files were created:

```bash
ls dist/
# jldiff-1.0.1-py3-none-any.whl
# jldiff-1.0.1.tar.gz
```

(Optional) Smoke-test the wheel:

```bash
uv run --isolated --no-project \
  --with dist/jldiff-1.0.1-py3-none-any.whl \
  python3 -c "from JLDiff import compute_diff; print('OK')"
```

### Step 3: Commit the version bump

```bash
git add pyproject.toml
git commit -m "Release v1.0.1"
```

### Step 4: Tag the release

```bash
git tag v1.0.1
```

### Step 5: Push the commit and tag

```bash
git push origin main --tags
```

### Step 6: Create a GitHub Release

Go to:

> **<https://github.com/JEdward7777/JLDiff/releases/new>**

1. Select the tag you just pushed (e.g., `v1.0.1`)
2. Set the release title (e.g., `v1.0.1`)
3. Write release notes describing what changed
4. Click **Publish release**

This triggers the `.github/workflows/publish.yml` workflow, which builds the package and publishes it to PyPI automatically via Trusted Publishing.

### Step 7: Verify

Wait a minute or two for the workflow to complete, then check:

- **GitHub Actions:** <https://github.com/JEdward7777/JLDiff/actions>
- **PyPI page:** <https://pypi.org/project/JLDiff/>

Test that it installs:

```bash
pip install JLDiff==1.0.1
jldiff --help
```

---

## Quick Reference (copy-paste for repeat releases)

```bash
# 1. Edit pyproject.toml version, then:
rm -rf dist/
uv build

# 2. Commit, tag, push
git add pyproject.toml
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags

# 3. Go create the release:
#    https://github.com/JEdward7777/JLDiff/releases/new
#
# 4. Verify:
#    https://pypi.org/project/JLDiff/
```

---

## Manual Publishing (without GitHub Actions)

If you ever need to publish manually (e.g., from your local machine):

```bash
# Build
rm -rf dist/
uv build

# Publish (will prompt for credentials)
uv publish --token pypi-YOUR_API_TOKEN
```

To create an API token: go to <https://pypi.org/manage/account/> → **API tokens** → **Add API token**.

---

## References

- [uv build & publish guide](https://docs.astral.sh/uv/guides/package/)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions publishing guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows)
