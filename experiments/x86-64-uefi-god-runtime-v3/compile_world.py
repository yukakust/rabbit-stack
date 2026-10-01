"""Strict data-only RUP3 compiler; legacy v2 worlds remain byte-identical."""
import json
import re
from pathlib import Path
from package import PackageError, build_package, v2, LEGACY


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PackageError("duplicate JSON field")
        result[key] = value
    return result


def bounded(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise PackageError("integer field is outside the reviewed budget")


def compile_world(path, counter, private):
    bounded(counter, 1, 0xffffffff)
    if path.stat().st_size > 2 * 1024 * 1024:
        raise PackageError("world JSON exceeds input budget")
    world = json.loads(path.read_text(), object_pairs_hook=unique_pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(PackageError("invalid number")))
    if type(world) is not dict or set(world) != {"schema_version", "world_id", "palette", "sprites", "objects", "programs"}:
        raise PackageError("world fields differ from contract")
    if type(world["schema_version"]) is not int or world["schema_version"] not in (2, 3):
        raise PackageError("unsupported world version")
    if type(world["world_id"]) is not str or not re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,63}", world["world_id"]):
        raise PackageError("invalid world identity")
    if world["schema_version"] == 2:
        if type(world["palette"]) is not list or not 1 <= len(world["palette"]) <= 16 or any(type(c) is not str or not re.fullmatch(r"[0-9a-f]{6}", c) for c in world["palette"]):
            raise PackageError("invalid legacy palette")
        for category, fields in {
            "sprites": {"id","name","width","height","frames"},
            "objects": {"id","sprite","program","x","y","vx","vy","target"},
            "programs": {"id","name","code"}}.items():
            if type(world[category]) is not list or not 1 <= len(world[category]) <= 16:
                raise PackageError("legacy component count exceeds budget")
            for item in world[category]:
                if type(item) is not dict or set(item) != fields:
                    raise PackageError("legacy component fields differ from contract")
                bounded(item["id"],1,254)
                if "name" in item and (type(item["name"]) is not str or len(item["name"]) > 64):
                    raise PackageError("invalid legacy name")
                if category == "sprites":
                    bounded(item["width"],1,16);bounded(item["height"],1,16)
                    if type(item["frames"]) is not list or not 1 <= len(item["frames"]) <= 16 or any(type(f) is not str or not re.fullmatch(r"[0-9a-f]+",f) or len(f)!=item["width"]*item["height"] for f in item["frames"]):
                        raise PackageError("invalid legacy sprite frames")
                elif category == "objects":
                    bounded(item["sprite"],1,254);bounded(item["program"],1,254)
                    bounded(item["x"],0,159);bounded(item["y"],0,89)
                    bounded(item["vx"],-8,8);bounded(item["vy"],-8,8);bounded(item["target"],0,255)
                else:
                    if type(item["code"]) is not list or not 1 <= len(item["code"]) <= 32:
                        raise PackageError("legacy program budget exceeded")
                    for byte in item["code"]:bounded(byte,0,255)
        # No global sys.path mutation and no duplicate implementation of v2 wire encoding.
        sprites = tuple(v2.Sprite(i["id"], i["width"], i["height"], tuple(bytes(int(c,16) for c in frame) for frame in i["frames"])) for i in world["sprites"])
        objects = tuple(v2.Object(i["id"], i["sprite"], i["program"], i["x"], i["y"], i["vx"], i["vy"], i["target"]) for i in world["objects"])
        programs = tuple(v2.Program(i["id"], bytes(i["code"])) for i in world["programs"])
        return v2.build_package(counter=counter, palette=tuple(int(c,16) for c in world["palette"]), sprites=sprites, objects=objects, programs=programs, private_key=private)
    if type(world["palette"]) is not list or not 1 <= len(world["palette"]) <= 256 or any(type(c) is not str or not re.fullmatch(r"[0-9a-f]{8}", c) for c in world["palette"]):
        raise PackageError("invalid RGBA palette")
    categories = {
        "sprites": {"id", "name", "width", "height", "display_width", "display_height", "frames"},
        "objects": {"id", "sprite", "program", "x", "y", "vx", "vy", "target"},
        "programs": {"id", "name", "code"}}
    for category, fields in categories.items():
        items = world[category]
        if type(items) is not list or not 1 <= len(items) <= 16:
            raise PackageError("component count exceeds budget")
        for item in items:
            if type(item) is not dict or set(item) != fields:
                raise PackageError("component fields differ from contract")
            bounded(item["id"], 1, 254)
            if "name" in item and (type(item["name"]) is not str or len(item["name"]) > 64):
                raise PackageError("component name exceeds budget")
            if category == "sprites":
                for dimension in ("width", "height"):
                    bounded(item[dimension], 1, 128)
                for dimension in ("display_width", "display_height"):
                    bounded(item[dimension], 1, 64)
                if type(item["frames"]) is not list or not 1 <= len(item["frames"]) <= 16 or any(type(f) is not str or not re.fullmatch(r"[0-9a-f]+", f) or len(f) != item["width"] * item["height"] * 2 for f in item["frames"]):
                    raise PackageError("invalid indexed frame")
            elif category == "programs":
                if type(item["code"]) is not list or not 1 <= len(item["code"]) <= 32:
                    raise PackageError("VM code exceeds budget")
                for byte in item["code"]:
                    bounded(byte, 0, 255)
            else:
                for field in ("sprite", "program"):
                    bounded(item[field], 1, 254)
                bounded(item["target"], 0, 255)
                bounded(item["x"], 0, 159); bounded(item["y"], 0, 89)
                bounded(item["vx"], -8, 8); bounded(item["vy"], -8, 8)
    return build_package(world, counter, private)
