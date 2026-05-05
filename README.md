PIT Mutation Testing Toolkit (Commons Numbers)

This repository contains a mutation testing pipeline built around PIT and the Apache Commons Numbers project. It includes Java source modules, PIT mutation reports, generated build artifacts, and a Python-based mutation applier that recreates mutants using token-level Java parsing through `javalang`.

Layout

```text
.
├── README.md
├── .gitignore
├── scripts/
│   └── MutationApplier.py
└── test/
    └── commons-numbers-1.0-src/
        ├── pom.xml
        ├── LICENSE
        ├── NOTICE
        ├── RELEASE-NOTES.txt
        ├── CONTRIBUTING.md
        ├── src/
        ├── target/
        ├── doc/
        ├── dist-archive/
        ├── commons-numbers-angle/
        ├── commons-numbers-arrays/
        ├── commons-numbers-combinatorics/
        ├── commons-numbers-complex/
        ├── commons-numbers-core/
        ├── commons-numbers-examples/
        ├── commons-numbers-field/
        ├── commons-numbers-fraction/
        ├── commons-numbers-gamma/
        ├── commons-numbers-primes/
        ├── commons-numbers-quaternion/
        └── commons-numbers-rootfinder/
