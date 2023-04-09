import UnityPy
from pathlib import Path
from get_abfile_dependences import *

BASE_PATH = Path(r"D:/ArkAssets") # 下载资源存储位置
LEVELIDS = [
    'Obt/Main/level_main_00-01',
    'Obt/Main/level_main_01-07',
    'Obt/Main/level_main_01-12',
    'Obt/Main/level_main_02-08',
    'Obt/Main/level_main_03-03',
    'Obt/Main/level_main_04-10',
    'Obt/Main/level_main_05-10',
    'Obt/Main/level_main_06-15',
    'Obt/Main/level_main_07-13',
    'Obt/Main/level_main_08-10',
    'Obt/Main/level_main_08-16',
    'Obt/Main/level_main_08-17',
    'Obt/Main/level_main_09-17',
    'Obt/Main/level_tough_10-15',
    'Obt/Main/level_tough_11-18',
    'Obt/Main/level_main_12-04',
    'Obt/Main/level_tough_12-18',
    'Activities/ACT3D0/level_act3d0_03',
    'Activities/ACT3D0/level_act3d0_ex03',
    'Activities/ACT3D0/level_act3d0_ex06',
    'Activities/ACT12SIDE/level_act12side_ex05',
    'Activities/act13side/level_act13side_sub-1-5',
    'Activities/ACT14SIDE/level_act14side_05',
    'Activities/ACT15side/level_act15side_02',
    'Activities/ACT15side/level_act15side_09',
    'Activities/act16side/level_act16side_06',
    'Activities/act16side/level_act16side_ex08',
    'Activities/act17side/level_act17side_09',
    'Activities/ACT5D0/level_act5d0_08',
    'Activities/ACT9D0/level_act9d0_08',
    'Activities/ACT11D0/level_act11d0_08',
    'Activities/ACT12D0/level_act12d0_08',
    'Activities/act16d5/level_act16d5_08',
    'Activities/act16d5/level_act16d5_ex05',
    'Activities/act17d7/level_act17d7_01',
    'Activities/act18d0/level_act18d0_06',
    'Activities/act18d3/level_act18d3_09',
    'activities/act3fun/level_act3fun_03',
    'activities/act4fun/level_act4fun_01',
    'obt/legion/lt06/level_lt06_05',
    'obt/rune/level_rune_14-01',
    'obt/roguelike/ro1/level_rogue1_4-5',
    'obt/roguelike/ro1/level_rogue1_b-8',
    'obt/roguelike/ro2/level_rogue2_4-5',
    'obt/roguelike/ro2/level_rogue2_b-8',
    'obt/roguelike/ro2/level_rogue2_b-10'
    ]

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