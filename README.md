# CTF Utils

This repository is a collection of my **write-ups**, **learning notes**, **labs** and **helper scripts** I build along the way.  
It will serve as a place to document what I’m learning, practice, code snippets, and solutions to challenges.  

---


## Structure Overview
```bash
.
├── labs/                    # Structured vulnerability practice
├── ctf-writeups/           # Competition solutions and writeups
├── scripting/              # Code fundamentals and utilities
├── tools/                  # ready to use tools
├── resources/              # Reference materials and payloads
└── notes/                  # Concepts and methodologies
```
[open_tree](#main-structure)
 
## 📚 [Labs](./labs)

Hands on practice with labs organized by attack type. Each lab includes detailed notes, exploitation scripts, and lessons learned.

**Current:**
- **SQL Injection** - PortSwigger Academy progression (1-18)
- **XSS** - Cross-site scripting challenges and bypass techniques

---

## 🏆 [CTF Writeups](./ctf-writeups/README.md)

Detailed solutions from capture-the-flag competitions and challenge platforms, organized by year and platform.

**What to Expect:**
- Complete methodology and thought process
- Exploitation scripts with inline comments
- Alternative approaches and rabbit holes encountered
- Tools and techniques used
- Lessons learned for future challenges

**Table of Contents**
 1. [Root-Me TCP Encoded String Challenge](./ctf-writeups/2025/root-me.org/tcp-encoded-string/WRITEUP-tcp-encoded-string.md)
 2. [Another CTF challenge](#2-next)  
 3. [More to Come](#3-aa)

---

## 💻 [Scripting](./scripting)

Supporting code and learning materials that don't belong to specific labs but are essential for exploitation and automation.

**What to Expect:**
- Learning notes on each module/library
- Progressive examples (basic → advanced)
- Real-world use cases from labs and CTFs
- Quick reference snippets


**Table of Contents**
 1. [regex](./scripting/fundamentals/regex/LEARN-regex.md)
 2. [something else](#2-next)  
 3. [More to Come](#3-aa)

---

## 🛠️ [Tools](./tools)

Production-ready utilities built during my journey - scripts that proved useful enough to be polished and reused.
 
**What to Expect:**
- Well-documented, reusable code
- Command-line interfaces with help text
- Tools born from solving actual challenges
- Performance-optimized for real-world use

**Table of Contents**
 1. [proxy checker](./tools/proxy_checkers/README.md)
 2. [tool x](#2-next)  
 3. [More to Come](#3-aa)

---

## 📖 Resources

Reference materials, cheatsheets, and curated knowledge base.

**Contents:**
- **cheatsheets/** - Quick references for common vulnerabilities
- **payloads/** - Collections for SQL injection, XSS, command injection, etc.
- **files/** - Test data and sample inputs for practicing parsing/exploitation
- **reading-list.md** - Books, articles, and courses I'm working through
- **useful-links.md** - Tools, platforms, and resources I frequently use

---

## 📝 Notes

General learning documentation for concepts and methodologies that span multiple challenges.

**Contents:**
- **concepts/** - Web vulnerabilities, network fundamentals, cryptography basics
- **methodologies/** - Testing approaches, enumeration strategies, privilege escalation
- **til.md** - Today I Learned - quick daily discoveries and "aha!" moments

---

---

## Purpose

- Post **CTF writeups** (step-by-step + code)  
- Post solutions to labs 
- Record what I’m **learning per challenge**  
- Build a personal library of **tools and snippets** useful for CTFs  

---

🚀 Ongoing project — more writeups & utilities will be added as I progress.  


---

## Main Structure

```bash
.
├── README.md
├── labs/
│   ├── sql-injection/
│   │   ├── README.md
│   │   ├── portswigger
│   │   │   ├── notes.md
│   │   │   ├── solution.py
│   │   │   └── screenshots/
│   │   └── ...
│   ├── xss/
│   └── ...
│
├── ctf-writeups/
│   ├── 2025/
│   │   ├── root-me.org/
│   │   │   ├── tcp-encoded-string/
|   |   │   │   ├── writeup.md
│   │   │   |   └── root-me-TCP-Encoded-String.py
|   │   │   └── ...
│   │   └── ...
│   └── README.md
│
├── scripting/
│   ├── fundamentals/
│   │   ├── regex/
│   │   │   ├── notes.md
│   │   │   └── regex-learn.py
│   ├── web/
│   │   ├── requests-basics/
│   │   │   ├── notes.md
│   │   │   └── examples.py
│   │   ├── session-handling/
│   │   └── ...
│   ├── networking/
│   │   ├── sockets/
│   │   ├── urllib/
│   │   └── ...
│   └── README.md (quick reference guide)
│
├── tools/
│   ├── encoders/
│   │   ├── ascii_converter.py
│   │   └── ...
│   ├── web/
│   │   ├── sqli_fuzzer.py
│   │   └── ...
│   ├── proxy_checkers/
│   │   ├── proxy_checker_simple.py
│   │   └── proxy_checker_with_scamalytics.py
│   ├── misc/
│   └── README.md (tool documentation)
│
├── resources/
│   ├── cheatsheets/
│   │   ├── sql-injection.md
│   │   └── ...
│   ├── payloads/
│   │   ├── sqli-payloads.txt
│   │   ├── xss-payloads.txt
│   │   └── ...
│   ├── files/
│   │   ├── regex/
│   │   │   └── data.txt
│   │   ├── sqli-payloads.txt
│   │   └── ...
│   ├── reading-list.md
│   └── useful-links.md
│
└── notes/
#    ├── concepts/
#    │   ├── web-vulnerabilities.md
#    │   ├── network-basics.md
#    │   └── ...
#    ├── methodologies/
#    │   ├── web-app-testing.md
#    │   ├── enumeration.md
#    │   └── ...
    └── til.md (Today I Learned - quick daily notes)

```

[back to top ](#ctf-utils)
