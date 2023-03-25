import UnityPy
from pathlib import Path
from get_abfile_dependences import *

BASE_PATH = Path(r"D:/ArkAssets")
SCENE_PATH = 'scenes/obt/main/level_main_01-07/level_main_01-07.ab'

manifest_env = UnityPy.load(str(BASE_PATH / 'torappu.ab'))

def get_scripts(env: UnityPy.Environment) -> list[str]:
    scripts = []
    for obj in env.objects:
        if obj.type.name == 'MonoScript':
            typetree = obj.read_typetree()
            scripts.append((typetree['m_Namespace'] + '.' if typetree['m_Namespace'] not in ['', None] else '') + typetree['m_ClassName'])
    return scripts

main_scene_env = UnityPy.load(str(BASE_PATH / SCENE_PATH))
scripts = get_scripts(main_scene_env)
print('loaded main scene: ' + SCENE_PATH)
for dep in get_deps(get_manifest(manifest_env), SCENE_PATH):
    dep_env = UnityPy.load(str(BASE_PATH / dep))
    scripts += get_scripts(dep_env)
    print('loaded dep: ' + dep)

scripts = set(scripts) #去重

with open('D:/ArknightsAssets/scripts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(scripts))