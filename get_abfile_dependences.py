import UnityPy

def get_manifest(manifest_env: UnityPy.Environment) -> dict | None:
    for obj in manifest_env.objects:
        if obj.type.name == 'AssetBundleManifest':
            return obj.read_typetree()

def get_deps(manifest: dict, path: str) -> list[str]:
    dep_names = []

    def get(_path: str):
        nonlocal dep_names
        temp_names = []

        #for obj in env.objects:
        #    if obj.type.name == 'PreloadData':
        #        for n in obj.read_typetree()['m_Dependencies']:
        #            if n not in dep_names: temp_names.append(n)

        for pair in manifest['AssetBundleNames']:
            if pair[1] == _path:
                first = pair[0]

        for info in manifest['AssetBundleInfos']:
            if info[0] == first:
                deps = info[1]['AssetBundleDependencies']

        for pair in manifest['AssetBundleNames']:
            if pair[0] in deps:
                if pair[1] not in dep_names and pair[1] not in temp_names: temp_names.append(pair[1])

        dep_names += temp_names
        for n in temp_names:
            get(n)

    get(path)
    return dep_names