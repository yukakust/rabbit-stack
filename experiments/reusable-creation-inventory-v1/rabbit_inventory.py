#!/usr/bin/env python3
"""Target-independent reusable Rabbit component inventory and signed sharing package."""

from __future__ import annotations

import hashlib
import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


MAGIC = b"RBINV1\0\0"
VERSION = 1
PREFIX = struct.Struct("<8sII32s32s")
SIGNATURE_SIZE = 64
HEADER_SIZE = PREFIX.size + SIGNATURE_SIZE
MAX_PACKAGE_BYTES = 4 * 1024 * 1024
KINDS = {"asset", "capability", "anima", "creation", "policy"}
RESOURCE_FIELDS = {
    "memory_bytes",
    "persistent_bytes",
    "objects",
    "pixels_per_frame",
    "ticks_per_second",
}
COMPONENT_FIELDS = {
    "schema_version",
    "component_id",
    "version",
    "kind",
    "name",
    "summary",
    "creator",
    "license",
    "interfaces",
    "dependencies",
    "provides",
    "authorities",
    "resources",
    "implementation",
}
PORT_FIELDS = {"name", "type"}
DEPENDENCY_FIELDS = {"component_id", "version"}
ENDPOINT_FIELDS = {"component_id", "port"}
BINDING_FIELDS = {"from", "to"}
MEMBER_FIELDS = {"component_id", "version"}
CREATION_FIELDS = {"creation_id", "version", "name", "summary", "creator", "license"}
MERGE_FIELDS = {"schema_version", "creation", "members", "bindings", "grants", "budgets"}
CATALOG_FIELDS = {"schema_version", "catalog_id", "components"}
ID_RE = re.compile(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*\Z")
VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
TYPE_RE = re.compile(r"[a-z][a-z0-9]*(?:\.[a-z0-9-]+)+\Z")
SPDX_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+-]{0,63}\Z")
ALLOWED_IMPLEMENTATIONS = {
    "rabbit.sprite.v1",
    "rabbit.capability-contract.v1",
    "rabbit.state-machine.v1",
    "rabbit.policy.v1",
}
FORBIDDEN_TARGET_WORDS = (b"x86", b"arm64", b"riscv", b"uefi", b"qemu", b"dell", b"framebuffer", b"mmio")


class InventoryError(ValueError):
    pass


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InventoryError(f"duplicate JSON field: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    except (OSError, json.JSONDecodeError) as error:
        raise InventoryError(f"could not load {path}: {error}") from error
    if not isinstance(value, dict):
        raise InventoryError(f"{path.name} must contain one JSON object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def sha256_bytes(value: bytes) -> bytes:
    return hashlib.sha256(value).digest()


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        missing = sorted(expected - set(value))
        unknown = sorted(set(value) - expected)
        raise InventoryError(f"{label} fields mismatch: missing={missing}, unknown={unknown}")


def require_text(value: Any, label: str, pattern: re.Pattern[str] | None = None, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum or any(ord(char) < 32 for char in value):
        raise InventoryError(f"{label} must be nonempty printable text up to {maximum} characters")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise InventoryError(f"{label} has an invalid format")
    return value


def validate_creator(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise InventoryError(f"{label} must be an object")
    require_fields(value, {"id", "display_name"}, label)
    require_text(value["id"], f"{label}.id", ID_RE, 128)
    require_text(value["display_name"], f"{label}.display_name", maximum=128)


def validate_license(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise InventoryError(f"{label} must be an object")
    require_fields(value, {"spdx"}, label)
    require_text(value["spdx"], f"{label}.spdx", SPDX_RE, 64)


def validate_string_list(value: Any, label: str, pattern: re.Pattern[str] = TYPE_RE) -> list[str]:
    if not isinstance(value, list):
        raise InventoryError(f"{label} must be a list")
    result = [require_text(item, f"{label} item", pattern, 128) for item in value]
    if result != sorted(set(result)):
        raise InventoryError(f"{label} must be sorted and contain no duplicates")
    return result


def validate_ports(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, list):
        raise InventoryError(f"{label} must be a list")
    ports: dict[str, str] = {}
    for index, port in enumerate(value):
        if not isinstance(port, dict):
            raise InventoryError(f"{label}[{index}] must be an object")
        require_fields(port, PORT_FIELDS, f"{label}[{index}]")
        name = require_text(port["name"], f"{label}[{index}].name", ID_RE, 64)
        port_type = require_text(port["type"], f"{label}[{index}].type", TYPE_RE, 128)
        if name in ports:
            raise InventoryError(f"{label} contains duplicate port {name!r}")
        ports[name] = port_type
    return ports


def validate_resources(value: Any, label: str) -> dict[str, int]:
    if not isinstance(value, dict):
        raise InventoryError(f"{label} must be an object")
    require_fields(value, RESOURCE_FIELDS, label)
    result: dict[str, int] = {}
    limits = {
        "memory_bytes": 64 * 1024 * 1024,
        "persistent_bytes": 64 * 1024 * 1024,
        "objects": 4096,
        "pixels_per_frame": 16 * 1024 * 1024,
        "ticks_per_second": 1000,
    }
    for field in sorted(RESOURCE_FIELDS):
        number = value[field]
        if isinstance(number, bool) or not isinstance(number, int) or not 0 <= number <= limits[field]:
            raise InventoryError(f"{label}.{field} is outside the reviewed limit")
        result[field] = number
    return result


def validate_sprite(implementation: dict[str, Any], label: str) -> None:
    expected = {"format", "width", "height", "palette", "frames"}
    require_fields(implementation, expected, label)
    width = implementation["width"]
    height = implementation["height"]
    if isinstance(width, bool) or isinstance(height, bool) or not isinstance(width, int) or not isinstance(height, int) or not 1 <= width <= 64 or not 1 <= height <= 64:
        raise InventoryError(f"{label} sprite dimensions are outside 1..64")
    palette = implementation["palette"]
    if not isinstance(palette, dict) or not 1 <= len(palette) <= 16:
        raise InventoryError(f"{label}.palette must contain 1..16 colors")
    for symbol, color in palette.items():
        if not isinstance(symbol, str) or len(symbol) != 1 or not isinstance(color, str) or re.fullmatch(r"[0-9A-F]{6}|transparent", color) is None:
            raise InventoryError(f"{label}.palette has an invalid symbol or RGB value")
    frames = implementation["frames"]
    if not isinstance(frames, list) or not 1 <= len(frames) <= 32:
        raise InventoryError(f"{label}.frames must contain 1..32 frames")
    for frame_index, frame in enumerate(frames):
        if not isinstance(frame, list) or len(frame) != height:
            raise InventoryError(f"{label}.frames[{frame_index}] has the wrong height")
        for row in frame:
            if not isinstance(row, str) or len(row) != width or any(pixel not in palette for pixel in row):
                raise InventoryError(f"{label}.frames[{frame_index}] has an invalid row")


def validate_implementation(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise InventoryError(f"{label} must be an object")
    implementation_format = require_text(value.get("format"), f"{label}.format", TYPE_RE, 128)
    if implementation_format not in ALLOWED_IMPLEMENTATIONS:
        raise InventoryError(f"{label}.format is not reviewed")
    if implementation_format == "rabbit.sprite.v1":
        validate_sprite(value, label)
    else:
        encoded = canonical_bytes(value)
        if len(encoded) > 16 * 1024:
            raise InventoryError(f"{label} exceeds the reviewed declarative size")


def validate_component(component: Any, label: str = "component") -> dict[str, Any]:
    if not isinstance(component, dict):
        raise InventoryError(f"{label} must be an object")
    require_fields(component, COMPONENT_FIELDS, label)
    if component["schema_version"] != 1:
        raise InventoryError(f"{label}.schema_version is unsupported")
    require_text(component["component_id"], f"{label}.component_id", ID_RE, 128)
    require_text(component["version"], f"{label}.version", VERSION_RE, 32)
    if component["kind"] not in KINDS:
        raise InventoryError(f"{label}.kind is unsupported")
    require_text(component["name"], f"{label}.name", maximum=128)
    require_text(component["summary"], f"{label}.summary", maximum=512)
    validate_creator(component["creator"], f"{label}.creator")
    validate_license(component["license"], f"{label}.license")
    interfaces = component["interfaces"]
    if not isinstance(interfaces, dict):
        raise InventoryError(f"{label}.interfaces must be an object")
    require_fields(interfaces, {"inputs", "outputs"}, f"{label}.interfaces")
    input_ports = validate_ports(interfaces["inputs"], f"{label}.interfaces.inputs")
    output_ports = validate_ports(interfaces["outputs"], f"{label}.interfaces.outputs")
    if set(input_ports) & set(output_ports):
        raise InventoryError(f"{label} reuses a port name across inputs and outputs")
    dependencies = component["dependencies"]
    if not isinstance(dependencies, list):
        raise InventoryError(f"{label}.dependencies must be a list")
    dependency_keys: list[tuple[str, str]] = []
    for index, dependency in enumerate(dependencies):
        if not isinstance(dependency, dict):
            raise InventoryError(f"{label}.dependencies[{index}] must be an object")
        require_fields(dependency, DEPENDENCY_FIELDS, f"{label}.dependencies[{index}]")
        dependency_keys.append((
            require_text(dependency["component_id"], f"{label}.dependencies[{index}].component_id", ID_RE, 128),
            require_text(dependency["version"], f"{label}.dependencies[{index}].version", VERSION_RE, 32),
        ))
    if dependency_keys != sorted(set(dependency_keys)):
        raise InventoryError(f"{label}.dependencies must be sorted and unique")
    validate_string_list(component["provides"], f"{label}.provides")
    validate_string_list(component["authorities"], f"{label}.authorities")
    validate_resources(component["resources"], f"{label}.resources")
    validate_implementation(component["implementation"], f"{label}.implementation")
    if any(word in canonical_bytes(component).lower() for word in FORBIDDEN_TARGET_WORDS):
        raise InventoryError(f"{label} contains target-specific vocabulary")
    return component


def validate_catalog(catalog: Any) -> dict[tuple[str, str], dict[str, Any]]:
    if not isinstance(catalog, dict):
        raise InventoryError("catalog must be an object")
    require_fields(catalog, CATALOG_FIELDS, "catalog")
    if catalog["schema_version"] != 1:
        raise InventoryError("catalog schema version is unsupported")
    require_text(catalog["catalog_id"], "catalog.catalog_id", ID_RE, 128)
    if not isinstance(catalog["components"], list) or not catalog["components"]:
        raise InventoryError("catalog.components must be a nonempty list")
    index: dict[tuple[str, str], dict[str, Any]] = {}
    ordered_keys: list[tuple[str, str]] = []
    for position, component in enumerate(catalog["components"]):
        validated = validate_component(component, f"catalog.components[{position}]")
        key = (validated["component_id"], validated["version"])
        if key in index:
            raise InventoryError(f"catalog contains duplicate component {key}")
        index[key] = validated
        ordered_keys.append(key)
    if ordered_keys != sorted(ordered_keys):
        raise InventoryError("catalog components must be sorted by id and version")
    return index


def component_identity(component: dict[str, Any]) -> str:
    validate_component(component)
    return sha256_hex(canonical_bytes(component))


def endpoint(value: Any, label: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise InventoryError(f"{label} must be an object")
    require_fields(value, ENDPOINT_FIELDS, label)
    return (
        require_text(value["component_id"], f"{label}.component_id", ID_RE, 128),
        require_text(value["port"], f"{label}.port", ID_RE, 64),
    )


def resolve_merge(catalog: dict[str, Any], merge: dict[str, Any]) -> dict[str, Any]:
    index = validate_catalog(catalog)
    if not isinstance(merge, dict):
        raise InventoryError("merge must be an object")
    require_fields(merge, MERGE_FIELDS, "merge")
    if merge["schema_version"] != 1:
        raise InventoryError("merge schema version is unsupported")
    creation = merge["creation"]
    if not isinstance(creation, dict):
        raise InventoryError("merge.creation must be an object")
    require_fields(creation, CREATION_FIELDS, "merge.creation")
    require_text(creation["creation_id"], "merge.creation.creation_id", ID_RE, 128)
    require_text(creation["version"], "merge.creation.version", VERSION_RE, 32)
    require_text(creation["name"], "merge.creation.name", maximum=128)
    require_text(creation["summary"], "merge.creation.summary", maximum=512)
    validate_creator(creation["creator"], "merge.creation.creator")
    validate_license(creation["license"], "merge.creation.license")
    members = merge["members"]
    if not isinstance(members, list) or not members:
        raise InventoryError("merge.members must be a nonempty list")
    member_keys: list[tuple[str, str]] = []
    for position, member in enumerate(members):
        if not isinstance(member, dict):
            raise InventoryError(f"merge.members[{position}] must be an object")
        require_fields(member, MEMBER_FIELDS, f"merge.members[{position}]")
        key = (
            require_text(member["component_id"], f"merge.members[{position}].component_id", ID_RE, 128),
            require_text(member["version"], f"merge.members[{position}].version", VERSION_RE, 32),
        )
        if key not in index:
            raise InventoryError(f"merge refers to unavailable component {key}")
        member_keys.append(key)
    if member_keys != sorted(set(member_keys)):
        raise InventoryError("merge.members must be sorted and unique")
    member_set = set(member_keys)
    for key in member_keys:
        for dependency in index[key]["dependencies"]:
            dependency_key = (dependency["component_id"], dependency["version"])
            if dependency_key not in member_set:
                raise InventoryError(f"merge omits dependency {dependency_key} required by {key}")
    visiting: set[tuple[str, str]] = set()
    visited: set[tuple[str, str]] = set()

    def visit(key: tuple[str, str]) -> None:
        if key in visiting:
            raise InventoryError(f"component dependency cycle includes {key}")
        if key in visited:
            return
        visiting.add(key)
        for dependency in index[key]["dependencies"]:
            visit((dependency["component_id"], dependency["version"]))
        visiting.remove(key)
        visited.add(key)

    for key in member_keys:
        visit(key)
    by_id = {component_id: index[(component_id, version)] for component_id, version in member_keys}
    if len(by_id) != len(member_keys):
        raise InventoryError("one merge cannot contain two versions of the same component")
    bindings = merge["bindings"]
    if not isinstance(bindings, list):
        raise InventoryError("merge.bindings must be a list")
    bound_inputs: set[tuple[str, str]] = set()
    normalized_bindings: list[dict[str, dict[str, str]]] = []
    for position, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise InventoryError(f"merge.bindings[{position}] must be an object")
        require_fields(binding, BINDING_FIELDS, f"merge.bindings[{position}]")
        source = endpoint(binding["from"], f"merge.bindings[{position}].from")
        destination = endpoint(binding["to"], f"merge.bindings[{position}].to")
        if source[0] not in by_id or destination[0] not in by_id:
            raise InventoryError("binding refers to a component outside the merge")
        outputs = {port["name"]: port["type"] for port in by_id[source[0]]["interfaces"]["outputs"]}
        inputs = {port["name"]: port["type"] for port in by_id[destination[0]]["interfaces"]["inputs"]}
        if source[1] not in outputs or destination[1] not in inputs:
            raise InventoryError("binding refers to an unknown or wrongly directed port")
        if outputs[source[1]] != inputs[destination[1]]:
            raise InventoryError(f"binding type mismatch: {outputs[source[1]]!r} != {inputs[destination[1]]!r}")
        if destination in bound_inputs:
            raise InventoryError(f"input port {destination} is bound more than once")
        bound_inputs.add(destination)
        normalized_bindings.append(binding)
    if normalized_bindings != sorted(normalized_bindings, key=lambda item: canonical_bytes(item)):
        raise InventoryError("merge.bindings must be canonically sorted")
    grants = validate_string_list(merge["grants"], "merge.grants")
    required_authorities = sorted({authority for key in member_keys for authority in index[key]["authorities"]})
    if grants != required_authorities:
        raise InventoryError(f"merge grants must exactly match required authorities: {required_authorities}")
    budgets = validate_resources(merge["budgets"], "merge.budgets")
    totals = {field: sum(index[key]["resources"][field] for key in member_keys) for field in RESOURCE_FIELDS}
    for field in RESOURCE_FIELDS:
        if totals[field] > budgets[field]:
            raise InventoryError(f"merge exceeds budget {field}: {totals[field]} > {budgets[field]}")
    provenance = [
        {
            "component_id": key[0],
            "version": key[1],
            "sha256": component_identity(index[key]),
            "creator_id": index[key]["creator"]["id"],
            "license_spdx": index[key]["license"]["spdx"],
        }
        for key in member_keys
    ]
    lock = {
        "schema_version": 1,
        "creation": creation,
        "components": provenance,
        "bindings": bindings,
        "grants": grants,
        "resources": totals,
        "budgets": budgets,
    }
    if any(word in canonical_bytes(lock).lower() for word in FORBIDDEN_TARGET_WORDS):
        raise InventoryError("resolved creation contains target-specific vocabulary")
    lock["creation_sha256"] = sha256_hex(canonical_bytes(lock))
    return lock


@dataclass(frozen=True)
class InventoryPackage:
    payload: bytes
    signer_public_key: bytes
    signature: bytes

    @classmethod
    def sign(cls, payload_value: dict[str, Any], private_key: Ed25519PrivateKey) -> "InventoryPackage":
        payload = canonical_bytes(payload_value)
        if not 0 < len(payload) <= MAX_PACKAGE_BYTES:
            raise InventoryError("package payload size is outside the reviewed limit")
        public = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        prefix = PREFIX.pack(MAGIC, VERSION, len(payload), sha256_bytes(payload), public)
        return cls(payload, public, private_key.sign(prefix))

    def encode(self) -> bytes:
        if len(self.signer_public_key) != 32 or len(self.signature) != SIGNATURE_SIZE:
            raise InventoryError("package key or signature length is invalid")
        prefix = PREFIX.pack(MAGIC, VERSION, len(self.payload), sha256_bytes(self.payload), self.signer_public_key)
        return prefix + self.signature + self.payload

    @classmethod
    def decode_and_verify(cls, encoded: bytes, trusted_public_key: bytes) -> tuple["InventoryPackage", dict[str, Any]]:
        if len(encoded) < HEADER_SIZE or len(trusted_public_key) != 32:
            raise InventoryError("package is truncated or trusted key is invalid")
        magic, version, payload_size, payload_hash, public = PREFIX.unpack_from(encoded)
        if magic != MAGIC or version != VERSION or not 0 < payload_size <= MAX_PACKAGE_BYTES:
            raise InventoryError("package header is unsupported")
        if public != trusted_public_key or len(encoded) != HEADER_SIZE + payload_size:
            raise InventoryError("package signer is untrusted or package length is invalid")
        signature = encoded[PREFIX.size:HEADER_SIZE]
        payload = encoded[HEADER_SIZE:]
        if sha256_bytes(payload) != payload_hash:
            raise InventoryError("package payload hash mismatch")
        try:
            Ed25519PublicKey.from_public_bytes(public).verify(signature, encoded[:PREFIX.size])
        except InvalidSignature as error:
            raise InventoryError("package signature is invalid") from error
        try:
            payload_value = json.loads(payload.decode("ascii"), object_pairs_hook=unique_pairs)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise InventoryError(f"package payload is invalid JSON: {error}") from error
        if not isinstance(payload_value, dict) or set(payload_value) != {"schema_version", "catalog", "merge", "lock"}:
            raise InventoryError("package payload fields differ from Inventory v1")
        if payload_value["schema_version"] != 1:
            raise InventoryError("package payload schema is unsupported")
        expected_lock = resolve_merge(payload_value["catalog"], payload_value["merge"])
        if payload_value["lock"] != expected_lock:
            raise InventoryError("package lock does not match its components and Merge")
        return cls(payload, public, signature), payload_value


def build_share_package(catalog: dict[str, Any], merge: dict[str, Any], private_key: Ed25519PrivateKey) -> tuple[bytes, dict[str, Any]]:
    lock = resolve_merge(catalog, merge)
    selected = {(item["component_id"], item["version"]) for item in lock["components"]}
    subset_catalog = {
        "schema_version": 1,
        "catalog_id": catalog["catalog_id"],
        "components": [
            component for component in catalog["components"]
            if (component["component_id"], component["version"]) in selected
        ],
    }
    payload_value = {"schema_version": 1, "catalog": subset_catalog, "merge": merge, "lock": lock}
    package = InventoryPackage.sign(payload_value, private_key).encode()
    report = {
        "schema_version": 1,
        "status": "SIGNED-INVENTORY-PACKAGE-NOT-DEPLOYED",
        "creation_id": lock["creation"]["creation_id"],
        "creation_sha256": lock["creation_sha256"],
        "component_count": len(lock["components"]),
        "package_sha256": sha256_hex(package),
        "package_size_bytes": len(package),
        "signer_public_key_sha256": sha256_hex(package[PREFIX.size - 32:PREFIX.size]),
        "deployments_performed": [],
    }
    return package, report
