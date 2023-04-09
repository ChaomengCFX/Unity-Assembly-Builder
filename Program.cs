using System;

namespace AssemblyFixer
{
    internal class Program
    {
        static void Main(string[] args)
        {
            AssemblySpliter spliter = new(@"D:\ArknightsDump\1.9.91\Il2cppDumperOut\DummyDll"); // dump程序集
            spliter.Split(File.ReadAllLines(@"D:\ArknightsMapAssets\scripts.txt"));
            spliter.SaveAll(@"D:\ArknightsMapAssets\Fixed"); // 程序集导出文件夹
        }
    }
}