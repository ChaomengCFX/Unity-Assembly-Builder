import UnityPy, shutil
from pathlib import Path
from get_abfile_dependences import *
from levels import LEVELIDS

BASE_PATH = Path(r"D:/ArkAssets")
COPY_PATH = Path(r"D:\ArknightsMapAssets\Level_2001_assets")

SCENE_PATHS = [] # 场景文件 ['scenes/obt/main/level_main_07-13/level_main_07-13.ab']
for s in LEVELIDS:
    p = Path(s)
    SCENE_PATHS.append('scenes/' + str(p / p.name).lower().replace('\\', '/') + '.ab')

manifest_env = UnityPy.load(str(BASE_PATH / 'torappu.ab'))
manifest = get_manifest(manifest_env)
deps = []
for sp in SCENE_PATHS:
    shutil.copy(str(BASE_PATH / sp), str(COPY_PATH / sp.replace('/', '_')))
    print('copied main scene: ' + sp)
    for dep in get_deps(manifest, sp):
        if dep in deps: continue
        deps.append(dep)
        shutil.copy(str(BASE_PATH / dep), str(COPY_PATH / dep.replace('/', '_')))
        print('copied dep: ' + dep)