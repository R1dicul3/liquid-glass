# -*- coding: utf-8 -*-
"""Shared helpers: logging, idempotent asset find/create/save."""
import os
import unreal

LOG_PATH = r"D:\ue5\liquied\outputs\build_log.txt"


def log(msg):
    line = "[liquid-glass] " + str(msg)
    try:
        print(line)
    except Exception:
        pass
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def ensure_dir(path):
    unreal.EditorAssetLibrary.make_directory(path)


def asset_exists(path):
    return unreal.EditorAssetLibrary.does_asset_exist(path)


def load_asset(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def delete_asset(path):
    if asset_exists(path):
        unreal.EditorAssetLibrary.delete_asset(path)


def create_asset(name, package_path, uclass, factory):
    at = unreal.AssetToolsHelpers.get_asset_tools()
    return at.create_asset(name, package_path, uclass, factory)


def save_asset(path, only_if_dirty=True):
    return unreal.EditorAssetLibrary.save_asset(path, only_if_dirty)


def save_dir(path, recursive=True):
    return unreal.EditorAssetLibrary.save_directory(path, recursive, True)
