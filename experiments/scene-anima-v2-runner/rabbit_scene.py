#!/usr/bin/env python3
"""Deterministic target-independent Scene/Anima v2 reference runner."""

from __future__ import annotations

import hashlib
import html
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
INVENTORY_ROOT = ROOT.parent / "reusable-creation-inventory-v1"
CATALOG_PATH = INVENTORY_ROOT / "catalog.json"
MERGE_PATH = INVENTORY_ROOT / "examples" / "cat-plays-with-ball.merge.json"

CONTRACT_FIELDS = {
    "schema_version", "runner_id", "version", "accepted_creation_id",
    "accepted_creation_sha256", "tick_rate", "max_ticks", "logical_width",
    "logical_height", "pixel_scale", "max_entities", "required_grants",
    "output_format",
}
REQUIRED_COMPONENTS = {
    "rabbit.anima.bouncing-ball",
    "rabbit.anima.cat-chase-ball",
    "rabbit.asset.ball-pixel",
    "rabbit.asset.cat-pixel",
    "rabbit.capability.animation-frames",
    "rabbit.capability.clock-tick",
    "rabbit.capability.collision-circle",
    "rabbit.capability.physics-2d",
    "rabbit.capability.scene-graph",
    "rabbit.capability.sprite-renderer",
    "rabbit.policy.resource-budget",
    "rabbit.policy.signed-package",
    "rabbit.policy.transactional-rollback",
}


class SceneError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise SceneError(f"duplicate JSON field: {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (OSError, json.JSONDecodeError) as error:
        raise SceneError(f"could not load {path}: {error}") from error
    if not isinstance(value, dict):
        raise SceneError(f"{path.name} must contain one object")
    return value


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if set(contract) != CONTRACT_FIELDS:
        raise SceneError("runner contract fields differ from Scene/Anima v2")
    expected_text = {
        "runner_id": "rabbit.scene-anima.reference",
        "version": "2.0.0",
        "accepted_creation_id": "creation.cat-plays-with-ball",
        "output_format": "raster.rgb24.v1",
    }
    if contract["schema_version"] != 1 or any(contract[key] != value for key, value in expected_text.items()):
        raise SceneError("runner contract identity is unsupported")
    expected_numbers = {
        "tick_rate": 30,
        "max_ticks": 600,
        "logical_width": 160,
        "logical_height": 90,
        "pixel_scale": 3,
        "max_entities": 2,
    }
    if any(contract[key] != value for key, value in expected_numbers.items()):
        raise SceneError("runner bounds differ from the reviewed contract")
    if contract["required_grants"] != ["display.draw", "time.read"]:
        raise SceneError("runner authority grants differ from the reviewed contract")
    identity = contract["accepted_creation_sha256"]
    if not isinstance(identity, str) or len(identity) != 64 or any(char not in "0123456789abcdef" for char in identity):
        raise SceneError("runner creation identity is invalid")
    return contract


@dataclass
class Body:
    x: int
    y: int
    vx: int
    vy: int


@dataclass
class RuntimeState:
    tick: int
    cat: Body
    ball: Body
    cat_state: str
    cat_frame: int
    wait_ticks: int
    bat_count: int
    edge_bounce_count: int


def _component_by_id(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {component["component_id"]: component for component in catalog["components"]}


def load_reviewed_creation(
    contract_path: Path = ROOT / "runner.json",
    catalog_path: Path = CATALOG_PATH,
    merge_path: Path = MERGE_PATH,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    # Import the Inventory verifier itself: the runner does not duplicate or weaken it.
    import sys

    inventory_directory = str(INVENTORY_ROOT)
    if inventory_directory not in sys.path:
        sys.path.insert(0, inventory_directory)
    from rabbit_inventory import InventoryError, resolve_merge  # type: ignore

    contract = validate_contract(load_json(contract_path))
    catalog = load_json(catalog_path)
    merge = load_json(merge_path)
    try:
        lock = resolve_merge(catalog, merge)
    except InventoryError as error:
        raise SceneError(f"Inventory rejected the Creation: {error}") from error
    if lock["creation"]["creation_id"] != contract["accepted_creation_id"]:
        raise SceneError("Creation id is not accepted by this runner")
    if lock["creation_sha256"] != contract["accepted_creation_sha256"]:
        raise SceneError("Creation revision is not accepted by this runner")
    if lock["grants"] != contract["required_grants"]:
        raise SceneError("Creation grants do not match the runner")
    ids = {item["component_id"] for item in lock["components"]}
    if ids != REQUIRED_COMPONENTS:
        raise SceneError("Creation component set differs from the reviewed runner")
    components = _component_by_id(catalog)
    return contract, catalog, merge, components


def initial_state() -> RuntimeState:
    return RuntimeState(
        tick=0,
        cat=Body(x=12, y=58, vx=0, vy=0),
        ball=Body(x=116, y=34, vx=2, vy=1),
        cat_state="look",
        cat_frame=0,
        wait_ticks=10,
        bat_count=0,
        edge_bounce_count=0,
    )


def sign(number: int) -> int:
    return (number > 0) - (number < 0)


def advance(previous: RuntimeState, width: int = 160, height: int = 90) -> RuntimeState:
    """Advance one deterministic integer-only tick."""
    state = RuntimeState(
        tick=previous.tick + 1,
        cat=Body(**asdict(previous.cat)),
        ball=Body(**asdict(previous.ball)),
        cat_state=previous.cat_state,
        cat_frame=previous.cat_frame,
        wait_ticks=previous.wait_ticks,
        bat_count=previous.bat_count,
        edge_bounce_count=previous.edge_bounce_count,
    )

    # Bouncing-ball Anima and fixed-point physics.
    state.ball.x += state.ball.vx
    state.ball.y += state.ball.vy
    maximum_x = width - 8
    maximum_y = height - 8
    if state.ball.x < 0 or state.ball.x > maximum_x:
        state.ball.x = max(0, min(maximum_x, state.ball.x))
        state.ball.vx = -state.ball.vx
        state.edge_bounce_count += 1
    if state.ball.y < 0 or state.ball.y > maximum_y:
        state.ball.y = max(0, min(maximum_y, state.ball.y))
        state.ball.vy = -state.ball.vy
        state.edge_bounce_count += 1

    # Cat Anima: look -> chase -> pounce -> bat -> wait -> chase.
    dx = state.ball.x - state.cat.x
    dy = state.ball.y - state.cat.y
    distance_squared = dx * dx + dy * dy
    if state.wait_ticks > 0:
        state.wait_ticks -= 1
        state.cat_state = "look" if state.bat_count == 0 else "wait"
        speed = 0
    elif distance_squared > 28 * 28:
        state.cat_state = "chase"
        speed = 2
    elif distance_squared > 11 * 11:
        state.cat_state = "pounce"
        speed = 3
    else:
        state.cat_state = "bat"
        speed = 0
        away_x = sign(dx) or 1
        away_y = sign(dy) or -1
        state.ball.vx = away_x * 3
        state.ball.vy = away_y * 2
        state.ball.x = max(0, min(maximum_x, state.ball.x + away_x * 2))
        state.ball.y = max(0, min(maximum_y, state.ball.y + away_y * 2))
        state.wait_ticks = 12
        state.bat_count += 1

    if speed:
        state.cat.vx = sign(dx) * speed
        state.cat.vy = sign(dy) * speed
        state.cat.x = max(0, min(maximum_x, state.cat.x + state.cat.vx))
        state.cat.y = max(0, min(maximum_y, state.cat.y + state.cat.vy))
    else:
        state.cat.vx = 0
        state.cat.vy = 0
    state.cat_frame = (state.tick // 4) % 2 if state.cat_state in {"chase", "pounce"} else 0
    return state


def trace_state(state: RuntimeState) -> dict[str, Any]:
    return {
        "tick": state.tick,
        "cat": {"x": state.cat.x, "y": state.cat.y, "vx": state.cat.vx, "vy": state.cat.vy},
        "ball": {"x": state.ball.x, "y": state.ball.y, "vx": state.ball.vx, "vy": state.ball.vy},
        "cat_state": state.cat_state,
        "cat_frame": state.cat_frame,
        "bat_count": state.bat_count,
        "edge_bounce_count": state.edge_bounce_count,
    }


def run_ticks(ticks: int, contract: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(ticks, bool) or not isinstance(ticks, int) or not 1 <= ticks <= contract["max_ticks"]:
        raise SceneError(f"ticks must be between 1 and {contract['max_ticks']}")
    state = initial_state()
    trace = [trace_state(state)]
    for _ in range(ticks):
        state = advance(state, contract["logical_width"], contract["logical_height"])
        trace.append(trace_state(state))
    return trace


def decode_palette(sprite: dict[str, Any]) -> dict[str, tuple[int, int, int] | None]:
    result: dict[str, tuple[int, int, int] | None] = {}
    for symbol, value in sprite["palette"].items():
        result[symbol] = None if value == "transparent" else tuple(bytes.fromhex(value))  # type: ignore[assignment]
    return result


def render_rgb(
    state: dict[str, Any],
    contract: dict[str, Any],
    components: dict[str, dict[str, Any]],
) -> bytes:
    width = contract["logical_width"]
    height = contract["logical_height"]
    background = (18, 24, 38)
    pixels = bytearray(background * (width * height))

    def draw(component_id: str, frame_index: int, x: int, y: int) -> None:
        implementation = components[component_id]["implementation"]
        frames = implementation["frames"]
        if not 0 <= frame_index < len(frames):
            raise SceneError("sprite frame is outside the reviewed asset")
        palette = decode_palette(implementation)
        for sprite_y, row in enumerate(frames[frame_index]):
            for sprite_x, symbol in enumerate(row):
                color = palette[symbol]
                if color is None:
                    continue
                target_x = x + sprite_x
                target_y = y + sprite_y
                if not 0 <= target_x < width or not 0 <= target_y < height:
                    raise SceneError("renderer attempted an out-of-bounds pixel write")
                offset = (target_y * width + target_x) * 3
                pixels[offset:offset + 3] = bytes(color)

    draw("rabbit.asset.ball-pixel", 0, state["ball"]["x"], state["ball"]["y"])
    draw("rabbit.asset.cat-pixel", state["cat_frame"], state["cat"]["x"], state["cat"]["y"])
    return bytes(pixels)


def scale_rgb(rgb: bytes, width: int, height: int, scale: int) -> bytes:
    if len(rgb) != width * height * 3 or not 1 <= scale <= 8:
        raise SceneError("invalid raster or scale")
    output = bytearray()
    for y in range(height):
        row = rgb[y * width * 3:(y + 1) * width * 3]
        expanded = b"".join(row[x:x + 3] * scale for x in range(0, len(row), 3))
        for _ in range(scale):
            output.extend(expanded)
    return bytes(output)


def ppm_bytes(rgb: bytes, width: int, height: int) -> bytes:
    if len(rgb) != width * height * 3:
        raise SceneError("RGB payload length does not match its dimensions")
    return f"P6\n{width} {height}\n255\n".encode("ascii") + rgb


def preview_html(trace: list[dict[str, Any]], components: dict[str, dict[str, Any]], contract: dict[str, Any]) -> str:
    assets = {
        "cat": components["rabbit.asset.cat-pixel"]["implementation"],
        "ball": components["rabbit.asset.ball-pixel"]["implementation"],
    }
    payload = json.dumps({"trace": trace, "assets": assets, "contract": contract}, separators=(",", ":"))
    title = html.escape("Rabbit Scene/Anima v2 — Cat Plays With Ball")
    return f"""<!doctype html>
<meta charset=\"utf-8\"><title>{title}</title>
<style>html,body{{margin:0;background:#0b0f18;color:#eee;font:16px system-ui}}main{{display:grid;place-items:center;min-height:100vh}}canvas{{width:min(96vw,960px);image-rendering:pixelated;border:1px solid #39445f}}p{{max-width:960px}}</style>
<main><section><h1>{title}</h1><canvas id=\"scene\"></canvas><p id=\"status\"></p></section></main>
<script>const data={payload};const c=document.querySelector('#scene'),x=c.getContext('2d');
c.width=data.contract.logical_width;c.height=data.contract.logical_height;let i=0;
function sprite(asset,frame,px,py){{for(let y=0;y<asset.height;y++)for(let q=0;q<asset.width;q++){{let k=asset.frames[frame][y][q],v=asset.palette[k];if(v==='transparent')continue;x.fillStyle='#'+v;x.fillRect(px+q,py+y,1,1)}}}}
function draw(){{let s=data.trace[i];x.fillStyle='#121826';x.fillRect(0,0,c.width,c.height);sprite(data.assets.ball,0,s.ball.x,s.ball.y);sprite(data.assets.cat,s.cat_frame,s.cat.x,s.cat.y);document.querySelector('#status').textContent=`tick ${{s.tick}} · ${{s.cat_state}} · bats ${{s.bat_count}} · edge bounces ${{s.edge_bounce_count}}`;i=(i+1)%data.trace.length}}setInterval(draw,1000/data.contract.tick_rate);draw();</script>"""


def execute(ticks: int = 240) -> dict[str, Any]:
    contract, _catalog, _merge, components = load_reviewed_creation()
    trace = run_ticks(ticks, contract)
    final_rgb = render_rgb(trace[-1], contract, components)
    return {
        "contract": contract,
        "components": components,
        "trace": trace,
        "trace_sha256": sha256_hex(canonical_bytes(trace)),
        "final_rgb": final_rgb,
        "final_rgb_sha256": sha256_hex(final_rgb),
    }
