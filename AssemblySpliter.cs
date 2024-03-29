﻿using Mono.Cecil;
using Mono.Cecil.Cil;
using Mono.Collections.Generic;

namespace AssemblyFixer
{
    public class AssemblySpliter
    {
        private readonly string m_path;
        private readonly HashSet<AssemblyDefinition> m_assemblys = new();
        private readonly HashSet<ModuleDefinition> m_modules = new();
        private readonly HashSet<TypeReference> m_closedList = new();
        private readonly HashSet<TypeReference> m_depList = new();
        private readonly SplitSetting m_setting;

        public AssemblySpliter(string path, SplitSetting? setting = null)
        {
            m_setting = setting ?? new SplitSetting();
            m_path = path;
            MyAssemblyResolver resolver = new();
            foreach (FileInfo fileInfo in new DirectoryInfo(m_path).EnumerateFiles())
            {
                if (fileInfo.Extension == ".dll")
                {
                    AssemblyDefinition assemblyDef = AssemblyDefinition.ReadAssembly(fileInfo.FullName, new ReaderParameters { AssemblyResolver = resolver });
                    resolver.Register(assemblyDef);
                    bool skip = false;
                    foreach (string name in m_setting.skipAssemblies)
                    {
                        if (fileInfo.Name.Contains(name))
                        {
                            skip = true;
                            break;
                        }
                    }
                    if (!skip)
                    {
                        m_assemblys.Add(assemblyDef);
                        m_modules.Add(assemblyDef.MainModule);
                    }
                }
            }
        }

        private bool _Split(TypeDefinition typeDef, out HashSet<TypeDefinition> deps)
        {
            deps = new();

            if (typeDef.HasFields)
            {
                foreach (FieldDefinition fieldDef in typeDef.Fields.ToArray())
                {
                    if (fieldDef.HasCustomAttributes)
                    {
                        bool found = false;
                        foreach (CustomAttribute attribute in fieldDef.CustomAttributes.ToArray())
                        {
                            if (attribute.AttributeType.FullName == "UnityEngine.SerializeField")
                            {
                                _ClearCustomAttributesOfField(fieldDef);
                                TypeReference fieldTypeRef = fieldDef.FieldType;

                                if (!fieldTypeRef.ContainsGenericParameter)
                                {
                                    TypeDefinition fieldTypeDef = fieldTypeRef.Resolve();
                                    deps.Add(fieldTypeDef);
                                    if (fieldTypeRef.IsGenericInstance)
                                    {
                                        foreach (TypeDefinition genericType in _GetGenericTypes(fieldTypeRef))
                                        {
                                            deps.Add(genericType);
                                        }
                                    }
                                }
                                found = true;
                                break;
                            }
                        }
                        if (found) continue;
                    }

                    if (typeDef.IsValueType || (fieldDef.Attributes.HasFlag(FieldAttributes.Public) &&
                        !fieldDef.Attributes.HasFlag(FieldAttributes.Static) &&
                        !fieldDef.Attributes.HasFlag(FieldAttributes.InitOnly) &&
                        !fieldDef.Attributes.HasFlag(FieldAttributes.NotSerialized) &&
                        !fieldDef.Attributes.HasFlag(FieldAttributes.Literal)))
                    {
                        TypeReference fieldTypeRef = fieldDef.FieldType;
                        if (fieldTypeRef.IsValueType)
                        {
                            _ClearCustomAttributesOfField(fieldDef);
                            deps.Add(fieldTypeRef.Resolve());
                            continue;
                        }
                        else if (fieldTypeRef.ContainsGenericParameter)
                        {
                            _ClearCustomAttributesOfField(fieldDef);
                            continue;
                        }
                        else
                        {
                            TypeDefinition fieldTypeDef = fieldTypeRef.Resolve();
                            if (_IsUnityObject(fieldTypeDef) || fieldTypeDef.Attributes.HasFlag(TypeAttributes.Serializable) || fieldTypeDef.FullName == "System.Collections.Generic.List`1" || _IsJsonSerializeType(typeDef))
                            {
                                _ClearCustomAttributesOfField(fieldDef);
                                deps.Add(fieldTypeDef);
                                if (fieldTypeRef.IsGenericInstance)
                                {
                                    foreach (TypeDefinition genericType in _GetGenericTypes(fieldTypeRef))
                                    {
                                        deps.Add(genericType);
                                    }
                                }
                                continue;
                            }
                        }
                    }

                    // Remove Field
                    typeDef.Fields.Remove(fieldDef);
                }
            }

            _ClearAllMembersInType(typeDef, false);

            _HandleBaseType(typeDef);

            _HandleNestedType(typeDef);

            foreach (TypeDefinition depTypeDef in deps.ToArray())
            {
                if (m_closedList.Contains(depTypeDef) || !_CheckScope(depTypeDef))
                    deps.Remove(depTypeDef);
            }

            Console.WriteLine(string.Format("\u001b[36mSplited {0}\u001b[m", typeDef));

            return deps.Count != 0;
        }

        private bool _IsJsonSerializeType(TypeReference typeRef)
        {
            if (typeRef.IsNested) 
                return _IsJsonSerializeType(typeRef.DeclaringType);
            return m_setting.jsonSerializeType.Contains(typeRef.FullName);
        }

        private static bool _IsUnityObject(TypeDefinition typeDef)
        {
            TypeReference? baseRef = typeDef?.BaseType;
            if (baseRef == null) return false;
            if (baseRef.FullName == "UnityEngine.Object") return true;
            else
            {
                TypeDefinition baseDef = baseRef.Resolve();
                if (baseDef == null)
                {
                    Console.Write($"\u001b[1;31mCan't resolve {baseRef.FullName}\u001b[m");
                    return false;
                }
                return _IsUnityObject(baseDef);
            }
        }

        private void _ClearCustomAttributes(Collection<CustomAttribute> customAttributes)
        {
            foreach (CustomAttribute attribute in customAttributes.ToArray())
            {
                bool skip = false;
                foreach (string name in m_setting.saveAttributes)
                {
                    if (attribute.AttributeType.Scope.Name.Contains(name))
                    {
                        skip = true;
                        break;
                    }
                }
                if (!skip)
                    customAttributes.Remove(attribute);
            }
        }

        private void _ClearCustomAttributesOfField(FieldDefinition fieldDef)
        {
            if (fieldDef.HasCustomAttributes)
                _ClearCustomAttributes(fieldDef.CustomAttributes);
        }

        private void _ClearAllMembersInType(TypeDefinition typeDef, bool includeFields = false)
        {
            if (includeFields && typeDef.HasFields)
                typeDef.Fields.Clear();

            if (typeDef.HasMethods)
                typeDef.Methods.Clear();

            if (typeDef.HasProperties)
                typeDef.Properties.Clear();

            if (typeDef.HasEvents)
                typeDef.Events.Clear();

            if (typeDef.HasCustomAttributes)
                _ClearCustomAttributes(typeDef.CustomAttributes);

            if (typeDef.HasInterfaces)
                typeDef.Interfaces.Clear();
        }

        /// <summary>
        /// 获得类型的所有相关泛型
        /// </summary>
        /// <param name="typeRef">传入类型</param>
        /// <returns>所有相关泛型（仅用户程序集）</returns>
        private HashSet<TypeDefinition> _GetGenericTypes(TypeReference typeRef)
        {
            HashSet<TypeReference> typeRefs = new();

            void _GetInternal(TypeReference _typeRef)
            {
                if (_typeRef.IsGenericInstance)
                {
                    foreach (TypeReference parameter in ((IGenericInstance)_typeRef).GenericArguments)
                    {
                        if (!parameter.ContainsGenericParameter)
                        {
                            typeRefs.Add(parameter);
                            _GetInternal(parameter);
                        }
                    }
                }
            }

            _GetInternal(typeRef);

            HashSet<TypeDefinition> result = new();
            foreach (TypeReference tref in typeRefs)
            {
                if (_CheckScope(tref))
                    result.Add(tref.Resolve());
            }
            return result;
        }

        private bool _CheckScope(TypeReference typeRef) => m_modules.Contains(typeRef.Scope);

        private void _HandleBaseType(TypeDefinition typeDef)
        {
            TypeReference baseTypeRef = typeDef.BaseType;

            if (baseTypeRef == null || (!_CheckScope(baseTypeRef) && !baseTypeRef.IsGenericInstance)) return;

            if (baseTypeRef.IsGenericInstance)
            {
                foreach (TypeReference parameter in ((IGenericInstance)baseTypeRef).GenericArguments)
                {
                    if (!parameter.ContainsGenericParameter)
                    {
                        _HandleType(parameter.Resolve());
                    }
                }
            }

            if (_CheckScope(baseTypeRef))
                _HandleType(baseTypeRef.Resolve());
        }

        private void _HandleNestedType(TypeDefinition typeDef)
        {
            if (!typeDef.IsNested) return;
            TypeDefinition declaringTypeDef = typeDef.DeclaringType;
            if (!m_depList.Contains(declaringTypeDef))
            {
                m_depList.Add(declaringTypeDef);
                _HandleNestedType(declaringTypeDef);
            }
        }

        private void _HandleType(TypeDefinition typeDef)
        {
            if (typeDef == null) throw new ArgumentNullException(nameof(typeDef));
            if (m_closedList.Contains(typeDef) || !_CheckScope(typeDef)) return;
            else
            {
                m_closedList.Add(typeDef);
                if (!_Split(typeDef, out HashSet<TypeDefinition> deps)) return;
                else
                {
                    _HandleTypes(deps);
                }
            }
        }

        private void _HandleTypes(HashSet<TypeDefinition> types)
        {
            foreach (TypeDefinition typeDef in types)
            {
                _HandleType(typeDef);
            }
        }

        public void Split(string[] typesInScenes)
        {
            HashSet<string> typeNames = new(typesInScenes);
            HashSet<TypeDefinition> typesInScene = new();
            foreach (ModuleDefinition module in m_modules)
            {
                foreach (TypeDefinition typeDef in module.Types)
                {
                    if (typeNames.Contains(typeDef.FullName))
                    {
                        typesInScene.Add(typeDef);
                        typeNames.Remove(typeDef.FullName);
                    }
                }
            }

            Console.WriteLine("\u001b[1;34mThe following type will not be handled:\u001b[m\u001b[1;34m");
            Console.WriteLine(string.Join('\n', typeNames) + "\u001b[m");

            _HandleTypes(typesInScene);

            void _HandleInternal(TypeDefinition _typeDef, Collection<TypeDefinition> _types)
            {
                if (!m_closedList.Contains(_typeDef))
                {
                    if (m_depList.Contains(_typeDef))
                    {
                        _ClearAllMembersInType(_typeDef, true);
                    }
                    else
                    {
                        _types.Remove(_typeDef);
                    }
                }
                if (_typeDef.HasNestedTypes)
                {
                    // 处理嵌套类
                    foreach (TypeDefinition nestedTypeDef in _typeDef.NestedTypes.ToArray())
                    {
                        _HandleInternal(nestedTypeDef, _typeDef.NestedTypes);
                    }
                }
            }

            foreach (ModuleDefinition module in m_modules)
            {
                foreach (TypeDefinition typeDef in module.Types.ToArray())
                {
                    _HandleInternal(typeDef, module.Types);
                }
            }
        }

        public void SaveAll(string path)
        {
            DirectoryInfo dirInfo = Directory.CreateDirectory(path);
            Console.WriteLine(string.Format("\u001b[1;34mThe files will be saved to {0}\u001b[m", path));

            if (!dirInfo.Exists)
                dirInfo.Create();

            foreach (AssemblyDefinition assembly in m_assemblys)
            {
                if (assembly.MainModule.Types.Count == 0) continue;
                Console.WriteLine(string.Format("\u001b[1;32mWriting assembly [{0}] ...\u001b[m", assembly.MainModule.Name));
                assembly.Write(Path.Combine(path, assembly.MainModule.Name));
            }
            Console.WriteLine("\u001b[1;34mOutput done\u001b[m");
        }
    }
}