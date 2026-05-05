# PIT Mutation Testing Toolkit (Commons Numbers)

This repository contains a mutation testing pipeline built around PIT and the Apache Commons Numbers project. It includes Java source modules, PIT mutation reports, generated build artifacts, and a Python-based mutation applier that recreates mutants using token-level Java parsing through `javalang`.

## Layout

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
Overview

This project performs mutation testing and mutation reconstruction on the Apache Commons Numbers project.

The pipeline supports:

Mutation testing using PIT on a multi-module Java Maven project
Extraction of mutation data from PIT-generated mutations.xml files
Java token-based mutation application using Python and javalang
Generation of mutated Java source files for manual inspection and analysis

Apache Commons Numbers is structured as a multi-module Maven project. Because of this, each module can have its own PIT mutation report.

Example modules include:

commons-numbers-angle
commons-numbers-arrays
commons-numbers-combinatorics
commons-numbers-complex
commons-numbers-core
commons-numbers-field
commons-numbers-fraction
commons-numbers-gamma
commons-numbers-primes
commons-numbers-quaternion
commons-numbers-rootfinder
Requirements
Java 8 or higher
Maven
Python 3
javalang

Install the required Python dependency:

python3 -m pip install javalang
Running PIT

To generate PIT mutation reports for a specific module, go into that module and run PIT using Maven.

Example:

cd test/commons-numbers-1.0-src/commons-numbers-angle
mvn test-compile org.pitest:pitest-maven:mutationCoverage

This produces a PIT report at:

test/commons-numbers-1.0-src/commons-numbers-angle/target/pit-reports/mutations.xml

Because Commons Numbers has multiple modules, other modules may also have their own reports, such as:

test/commons-numbers-1.0-src/commons-numbers-arrays/target/pit-reports/mutations.xml
test/commons-numbers-1.0-src/commons-numbers-core/target/pit-reports/mutations.xml
test/commons-numbers-1.0-src/commons-numbers-fraction/target/pit-reports/mutations.xml
Running the Mutation Applier

From the repository root, run the mutation applier on one module:

python3 scripts/MutationApplier.py test/commons-numbers-1.0-src test/commons-numbers-1.0-src/commons-numbers-angle/target/pit-reports/mutations.xml

This command:

Reads the PIT mutations.xml file
Locates the matching Java source file
Uses javalang to tokenize the Java source
Applies supported mutation transformations
Writes mutated Java files into an output folder
Running on All Modules

To run the mutation applier on every module that has a PIT report:

for f in test/commons-numbers-1.0-src/commons-numbers-*/target/pit-reports/mutations.xml; do
  echo "Running MutationApplier on $f"
  python3 scripts/MutationApplier.py test/commons-numbers-1.0-src "$f"
done
Supported Mutation Types

MutationApplier.py currently supports common PIT mutation types such as:

Conditional boundary mutations
Negated conditional mutations
Math operator mutations
Increment mutations
Remove conditional mutations
Primitive return mutations
Boolean return mutations
Null return mutations
Void method call mutations
Some non-void method call mutations

Unsupported mutations are skipped and reported in the terminal output.

Output

This project produces two main types of output.

1. PIT Mutation Reports

PIT generates mutation report files named mutations.xml.

Example location:

test/commons-numbers-1.0-src/commons-numbers-angle/target/pit-reports/mutations.xml

These XML files contain mutation metadata such as:

Mutated class
Mutated method
Source file
Line number
Mutator type
Mutation status
Whether the mutation was detected
Mutation description
2. Recreated Mutated Java Files

The Python mutation applier generates mutated Java source files for inspection.

Example output folder:

mutated_output/

When run across modules, the output may be organized by module, such as:

mutated_output/
├── commons-numbers-angle/
├── commons-numbers-arrays/
├── commons-numbers-core/
└── commons-numbers-fraction/

Each generated Java file represents a recreated mutant based on PIT mutation data.

Example Workflow

From the repository root:

python3 -m pip install javalang

python3 scripts/MutationApplier.py test/commons-numbers-1.0-src test/commons-numbers-1.0-src/commons-numbers-angle/target/pit-reports/mutations.xml

To run across all available modules:

for f in test/commons-numbers-1.0-src/commons-numbers-*/target/pit-reports/mutations.xml; do
  echo "Running MutationApplier on $f"
  python3 scripts/MutationApplier.py test/commons-numbers-1.0-src "$f"
done
Notes

This repository is organized as a mutation testing artifact repository. The scripts/ folder contains the mutation-processing logic, while the test/commons-numbers-1.0-src/ folder contains the Apache Commons Numbers project and related PIT artifacts.

Unlike a single-module project such as Apache Commons DbUtils, Apache Commons Numbers is multi-module. Therefore, mutation reports and source files are distributed across several commons-numbers-* submodules.
