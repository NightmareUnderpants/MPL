using System;
using System.Collections.Generic;

namespace SimpleExample
{
    public class User
    {
        public string Name { get; set; }
        public int Age { get; set; }

        public string GetInfo()
        {
            return $"Name: {Name}, Age: {Age}";
        }

        public User(string name, int age)
        {
            Name = name;
            Age = age;
        }
    }

    public class Program
    {
        public static void Main(string[] args)
        {
            var user = new User("John", 25);
            var info = user.GetInfo();
            Console.WriteLine(info);
        }
    }
}