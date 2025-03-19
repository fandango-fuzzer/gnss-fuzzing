# Fandango GNSS Fuzzing

This repository contains the implementation of **Fandango**, a flexible fuzzing tool tailored for testing GNSS (Global Navigation Satellite System) modules and other binary protocols. The tool leverages evolutionary algorithms to automatically generate inputs based on a user-defined grammar, allowing testers to target specific edge cases and vulnerabilities.

The primary goal of this project is to show how easily tailored fuzzing goals and constraints can be set up using Fandango to ensure comprehensive testing of GNSS-related protocols.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Specifications](#specifications)
- [Constraints and Fuzzing Configuration](#constraints-and-fuzzing-configuration)
- [Results](#results)
- [Contributions](#contributions)

---

## Installation

To run the Fandango GNSS fuzzing tests, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/fandango-fuzzer/gnss-fuzzing.git
    cd gnss-fuzzing
    ```

2. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure you have Python 3.8 or later.

---

## Usage

To generate fuzzed test cases for a specified GNSS protocol, use the following command:

```bash
fandango fuzz --file-mode=binary -f <specification-file>.fan -n <num-tests> -d <output-directory>
```

### Example:

To generate 100 test cases using the `ubx_cfg_navspg.fan` specification and save them to the `corpus` directory:

```bash
fandango fuzz --file-mode=binary -f specification/ubx_cfg_navspg.fan -n 100 -d corpus
```

This command will run Fandango and produce a set of fuzzed files based on the defined grammar and constraints.

---

## Specifications

Fandango uses a specification file, written in its custom language (with `.fan` extension), that defines the structure of the protocol being tested. These specifications include:

- Grammar rules
- Constraints on values (e.g., floating-point ranges, distributions, etc.)
- Special handling for extreme values, invalid combinations, and checksums

### Example Specification: `ubx_cfg_navspg.fan`

```plaintext
<start> ::= <ubx_message>

<ubx_message> ::= <ubx_header> <ubx_payload> <ubx_checksum>
...
```

You can define your own protocol specifications or modify existing ones to match your testing needs.

---

## Constraints and Fuzzing Configuration

Fandango allows users to set specific constraints in the grammar, such as:

- **Distributions**: Control the range of values that fields can take, using Python functions.
- **Extreme Values**: Introduce edge cases like NaN, infinity, and overflows.
- **Length Encodings**: Dynamically calculate lengths based on payloads.
- **Checksums**: Ensure that checksum fields are properly computed and match expectations.

These constraints ensure that the generated test cases are realistic and target a variety of failure modes, such as buffer overflows, invalid checksums, and unhandled extreme values.

---

## Results

Once fuzzing is complete, you can analyze the test results. Any generated inputs that result in crashes or unexpected behavior can be found in the `crashes` directory. These files are saved for further analysis and debugging.