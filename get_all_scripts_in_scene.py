import UnityPy
from pathlib import Path

BASE_PATH = Path(r"D:/ArkAssets")
SCENE_PATH = 'scenes/obt/main/level_main_01-07/level_main_01-07.ab'

manifest_env = UnityPy.load(str(BASE_PATH / 'torappu.ab'))

for obj in manifest_env.objects:
    if obj.type.name == 'AssetBundleManifest':
        manifest = obj.read_typetree()

def get_deps(env: UnityPy.Environment, path) -> list[str]:
    dep_names = []

    def get(env: UnityPy.Environment, path):
        nonlocal dep_names
        temp_names = []

        for obj in env.objects:
            if obj.type.name == 'PreloadData':
                for n in obj.read_typetree()['m_Dependencies']:
                    if n not in dep_names: temp_names.append(n)

        for pair in manifest['AssetBundleNames']:
            if pair[1] == path:
                first = pair[0]

        for info in manifest['AssetBundleInfos']:
            if info[0] == first:
                deps = info[1]['AssetBundleDependencies']

        for pair in manifest['AssetBundleNames']:
            if pair[0] in deps:
                if pair[1] not in dep_names and pair[1] not in temp_names: temp_names.append(pair[1])

        dep_names += temp_names
        for n in temp_names:
            get(env, n)

    get(env, path)
    return dep_names

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
for dep in get_deps(main_scene_env, SCENE_PATH):
    dep_env = UnityPy.load(str(BASE_PATH / dep))
    scripts += get_scripts(dep_env)
    print('loaded dep: ' + dep)

scripts = set(scripts) #去重

with open('D:/ArknightsAssets/scripts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(scripts))