using System;

namespace AssemblyFixer
{
    internal class Program
    {
        static void Main(string[] args)
        {
            AssemblySpliter spliter = new(@"D:\ArknightsDump\2.0.01\o\DummyDll"); // dump程序集
            spliter.Split(File.ReadAllLines(@"D:\ArknightsMapAssets\scripts.txt"));
            spliter.SaveAll(@"D:\ArknightsMapAssets\Level_2001_assets\Fixed"); // 程序集导出文件夹
        }
    }
}