import UnityPy
from pathlib import Path
from get_abfile_dependences import *
from levels import LEVELIDS

BASE_PATH = Path(r"D:/ArkAssets") # 下载资源存储位置

SCENE_PATHS = [] # 场景文件 ['scenes/obt/main/level_main_07-13/level_main_07-13.ab']
for s in LEVELIDS:
    p = Path(s)
    SCENE_PATHS.append('scenes/' + str(p / p.name).lower().replace('\\', '/') + '.ab')

manifest_env = UnityPy.load(str(BASE_PATH / 'torappu.ab'))

def get_scripts(env: UnityPy.Environment) -> list[str]:
    scripts = []
    for obj in env.objects:
        if obj.type.name == 'MonoScript':
            typetree = obj.read_typetree()
            scripts.append((typetree['m_Namespace'] + '.' if typetree['m_Namespace'] not in ['', None] else '') + typetree['m_ClassName'])
    return scripts

mainifest = get_manifest(manifest_env)
deps = []
scripts = []
for scene in SCENE_PATHS:
    main_scene_env = UnityPy.load(str(BASE_PATH / scene))
    scripts += get_scripts(main_scene_env)
    print('loaded main scene: ' + scene)
    for dep in get_deps(mainifest, scene):
        if dep in deps: continue
        deps.append(dep)
        dep_env = UnityPy.load(str(BASE_PATH / dep))
        scripts += get_scripts(dep_env)
        print('loaded dep: ' + dep)

scripts.append('Torappu.LevelData')

scripts = set(scripts) #去重

with open('D:/ArknightsMapAssets/scripts.txt', 'w', encoding='utf-8') as f: # 导出位置
    f.write('\n'.join(scripts))