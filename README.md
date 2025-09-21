# Vertex Language Documentation 🌀

Welcome to **Vertex** — a simple, expressive, and powerful programming language designed to be the **next Python killer**.  
Currently, Vertex runs on an interpreter and a Python transpiler, but will evolve into a full standalone compiler.

---

## 🚀 Getting Started

Clone first
bash
```
https://github.com/Ugochi56/Vertex.git
```

Compile to Python

bash
```
python vertexc.py test/hello.vx -o out/hello.py
python out/hello.py
```
**✨ Language Features**

**1. Variables**
Declare variables with let:

**vertex**
```
let name: string = "Ugo"
let year: int = 2025
```
let keyword is used for variable declaration.

Types are optional but encouraged (string, int, etc.).

**2. Printing**

**vertex**
```
print "Hello, " + name
print year
```
Use print to output values.

Concatenate strings with +.

**3. Arithmetic**

**vertex**
```
let x: int = 10
let y: int = 5

print x + y       # 15
print x * y       # 50
print x - y       # 5
print x / y       # 2
```

**📝 Example Program**

**vertex**
```
let name: string = "NAME"
let year: int = 2025

print "Hello, " + name
print "It is currently " + year

let x: int = 10
let y: int = 5

print "Sum: " + (x + y)
print "Product: " + (x * y)
```

**Output**
```
Hello, NAME
It is currently 2025
Sum: 15
Product: 50
```

**🔮 Roadmap (Planned Features)**

📝 Conditionals (if / else)

📝 Loops (for, while)

📝 Functions (fn greet(name: string))

📝 Classes & Objects (OOP support)

📝 Modules & Imports

📝 Custom Types & Enums
📝 Error Handling (try / catch)
📝 Direct Bytecode Compilation (no Python dependency)


**🤝 Contributing**
```
We welcome contributors!
. Fork the repo
. Create a branch (feature-x)
. Submit a pull request 🚀
```
