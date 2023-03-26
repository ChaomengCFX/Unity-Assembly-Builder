import UnityPy

unity3d = r"D:\level_custom.unity3d"
unity3d_fixed = r"D:\level_custom-fixed.unity3d"
ab = r"D:\ArknightsMapAssets\Level_01-07_assets"

unity3d_env = UnityPy.load(unity3d)
ab_env = UnityPy.load(ab)

def get_shaders(env: UnityPy.Environment):
    temp = []
    for obj in env.objects:
        if obj.type.name == "Shader":
            temp.append(obj.read_typetree()['m_ParsedForm']['m_Name'])
    return temp

shaders_need_fixed = get_shaders(unity3d_env)
shader_to_shader_dict = { }

for obj in ab_env.objects:
    if obj.type.name == "Shader":
        typetree = obj.read_typetree()
        shader_name = typetree['m_ParsedForm']['m_Name']
        if shader_name in shaders_need_fixed:
            shader_to_shader_dict[shader_name] = typetree

for obj in unity3d_env.objects:
    if obj.type.name == "Shader":
        shader_name = obj.read_typetree()['m_ParsedForm']['m_Name']
        if shader_name in shader_to_shader_dict:
            obj.save_typetree(shader_to_shader_dict[shader_name])
            print(shader_name)

with open(unity3d_fixed, 'wb') as f:
    f.write(unity3d_env.file.save(packer='lz4'))