# Secrets Abstraction Extensions — Design Spec

**Date:** 2026-04-10
**Status:** Draft
**Author:** Derek (with AI assist)
**Depends on:** Ansible Vault provider (v2.26.0, shipped)

---

## Summary

Extend the `SecretProvider` ABC and `SecretsManager` with list, CRUD, metadata, versioning, and batch operations. Every abstraction is validated against the real SDK/API of all 6 providers (OpenBao, AWS, GCP, Azure, File, Ansible Vault) to ensure it maps cleanly to native capabilities.

## Motivation

The current secrets module only abstracts `get` and `health_check`. Every provider supports list, create, update, delete, and metadata retrieval — but callers must drop down to provider-specific SDKs to use them. This creates provider lock-in and inconsistent error handling across services.

Common use cases not currently served:

- **Service bootstrap:** "Load all secrets under `myapp/`" — requires list + batch get
- **Control plane:** "Create/rotate/delete secrets programmatically" — requires CRUD
- **Operational visibility:** "What secrets exist, when were they last updated?" — requires metadata
- **Rollback:** "Get the previous version of this secret" — requires versioned access
- **Audit:** "What happened when this failed?" — requires structured permission errors

## Scope

### In scope

- `SecretFilter` dataclass (prefix, tags, pattern)
- `SecretMetadata` dataclass (normalised metadata across providers)
- Tier 1 ABC methods: `list`, `get_metadata`, `create`, `update`, `delete` (all providers)
- Tier 2 `VersionedProvider` mixin: `get_version`, `list_versions` (OpenBao, AWS, GCP, Azure)
- `SecretsManager.batch_get` (native where available, parallel fallback)
- `SecretsManager` delegation methods for all new operations
- New exception types for write operations and permission errors
- Comprehensive tests including permission-denied scenarios

### Out of scope

- Transit encryption / encryption-as-a-service (separate feature, Vault-specific)
- PKI / certificate generation (separate feature)
- Secret templating / composition (separate feature)
- Cross-provider sync / migration (separate feature)
- Log redaction (separate feature, applies to logging module)
- Audit event emission (separate feature, builds on this work)

---

## New Types

### `SecretMetadata`

Normalised metadata across all providers. Fields are `None` when a provider doesn't support them.

```python
@dataclass
class SecretMetadata:
    name: str
    """Secret name or path."""

    created_at: datetime | None = None
    """When the secret was created."""

    updated_at: datetime | None = None
    """When the secret was last modified."""

    expires_at: datetime | None = None
    """When the secret expires (Azure, AWS rotation)."""

    version: str | None = None
    """Current version identifier."""

    version_count: int | None = None
    """Number of versions (versioned providers only)."""

    tags: dict[str, str] | None = None
    """Provider tags/labels (cloud providers, OpenBao custom metadata)."""

    source: str = "unknown"
    """Provider name."""
```

**Provider field mapping:**

| Field | OpenBao | AWS | GCP | Azure | File | Ansible Vault |
|---|---|---|---|---|---|---|
| `created_at` | metadata.created_time | DescribeSecret.CreatedDate | secret.create_time | properties.created_on | stat.st_ctime | stat.st_ctime |
| `updated_at` | metadata.updated_time | DescribeSecret.LastChangedDate | — | properties.updated_on | stat.st_mtime | stat.st_mtime |
| `expires_at` | — | DescribeSecret.NextRotationDate | expiration (if set) | properties.expires_on | — | — |
| `version` | metadata.current_version | VersionId | version name | properties.version | mtime:size | mtime:size |
| `version_count` | metadata.versions count | — (need list call) | — (need list call) | — (need list call) | None | None |
| `tags` | metadata.custom_metadata | DescribeSecret.Tags | secret.labels | properties.tags | None | None |

### `SecretFilter`

```python
@dataclass
class SecretFilter:
    prefix: str | None = None
    """Path prefix — server-side filter where supported. Primary efficient filter."""

    tags: dict[str, str] | None = None
    """Tag/label filter. Server-side on AWS/GCP/Azure/OpenBao. Ignored on file-based."""

    pattern: str | None = None
    """Glob pattern — client-side post-filter on list results. Use prefix for efficiency."""
```

**Provider filter support:**

| Filter | OpenBao | AWS | GCP | Azure | File | Ansible Vault |
|---|---|---|---|---|---|---|
| `prefix` | Path-based (natural) | `name` filter | `filter` param | Client-side | Directory path | Directory path |
| `tags` | Custom metadata match | `tag-key`/`tag-value` filter | Labels filter | Client-side on properties | Ignored | Ignored |
| `pattern` | Client-side `fnmatch` | Client-side `fnmatch` | Client-side `fnmatch` | Client-side `fnmatch` | `Path.glob()` native | `Path.glob()` native |

`prefix` is the primary efficient server-side filter. `pattern` is a convenience post-filter — documented as potentially expensive on large secret sets.

---

## Exception Hierarchy Extension

Current:

```
SecretsError
├── SecretNotFoundError
├── ProviderError
│   └── AuthenticationError
├── ProviderNotConfiguredError
├── ProviderNotAvailableError
└── CacheError
```

New additions:

```python
class SecretAlreadyExistsError(SecretsError):
    """Secret already exists at the specified path (create conflict)."""

    def __init__(self, name: str, provider: str) -> None:
        self.name = name
        self.provider = provider
        super().__init__(f"secret '{name}' already exists in provider '{provider}'")


class SecretPermissionError(ProviderError):
    """Caller lacks permission for the requested operation.

    Common in read-only service accounts attempting write operations.
    Message includes the operation attempted and hints at what role/policy is needed.
    """

    def __init__(self, provider: str, operation: str, path: str, hint: str | None = None) -> None:
        self.operation = operation
        self.path = path
        self.hint = hint
        message = f"permission denied: cannot {operation} '{path}'"
        if hint:
            message += f" — {hint}"
        super().__init__(provider, message)


class SecretVersionNotFoundError(SecretNotFoundError):
    """Requested version does not exist."""

    def __init__(self, name: str, version: str, provider: str) -> None:
        self.version = version
        super().__init__(f"{name}@{version}", provider)


class VersioningNotSupportedError(ProviderError):
    """Provider does not support versioned access."""

    def __init__(self, provider: str) -> None:
        super().__init__(provider, "versioned access is not supported by this provider")
```

**Provider-specific permission hints:**

| Provider | Source exception | Hint |
|---|---|---|
| OpenBao | HTTP 403 | `"check Vault policy for '{operation}' capability on this path"` |
| AWS | `AccessDeniedException` | `"check IAM policy for secretsmanager:{Operation} permission"` |
| GCP | `PermissionDenied` (gRPC) | `"check IAM role for secretmanager.secrets.{operation}"` |
| Azure | `HttpResponseError` 403 | `"check Key Vault access policy or RBAC role assignment"` |
| File | `PermissionError` (OS) | `"check filesystem permissions on '{path}'"` |
| Ansible Vault | `PermissionError` (OS) | `"check filesystem permissions on '{path}'"` |

Example error message for a read-only service account:

```
SecretPermissionError: provider 'aws' error: permission denied: cannot create 'myapp/db-password'
  — check IAM policy for secretsmanager:CreateSecret permission
```

---

## ABC Extension — Tier 1 (Universal)

All 6 providers must implement these. Added to `SecretProvider`:

```python
class SecretProvider(ABC):
    # ... existing: name, get_async, get_sync, health_check_async, health_check_sync, close ...

    # --- List ---
    @abstractmethod
    async def list_async(self, filter: SecretFilter | None = None) -> list[str]:
        """List secret names/paths matching filter.

        Args:
            filter: Optional filter (prefix, tags, pattern).

        Returns:
            List of secret names/paths.
        """
        ...

    @abstractmethod
    def list_sync(self, filter: SecretFilter | None = None) -> list[str]:
        """List secret names/paths matching filter (sync)."""
        ...

    # --- Metadata ---
    @abstractmethod
    async def get_metadata_async(self, path: str) -> SecretMetadata:
        """Get secret metadata without fetching the value.

        Raises:
            SecretNotFoundError: Secret does not exist.
            ProviderError: Provider communication failed.
        """
        ...

    @abstractmethod
    def get_metadata_sync(self, path: str) -> SecretMetadata:
        """Get secret metadata without fetching the value (sync)."""
        ...

    # --- Create ---
    @abstractmethod
    async def create_async(self, path: str, value: bytes, tags: dict[str, str] | None = None) -> SecretMetadata:
        """Create a new secret.

        Args:
            path: Secret path/name.
            value: Secret value as bytes.
            tags: Optional tags/labels. Ignored by file-based providers.

        Returns:
            SecretMetadata of the created secret.

        Raises:
            SecretAlreadyExistsError: Secret already exists.
            SecretPermissionError: Caller lacks write permission.
            ProviderError: Write failed.
        """
        ...

    @abstractmethod
    def create_sync(self, path: str, value: bytes, tags: dict[str, str] | None = None) -> SecretMetadata:
        """Create a new secret (sync)."""
        ...

    # --- Update ---
    @abstractmethod
    async def update_async(self, path: str, value: bytes) -> SecretMetadata:
        """Update an existing secret's value.

        Returns:
            SecretMetadata of the updated secret (new version).

        Raises:
            SecretNotFoundError: Secret does not exist.
            SecretPermissionError: Caller lacks write permission.
            ProviderError: Write failed.
        """
        ...

    @abstractmethod
    def update_sync(self, path: str, value: bytes) -> SecretMetadata:
        """Update an existing secret's value (sync)."""
        ...

    # --- Delete ---
    @abstractmethod
    async def delete_async(self, path: str) -> None:
        """Delete a secret.

        Raises:
            SecretNotFoundError: Secret does not exist.
            SecretPermissionError: Caller lacks write permission.
            ProviderError: Delete failed.
        """
        ...

    @abstractmethod
    def delete_sync(self, path: str) -> None:
        """Delete a secret (sync)."""
        ...
```

**Design decisions:**

- `create` / `update` return `SecretMetadata` — confirms version created, no need to echo back the value
- `create` accepts optional `tags` — supported by cloud providers and OpenBao, silently ignored by file-based
- `update` does not accept `tags` — tag management is a metadata operation, not a value update
- `delete` returns `None` — fire and forget; Azure's async LRO poller handled internally
- `list` returns `list[str]` — lightweight; use `get_metadata` for details

---

## Tier 2 — `VersionedProvider` Mixin

Separate class for providers that support versioned secret access. Providers subclass this instead of `SecretProvider` directly.

```python
class VersionedProvider(SecretProvider):
    """Mixin for providers that support versioned secret access.

    Providers: OpenBao, AWS, GCP, Azure.
    Not implemented by: File, AnsibleVault.

    Use isinstance(provider, VersionedProvider) to check capability.
    """

    @abstractmethod
    async def get_version_async(self, path: str, version: str, key: str | None = None) -> SecretValue:
        """Fetch a specific version of a secret.

        Args:
            path: Secret path.
            version: Version identifier (provider-specific format).
            key: Optional key to extract from structured secret.

        Raises:
            SecretVersionNotFoundError: Version does not exist.
            SecretNotFoundError: Secret does not exist.
            ProviderError: Provider communication failed.
        """
        ...

    @abstractmethod
    def get_version_sync(self, path: str, version: str, key: str | None = None) -> SecretValue:
        """Fetch a specific version (sync)."""
        ...

    @abstractmethod
    async def list_versions_async(self, path: str) -> list[SecretMetadata]:
        """List all versions of a secret, newest first.

        Returns:
            List of SecretMetadata, one per version.

        Raises:
            SecretNotFoundError: Secret does not exist.
            ProviderError: Provider communication failed.
        """
        ...

    @abstractmethod
    def list_versions_sync(self, path: str) -> list[SecretMetadata]:
        """List all versions (sync)."""
        ...
```

**Provider inheritance changes:**

```python
# Before
class OpenBaoProvider(SecretProvider): ...
class AWSProvider(SecretProvider): ...
class GCPProvider(SecretProvider): ...
class AzureProvider(SecretProvider): ...
class FileProvider(SecretProvider): ...
class AnsibleVaultProvider(SecretProvider): ...

# After
class OpenBaoProvider(VersionedProvider): ...
class AWSProvider(VersionedProvider): ...
class GCPProvider(VersionedProvider): ...
class AzureProvider(VersionedProvider): ...
class FileProvider(SecretProvider): ...            # unchanged
class AnsibleVaultProvider(SecretProvider): ...    # unchanged
```

---

## `SecretsManager` Extensions

### Delegation Methods

All new provider operations are exposed through the manager with the same `name_or_path` / `provider` override pattern as existing `get()`:

```python
class SecretsManager:
    # ... existing ...

    # --- List ---
    async def list(self, filter: SecretFilter | None = None, provider: str | None = None) -> list[str]:
        """List secrets from a provider."""

    def list_sync(self, filter: SecretFilter | None = None, provider: str | None = None) -> list[str]:
        """List secrets (sync)."""

    # --- Batch get ---
    async def batch_get(self, names: list[str]) -> dict[str, SecretValue]:
        """Fetch multiple secrets. Uses native batch where available, parallel fallback."""

    def batch_get_sync(self, names: list[str]) -> dict[str, SecretValue]:
        """Fetch multiple secrets (sync)."""

    # --- Metadata ---
    async def get_metadata(self, name_or_path: str, provider: str | None = None) -> SecretMetadata:
        """Get secret metadata without fetching value."""

    def get_metadata_sync(self, name_or_path: str, provider: str | None = None) -> SecretMetadata:
        """Get secret metadata (sync)."""

    # --- CRUD ---
    async def create(self, path: str, value: bytes, provider: str | None = None,
                     tags: dict[str, str] | None = None) -> SecretMetadata:
        """Create a secret via the specified provider."""

    def create_sync(self, path: str, value: bytes, provider: str | None = None,
                    tags: dict[str, str] | None = None) -> SecretMetadata:
        """Create a secret (sync)."""

    async def update(self, path: str, value: bytes, provider: str | None = None) -> SecretMetadata:
        """Update a secret's value."""

    def update_sync(self, path: str, value: bytes, provider: str | None = None) -> SecretMetadata:
        """Update a secret (sync)."""

    async def delete(self, path: str, provider: str | None = None) -> None:
        """Delete a secret."""

    def delete_sync(self, path: str, provider: str | None = None) -> None:
        """Delete a secret (sync)."""

    # --- Versioned access (with capability check) ---
    async def get_version(self, name_or_path: str, version: str,
                          provider: str | None = None) -> SecretValue:
        """Get a specific version. Raises VersioningNotSupportedError if provider can't."""

    def get_version_sync(self, name_or_path: str, version: str,
                         provider: str | None = None) -> SecretValue:
        """Get a specific version (sync)."""

    async def list_versions(self, name_or_path: str,
                            provider: str | None = None) -> list[SecretMetadata]:
        """List versions. Raises VersioningNotSupportedError if provider can't."""

    def list_versions_sync(self, name_or_path: str,
                           provider: str | None = None) -> list[SecretMetadata]:
        """List versions (sync)."""
```

### `batch_get` Implementation Strategy

```python
async def batch_get(self, names: list[str]) -> dict[str, SecretValue]:
    # Group names by resolved provider
    by_provider: dict[str, list[str]] = {}
    for name in names:
        provider_name = self._resolve_provider_name(name)
        by_provider.setdefault(provider_name, []).append(name)

    results: dict[str, SecretValue] = {}

    async def fetch_group(provider_name: str, group_names: list[str]) -> dict[str, SecretValue]:
        # AWS has native batch — use it when available
        provider = self._providers[provider_name]
        if hasattr(provider, "batch_get_async"):
            return await provider.batch_get_async(group_names)
        # All others: parallel individual gets
        tasks = {name: self.get(name) for name in group_names}
        fetched = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return {
            name: value
            for name, value in zip(tasks.keys(), fetched)
            if not isinstance(value, Exception)
        }

    groups = await asyncio.gather(
        *[fetch_group(pn, gn) for pn, gn in by_provider.items()]
    )
    for group_result in groups:
        results.update(group_result)

    return results
```

### Versioned Access Capability Check

```python
async def get_version(self, name_or_path: str, version: str, provider: str | None = None) -> SecretValue:
    p = self._resolve_provider(name_or_path, provider)
    if not isinstance(p, VersionedProvider):
        raise VersioningNotSupportedError(p.name)
    return await p.get_version_async(name_or_path, version)
```

---

## Validated Provider API Mapping

Every abstraction maps to a real, confirmed SDK method:

### List

| Provider | SDK Method | Filter support |
|---|---|---|
| OpenBao | `LIST /v1/secret/metadata/{prefix}` | Path prefix native |
| AWS | `boto3: list_secrets(Filters=[...])` | Name prefix, tags native |
| GCP | `list_secrets(request={"parent": ..., "filter": ...})` | Filter string native |
| Azure | `list_properties_of_secrets()` | Client-side filter |
| File | `Path.iterdir()` / `Path.glob()` | Glob native |
| Ansible Vault | `Path.iterdir()` / `Path.glob()` | Glob native |

### Get Metadata

| Provider | SDK Method |
|---|---|
| OpenBao | `GET /v1/secret/metadata/{path}` |
| AWS | `boto3: describe_secret(SecretId=...)` |
| GCP | `get_secret(request={"name": ...})` |
| Azure | `get_secret(name)` → `.properties` |
| File | `Path.stat()` |
| Ansible Vault | `Path.stat()` |

### Create

| Provider | SDK Method |
|---|---|
| OpenBao | `POST /v1/secret/data/{path}` (with `cas=0` for create-only) |
| AWS | `boto3: create_secret(Name=..., SecretBinary=...)` |
| GCP | `create_secret()` + `add_secret_version()` |
| Azure | `set_secret(name, value)` |
| File | `Path.write_bytes()` (fail if exists) |
| Ansible Vault | `Vault.dump_raw()` + `Path.write_text()` (fail if exists) |

### Update

| Provider | SDK Method |
|---|---|
| OpenBao | `POST /v1/secret/data/{path}` |
| AWS | `boto3: put_secret_value(SecretId=..., SecretBinary=...)` |
| GCP | `add_secret_version(request={"parent": ..., "payload": ...})` |
| Azure | `set_secret(name, value)` |
| File | `Path.write_bytes()` (fail if not exists) |
| Ansible Vault | `Vault.dump_raw()` + `Path.write_text()` (fail if not exists) |

### Delete

| Provider | SDK Method |
|---|---|
| OpenBao | `DELETE /v1/secret/metadata/{path}` |
| AWS | `boto3: delete_secret(SecretId=...)` |
| GCP | `delete_secret(request={"name": ...})` |
| Azure | `begin_delete_secret(name)` |
| File | `Path.unlink()` |
| Ansible Vault | `Path.unlink()` |

### Get Version (Tier 2)

| Provider | SDK Method |
|---|---|
| OpenBao | `GET /v1/secret/data/{path}?version=N` |
| AWS | `boto3: get_secret_value(SecretId=..., VersionId=...)` |
| GCP | `access_secret_version(name="projects/.../versions/N")` |
| Azure | `get_secret(name, version=VERSION_ID)` |

### List Versions (Tier 2)

| Provider | SDK Method |
|---|---|
| OpenBao | `GET /v1/secret/metadata/{path}` → versions dict |
| AWS | `boto3: list_secret_version_ids(SecretId=...)` |
| GCP | `list_secret_versions(request={"parent": ...})` |
| Azure | `list_properties_of_secret_versions(name)` |

---

## Files to Create/Modify

### Modified files

| File | Change |
|---|---|
| `src/hyperi_pylib/secrets/providers/base.py` | Add Tier 1 abstract methods, add `VersionedProvider` class |
| `src/hyperi_pylib/secrets/types.py` | Add `SecretMetadata`, `SecretFilter`, update `__all__` |
| `src/hyperi_pylib/secrets/exceptions.py` | Add `SecretAlreadyExistsError`, `SecretPermissionError`, `SecretVersionNotFoundError`, `VersioningNotSupportedError` |
| `src/hyperi_pylib/secrets/manager.py` | Add delegation methods: list, batch_get, get_metadata, create, update, delete, get_version, list_versions |
| `src/hyperi_pylib/secrets/providers/openbao.py` | Implement Tier 1 + Tier 2 (extend `VersionedProvider`) |
| `src/hyperi_pylib/secrets/providers/aws.py` | Implement Tier 1 + Tier 2 (extend `VersionedProvider`), add `batch_get_async` |
| `src/hyperi_pylib/secrets/providers/gcp.py` | Implement Tier 1 + Tier 2 (extend `VersionedProvider`) |
| `src/hyperi_pylib/secrets/providers/azure.py` | Implement Tier 1 + Tier 2 (extend `VersionedProvider`) |
| `src/hyperi_pylib/secrets/providers/file.py` | Implement Tier 1 (stays `SecretProvider`) |
| `src/hyperi_pylib/secrets/providers/ansible_vault.py` | Implement Tier 1 (stays `SecretProvider`) |
| `src/hyperi_pylib/secrets/providers/__init__.py` | Export `VersionedProvider` |
| `src/hyperi_pylib/secrets/__init__.py` | Export new types |

### Test files to create/modify

| File | What |
|---|---|
| `tests/unit/test_secrets_types.py` | Tests for `SecretMetadata`, `SecretFilter` |
| `tests/unit/test_secrets_exceptions.py` | Tests for new exception types |
| `tests/unit/test_secrets_file_provider.py` | Add list, metadata, create, update, delete tests |
| `tests/unit/test_secrets_ansible_vault_provider.py` | Add list, metadata, create, update, delete tests |
| `tests/unit/test_secrets_manager.py` | Add batch_get, list, metadata, CRUD delegation, version capability check tests |
| `tests/integration/test_secrets_cloud_providers.py` | Add list, metadata, CRUD, versioning tests per provider |

---

## Testing Strategy

### Unit Tests — Per Provider (Happy Path)

| Test | Description |
|---|---|
| `test_list_all` | List with no filter returns all secrets |
| `test_list_prefix` | List with prefix filter returns subset |
| `test_list_pattern` | List with glob pattern filters correctly |
| `test_list_tags` | List with tag filter (cloud providers) |
| `test_list_empty` | List returns empty when no matches |
| `test_get_metadata` | Returns populated SecretMetadata |
| `test_get_metadata_tags` | Tags populated on cloud providers |
| `test_create_new` | Creates secret, returns metadata |
| `test_create_with_tags` | Tags applied on cloud providers |
| `test_update_existing` | Updates value, returns new metadata |
| `test_delete_existing` | Deletes successfully |
| `test_get_version` | Fetch specific version (versioned providers) |
| `test_list_versions` | List versions newest-first (versioned providers) |

### Unit Tests — Expected Failures

| Test | Description |
|---|---|
| `test_create_already_exists` | Create on existing path → `SecretAlreadyExistsError` |
| `test_create_permission_denied` | Read-only creds + create → `SecretPermissionError` with operation="create" and hint |
| `test_update_permission_denied` | Read-only creds + update → `SecretPermissionError` with operation="update" and hint |
| `test_delete_permission_denied` | Read-only creds + delete → `SecretPermissionError` with operation="delete" and hint |
| `test_delete_not_found` | Delete nonexistent → `SecretNotFoundError` |
| `test_update_not_found` | Update nonexistent → `SecretNotFoundError` |
| `test_get_metadata_not_found` | Metadata for nonexistent → `SecretNotFoundError` |
| `test_get_version_not_found` | Valid secret, bad version → `SecretVersionNotFoundError` |
| `test_get_version_not_supported` | File provider + version request → `VersioningNotSupportedError` |
| `test_list_versions_not_supported` | Ansible Vault + list versions → `VersioningNotSupportedError` |
| `test_permission_error_has_hint` | Verify hint is populated and provider-specific |
| `test_permission_error_includes_operation` | Verify `exc.operation` is set for programmatic handling |

### Unit Tests — SecretsManager

| Test | Description |
|---|---|
| `test_batch_get_multiple` | Fetch 5 secrets, all returned |
| `test_batch_get_partial_failure` | 3 succeed, 2 fail — returns the 3 |
| `test_batch_get_groups_by_provider` | Secrets from different providers fetched in parallel |
| `test_list_delegates_to_provider` | Manager.list passes filter to correct provider |
| `test_create_delegates_to_provider` | Manager.create calls provider.create_sync |
| `test_get_version_capability_check` | File provider → `VersioningNotSupportedError` |
| `test_get_version_versioned_provider` | OpenBao provider → delegates to `get_version_async` |
