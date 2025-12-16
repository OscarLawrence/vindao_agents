# Publishing Guide

This document describes how to publish new versions of `vindao_agents` to PyPI.

## Prerequisites

1. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

2. Set up PyPI trusted publishing:
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new pending publisher:
     - PyPI Project Name: `vindao_agents`
     - Owner: `vindao` (your GitHub username)
     - Repository name: `vindao_agents`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`

## Version Bumping

We use `bump2version` for semantic versioning. Choose the appropriate bump type:

### Patch Release (0.1.0 → 0.1.1)
Bug fixes and minor changes:
```bash
bump2version patch
```

### Minor Release (0.1.0 → 0.2.0)
New features, backward-compatible:
```bash
bump2version minor
```

### Major Release (0.1.0 → 1.0.0)
Breaking changes:
```bash
bump2version major
```

This will:
1. Update version in `pyproject.toml` and `src/vindao_agents/__init__.py`
2. Create a git commit with the version bump
3. Create a git tag (e.g., `v0.2.0`)

## Publishing Process

### 1. Update Changelog

Before bumping the version, update `CHANGELOG.md`:

```markdown
## [0.2.0] - 2025-12-20

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix Z
```

### 2. Bump Version

```bash
# Choose patch, minor, or major
bump2version minor
```

### 3. Push Changes and Tags

```bash
git push origin main
git push origin --tags
```

### 4. Automated Publishing

GitHub Actions will automatically:
1. Run tests on all platforms
2. Build the distribution packages
3. Publish to PyPI (using trusted publishing)
4. Create a GitHub release with auto-generated notes

### 5. Verify Publication

Check that the package is available:
```bash
pip install --upgrade vindao_agents
```

Visit: https://pypi.org/project/vindao_agents/

## Manual Publishing (Fallback)

If automated publishing fails, you can publish manually:

```bash
# Build the package
uv build

# Upload to PyPI (requires API token)
uv publish --token <your-pypi-token>
```

## Testing Before Release

### Test Installation Locally

```bash
# Build the package
uv build

# Install in a fresh environment
uv pip install dist/vindao_agents-*.whl

# Test the CLI
agent --version
agent --list
```

### Test on TestPyPI (Recommended for first release)

1. Create TestPyPI account: https://test.pypi.org/
2. Upload to TestPyPI:
   ```bash
   uv publish --repository testpypi --token <test-pypi-token>
   ```
3. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ vindao_agents
   ```

## Troubleshooting

### Build Failures

Check that all files are properly included:
```bash
uv build
tar -tzf dist/vindao_agents-*.tar.gz | grep -E '\\.md$|\\.py$'
```

### Import Errors

Ensure agent templates are included in the package:
```bash
python -c "from pathlib import Path; import vindao_agents; print(Path(vindao_agents.__file__).parent / 'agents')"
```

### Version Conflicts

If version is out of sync:
```bash
# Check current versions
grep "version = " pyproject.toml
grep "__version__ = " src/vindao_agents/__init__.py

# Manually sync if needed, then:
git commit -am "Fix version sync"
```

## Release Checklist

- [ ] Update CHANGELOG.md with changes
- [ ] Run tests locally: `pytest`
- [ ] Bump version: `bump2version [patch|minor|major]`
- [ ] Push changes: `git push origin main`
- [ ] Push tags: `git push origin --tags`
- [ ] Verify GitHub Actions workflow completes
- [ ] Check PyPI package: https://pypi.org/project/vindao_agents/
- [ ] Test installation: `pip install vindao_agents`
- [ ] Verify CLI works: `agent --version`
- [ ] Check GitHub release: https://github.com/vindao/vindao_agents/releases

## First Release Special Steps

Before the first release:

1. Create PyPI account at https://pypi.org/
2. Set up trusted publishing (see Prerequisites)
3. Test on TestPyPI first
4. Create a release branch if desired
5. Announce the release

## Support

For issues with publishing, contact: vindao@outlook.com
