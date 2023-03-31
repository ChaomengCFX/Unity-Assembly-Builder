import os
from pathlib import Path

def handle(dirpath):
    paths_to_remove: list[Path] = []
    for root, dirs, files in os.walk(dirpath):
        root = Path(root)
        for file in files:
            fp: Path = root / file
            if fp.suffix == '.prefab':
                asset = fp.with_suffix('.asset')
                asset_meta = fp.with_suffix('.asset.meta')
                paths_to_remove += [asset, asset_meta]

    for p in paths_to_remove:
        if not p.exists():
            print('[!] Not found ' + str(p))
            continue
        print('Removing ' + str(p))
        os.remove(str(p))

handle(r'D:\ArknightsMapAssets\Level_08-17_out\[uc]shaders.ab\ExportedProject\Assets') # 修复导出的assets