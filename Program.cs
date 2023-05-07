using System;
using System.IO;

namespace AssemblyFixer
{
    internal class Program
    {
        static void Main(string[] args)
        {
            SplitSetting splitSetting = new SplitSetting();
            splitSetting.skipAssemblies.AddRange(new List<string> {
                "UnityEngine",
                "DOTween",
                "System",
                "mscorlib",
                "Il2CppDummyDll",
                "Newtonsoft.Json",
                "spine-unity"
            });
            splitSetting.saveAttributes.AddRange(new List<string> {
                "UnityEngine",
                "DOTween",
                "System",
                "mscorlib",
                "Il2CppDummyDll",
                "Newtonsoft.Json",
                "spine-unity"
            });
            splitSetting.jsonSerializeType.Add("Torappu.LevelData");
            AssemblySpliter spliter = new(@"D:\ArknightsDump\2.0.01\o\DummyDll", splitSetting); // dump程序集
            spliter.Split(File.ReadAllLines(@"D:\ArknightsMapAssets\scripts.txt"));
            spliter.SaveAll(@"D:\ArknightsMapAssets\Level_2001_assets\Fixed"); // 程序集导出文件夹
        }
    }
}