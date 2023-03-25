using System;

namespace AssemblyFixer
{
    internal class Program
    {
        static void Main(string[] args)
        {
            AssemblySpliter spliter = new(@"D:/ArknightsDump/1.9.81/Il2cppDumperOut/DummyDll");
            spliter.Split(File.ReadAllLines(@"D:/ArknightsAssets/scripts.txt"));
            spliter.SaveAll(@"D:/ArknightsAssets/Fixed");
        }
    }
}