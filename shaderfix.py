import UnityPy

unity3d = r"D:\level_custom.unity3d"
unity3d_fixed = r"D:\level_custom-fixed.unity3d"
ab = r"D:\ArknightsMapAssets\Level_2001_assets"

unity3d_env = UnityPy.load(unity3d)
ab_env = UnityPy.load(ab)

def get_shaders(env: UnityPy.Environment):
    temp = {}
    for obj in env.objects:
        if obj.type.name == "Material":
            tree = obj.read_typetree()
            temp[tree['m_Name']] = tree['m_Shader']['m_PathID']
    return temp


def get_all_shaders(env: UnityPy.Environment):
    temp = []
    for obj in env.objects:
        if obj.type.name == "Shader":
            temp.append(obj.read_typetree()['m_ParsedForm']['m_Name'])
    return temp

shaders_need_fixed = get_shaders(unity3d_env)
shader_to_shader_dict = {}

shaders_need_fixed = get_shaders(unity3d_env)
shaders_all = get_all_shaders(unity3d_env)
shader_to_shader_dict : dict[int, UnityPy.environment.ObjectReader] = {}
shader_to_shader_dict_hidden = {}

for asset in ab_env.assets:
    asset: UnityPy.environment.SerializedFile = asset
    for pathid, obj in asset.objects.items():
        if obj.type.name == "Material":
            typetree = obj.read_typetree()
            mt_name = typetree['m_Name']
            if mt_name in shaders_need_fixed:
                pid = typetree['m_Shader']['m_PathID']
                if pid in asset.objects:
                    shader_to_shader_dict[shaders_need_fixed[mt_name]] = asset.objects[pid]
                else:
                    print(mt_name)
                    for obj2 in ab_env.objects:
                        if obj2.path_id == pid:
                            shader_to_shader_dict[shaders_need_fixed[mt_name]] = obj2

for obj in ab_env.objects:
    if obj.type.name == "Shader":
        typetree = obj.read_typetree()
        shader_name = typetree['m_ParsedForm']['m_Name']
        if 'Hidden' in shader_name and shader_name in shaders_all:
            shader_to_shader_dict_hidden[shader_name] = typetree

for obj in unity3d_env.objects:
    if obj.type.name == "Shader":
        shader_name = obj.read_typetree()['m_ParsedForm']['m_Name']
        if 'Hidden' in shader_name:
            if shader_name in shader_to_shader_dict_hidden:
                obj.save_typetree(shader_to_shader_dict_hidden[shader_name])
                print(shader_name)
        elif obj.path_id in shader_to_shader_dict:
            obj.save_typetree(shader_to_shader_dict[obj.path_id].read_typetree())
            print(shader_name)


with open(unity3d_fixed, 'wb') as f:
    f.write(unity3d_env.file.save(packer='lz4'))