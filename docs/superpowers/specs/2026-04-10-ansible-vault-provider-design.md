# Ansible Vault Secrets Provider — Design Spec

**Date:** 2026-04-10
**Status:** Draft
**Author:** Derek (with AI assist)

---

## Summary

Add an Ansible Vault provider to the `hyperi_pylib.secrets` module, enabling Python services to read secrets from Ansible Vault-encrypted files. This provider sits between the existing `FileProvider` (plaintext files) and `OpenBaoProvider` (dedicated secrets server) — offering encrypted-at-rest secrets with zero infrastructure overhead.

## Use Case

Designed primarily for SME networks that need encrypted-at-rest secrets without the operational overhead of a dedicated secrets server (OpenBao, AWS Secrets Manager, etc.). Also suitable for any environment where Ansible Vault is already the team's standard for secret management — dev/test environments, CI pipelines, or hybrid setups where some secrets live in vault files alongside infrastructure-as-code.

**When to use this provider:**

- Small-to-medium deployments where running a secrets server is overkill
- Teams already using Ansible for configuration management
- Environments transitioning from plaintext config files to encrypted secrets
- Dev/test environments that need secrets but not full secrets infrastructure
- Air-gapped or restricted networks where SaaS secrets managers aren't available

**When NOT to use this provider:**

- High-availability requirements (use OpenBao or a cloud secrets manager)
- Dynamic secret generation / rotation (use OpenBao)
- Fine-grained access control per secret (use OpenBao or cloud provider)

## Approach

Thin wrapper around the [`ansible-vault`](https://pypi.org/project/ansible-vault/) PyPI package (v4.1.0+, Production/Stable, Python 3.10-3.13). This package provides `Vault.load_raw()` and `Vault.load()` for decryption without requiring the full `ansible-core` dependency.

## Provider Interface

Implements `SecretProvider` ABC from `providers/base.py`:

```python
class AnsibleVaultProvider(SecretProvider):
    name = "ansible_vault"

    def __init__(self, config: AnsibleVaultConfig) -> None: ...
    async def get_async(self, path: str, key: str | None = None) -> SecretValue: ...
    def get_sync(self, path: str, key: str | None = None) -> SecretValue: ...
    async def health_check_async(self) -> bool: ...
    def health_check_sync(self) -> bool: ...
```

Async methods delegate to sync — Ansible Vault is file-based I/O, no network calls.

## Configuration

### Dataclass

```python
@dataclass
class AnsibleVaultConfig:
    password: str | None = None           # Resolved password (from env or file)
    password_file: str | None = None      # Path to password file (fallback)
```

No `timeout_secs` — this is a file-based provider with no network calls.

### Dict Config (via `SecretsManager.from_config()`)

```python
{
    "ansible_vault": {
        "password_file": "/etc/ansible/vault_pass"  # optional fallback
    }
}
```

Minimal config — most deployments just set the environment variable and go.

### Password Resolution

Priority order (checked at provider init):

1. `ANSIBLE_VAULT_PASSWORD` environment variable
2. `ANSIBLE_VAULT_PASS` environment variable (common shorthand)
3. `ANSIBLE_VAULT_PASSWORD_FILE` environment variable — read file at this path
4. `password_file` from config dict — read file at this path

Password is resolved once at init and stored in memory. Provider raises `ProviderError` at init if no password source is found.

## Decryption Flow

1. Read vault-encrypted file from `path` (must start with `$ANSIBLE_VAULT;` header)
2. Decrypt using `ansible_vault.Vault(password).load_raw(content)`
3. Auto-detect content type:
   - Try `yaml.safe_load()` on decrypted content
   - If valid YAML dict and `key` provided — extract the field value
   - If valid YAML dict and no `key` — return full YAML content as bytes
   - If not a YAML dict (raw value, scalar, or parse failure) — return raw decrypted bytes
4. Return `SecretValue` with:
   - `data`: the resolved bytes
   - `fetched_at`: current UTC timestamp
   - `version`: `"{mtime}:{size}"` derived from file stat (same pattern as `FileProvider`)
   - `source`: `"ansible_vault"`

## Error Handling

| Scenario | Exception |
|---|---|
| No password source configured | `ProviderError` at init |
| Password file doesn't exist | `ProviderError` at init |
| Password file is empty | `ProviderError` at init |
| Vault file not found | `SecretNotFoundError` |
| Wrong password (decryption fails) | `ProviderError` |
| Key requested but content is not YAML dict | `ProviderError` |
| Key requested but key not in YAML | `SecretNotFoundError` |
| Corrupted vault file (bad header/content) | `ProviderError` |
| Permission denied on vault file | `ProviderError` |

## Registration

### `ProviderType` enum (in `types.py`)

```python
class ProviderType(Enum):
    FILE = "file"
    OPENBAO = "openbao"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ANSIBLE_VAULT = "ansible_vault"
```

### Provider init (`providers/__init__.py`)

```python
try:
    from .ansible_vault import ANSIBLE_VAULT_AVAILABLE, AnsibleVaultProvider
except ImportError:
    AnsibleVaultProvider = None
    ANSIBLE_VAULT_AVAILABLE = False
```

### Manager registration (`manager.py`)

```python
if "ansible_vault" in config:
    try:
        from .providers.ansible_vault import AnsibleVaultProvider
        av_config = cls._parse_ansible_vault_config(config["ansible_vault"])
        providers["ansible_vault"] = AnsibleVaultProvider(av_config)
    except ImportError:
        logger.warning(
            "Ansible Vault provider not available. "
            "Install with: pip install hyperi-pylib[secrets-ansible-vault]"
        )
```

### Packaging (`pyproject.toml`)

New optional dependency extra:

```toml
[project.optional-dependencies]
secrets-ansible-vault = ["ansible-vault>=4.0.0"]
```

## Health Check

- Verifies that a password is available (already resolved at init)
- Verifies that the `ansible_vault` package is importable
- Does NOT check individual file accessibility (consistent with `FileProvider`)

## Files to Create/Modify

### New files

- `src/hyperi_pylib/secrets/providers/ansible_vault.py` — provider implementation
- `tests/unit/test_secrets_ansible_vault_provider.py` — unit tests

### Modified files

- `src/hyperi_pylib/secrets/types.py` — add `AnsibleVaultConfig`, extend `ProviderType`
- `src/hyperi_pylib/secrets/providers/__init__.py` — add graceful import
- `src/hyperi_pylib/secrets/manager.py` — add `from_config` block and `_parse_ansible_vault_config`
- `pyproject.toml` — add `secrets-ansible-vault` optional extra

## Testing Strategy

### Unit Tests — Happy Path

| Test | Description |
|---|---|
| `test_decrypt_single_value_file` | Decrypt a single-value vault file, returns raw bytes |
| `test_decrypt_yaml_file_extract_key` | Decrypt YAML vault file, extract specific key |
| `test_decrypt_yaml_file_no_key` | Decrypt YAML vault file without key, returns full YAML bytes |
| `test_password_from_env_var` | Password resolved from `ANSIBLE_VAULT_PASSWORD` |
| `test_password_from_fallback_env_var` | Password resolved from `ANSIBLE_VAULT_PASS` |
| `test_password_from_env_password_file` | Password file path from `ANSIBLE_VAULT_PASSWORD_FILE` |
| `test_password_from_config_file` | Password from `password_file` config |
| `test_password_priority_order` | Env var takes precedence over password file |
| `test_health_check_passes` | Health check returns `True` when password configured |
| `test_version_tracking` | Version string is `mtime:size` format |
| `test_async_delegates_to_sync` | Async get returns same result as sync get |

### Unit Tests — Expected Failures

| Test | Description |
|---|---|
| `test_no_password_source_raises` | No password configured — `ProviderError` at init |
| `test_file_not_found_raises` | Vault file missing — `SecretNotFoundError` |
| `test_wrong_password_raises` | Wrong password — `ProviderError` |
| `test_key_from_non_yaml_raises` | Key requested but content is not YAML — `ProviderError` |
| `test_missing_key_in_yaml_raises` | Key not found in YAML — `SecretNotFoundError` |
| `test_password_file_missing_raises` | Password file doesn't exist — `ProviderError` at init |
| `test_password_file_empty_raises` | Password file is empty — `ProviderError` at init |
| `test_corrupted_vault_file_raises` | Bad vault file content — `ProviderError` |
| `test_permission_denied_raises` | Unreadable vault file — `ProviderError` |

### Test Fixtures

Vault-encrypted files created at test time using `ansible_vault.Vault(password).dump()` in `tmp_path` fixtures. No checked-in encrypted blobs — tests are fully self-contained.

### Integration Tests

Add Ansible Vault section to `tests/integration/test_secrets_cloud_providers.py`:
- Real encrypt/decrypt round-trip
- Skip if `ansible-vault` package not installed

## Single Password Only

This provider supports a single vault password. Ansible's multi-password / vault-id feature is out of scope — single password covers the target SME use case.
