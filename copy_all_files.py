import UnityPy, shutil
from pathlib import Path
from get_abfile_dependences import *

BASE_PATH = Path(r"D:/ArkAssets")
COPY_PATH = Path(r"D:/ArknightsAssets/LEVEL_01-07")
SCENE_PATH = 'scenes/obt/main/level_main_01-07/level_main_01-07.ab'

manifest_env = UnityPy.load(str(BASE_PATH / 'torappu.ab'))

shutil.copy(str(BASE_PATH / SCENE_PATH), str(COPY_PATH / SCENE_PATH.replace('/', '_')))
print('copied main scene: ' + SCENE_PATH)
for dep in get_deps(get_manifest(manifest_env), SCENE_PATH):
    shutil.copy(str(BASE_PATH / dep), str(COPY_PATH / dep.replace('/', '_')))
    print('copied main scene: ' + dep)