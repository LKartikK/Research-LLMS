import sys
import os
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import javalang


def find_source_file(root_dir, file_name, preferred_module=None):
    """
    Recursively search for the Java source file.

    Priority:
    1. Files inside the same module as the mutations.xml
    2. Files inside src/main
    3. Files inside any /main/ directory
    4. Any matching file name
    """
    matches = []

    try:
        for path in Path(root_dir).rglob(file_name):
            if path.is_file():
                matches.append(path)
    except Exception:
        return None

    if not matches:
        return None

    if preferred_module:
        for path in matches:
            normalized = path.as_posix()
            if f"/{preferred_module}/" in normalized or normalized.startswith(
                f"{preferred_module}/"
            ):
                if "/src/main/" in normalized:
                    return str(path)

        for path in matches:
            normalized = path.as_posix()
            if f"/{preferred_module}/" in normalized or normalized.startswith(
                f"{preferred_module}/"
            ):
                return str(path)

    for path in matches:
        normalized = path.as_posix()
        if "/src/main/" in normalized:
            return str(path)

    for path in matches:
        normalized = path.as_posix()
        if "/main/" in normalized:
            return str(path)

    return str(matches[0])


def get_module_name_from_xml_path(xml_path):
    """
    Extract module name from paths like:
    ./commons-numbers-arrays/target/pit-reports/mutations.xml

    Returns:
    commons-numbers-arrays
    """
    parts = Path(xml_path).parts

    for part in parts:
        if part.startswith("commons-numbers-"):
            return part

    return "root"


def safe_tokenize(java_code):
    """
    Tokenize Java source using javalang.
    Returns a list of tokens, or an empty list if tokenization fails.
    """
    try:
        return list(javalang.tokenizer.tokenize(java_code))
    except Exception:
        return []


def safe_parse(java_code):
    """
    Parse Java source using javalang.
    This is used as a validation step.
    If parsing fails, the mutation can still be attempted with tokenization.
    """
    try:
        return javalang.parse.parse(java_code)
    except Exception:
        return None


def get_tokens_on_line(tokens, line_number):
    """
    Return all javalang tokens that appear on the target line.
    """
    line_tokens = []

    for token in tokens:
        if token.position and token.position.line == line_number:
            line_tokens.append(token)

    return line_tokens


def replace_at_column(line, column_1_based, old_text, new_text):
    """
    Replace text at a specific Java token column.
    javalang columns are 1-based.
    Python string indexes are 0-based.
    """
    index = column_1_based - 1

    if index < 0 or index >= len(line):
        return None

    if line[index : index + len(old_text)] != old_text:
        return None

    return line[:index] + new_text + line[index + len(old_text) :]


def replace_first_matching_operator(line, line_tokens, operator_mapping):
    """
    Replace the first matching Java operator token on the target line.
    operator_mapping example:
        {"<": "<=", "<=": "<"}
    """
    sorted_ops = sorted(operator_mapping.keys(), key=len, reverse=True)

    for token in line_tokens:
        token_value = getattr(token, "value", None)

        if token_value in sorted_ops:
            new_value = operator_mapping[token_value]
            changed = replace_at_column(
                line=line,
                column_1_based=token.position.column,
                old_text=token_value,
                new_text=new_value,
            )

            if changed is not None:
                return changed

    return None


def get_math_mapping_from_description(description):
    """
    PIT MathMutator descriptions usually describe the replacement clearly.
    This function maps PIT descriptions to Java operator replacements.
    """
    d = description.lower()

    if "addition with subtraction" in d:
        return {"+": "-"}
    if "subtraction with addition" in d:
        return {"-": "+"}
    if "multiplication with division" in d:
        return {"*": "/"}
    if "division with multiplication" in d:
        return {"/": "*"}
    if "modulus with multiplication" in d:
        return {"%": "*"}
    if "multiplication with modulus" in d:
        return {"*": "%"}
    if "bitwise and with or" in d:
        return {"&": "|"}
    if "bitwise or with and" in d:
        return {"|": "&"}
    if "exclusive or with and" in d:
        return {"^": "&"}
    if "shift left with shift right" in d:
        return {"<<": ">>"}
    if "shift right with shift left" in d:
        return {">>": "<<"}
    if "unsigned shift right with shift left" in d:
        return {">>>": "<<"}

    return None


def mutate_remove_conditional(line, description):
    """
    Handles RemoveConditionalMutator.
    Example:
        if (x > 0) {
    becomes:
        if (true) {
    or:
        if (false) {
    """
    d = description.lower()

    if "with true" in d:
        replacement = "true"
    elif "with false" in d:
        replacement = "false"
    else:
        return None

    pattern = r"\b(if|while)\s*\((.*)\)"
    match = re.search(pattern, line)

    if not match:
        return None

    start = match.start(2)
    end = match.end(2)

    return line[:start] + replacement + line[end:]


def mutate_return_value(line, description):
    """
    Handles return-value mutators.
    Uses regex for final rewrite because javalang does not rewrite source directly.
    """
    d = description.lower()

    if "return with 0" in d or "replaced int return with 0" in d:
        return re.sub(r"\breturn\s+.*?;", "return 0;", line)

    if "return with 1" in d:
        return re.sub(r"\breturn\s+.*?;", "return 1;", line)

    if "return with null" in d:
        return re.sub(r"\breturn\s+.*?;", "return null;", line)

    if "return with true" in d:
        return re.sub(r"\breturn\s+.*?;", "return true;", line)

    if "return with false" in d:
        return re.sub(r"\breturn\s+.*?;", "return false;", line)

    if "replaced boolean return with true" in d:
        return re.sub(r"\breturn\s+.*?;", "return true;", line)

    if "replaced boolean return with false" in d:
        return re.sub(r"\breturn\s+.*?;", "return false;", line)

    if "replaced object return with null" in d:
        return re.sub(r"\breturn\s+.*?;", "return null;", line)

    return None


def apply_mutation_with_javalang(java_code, line_number, mutator, description):
    """
    Main mutation function.

    Uses javalang tokenization to identify Java operators on the exact PIT line.
    Then rewrites only the targeted source line.
    """
    lines = java_code.splitlines(keepends=True)

    if line_number < 1 or line_number > len(lines):
        return None

    original_line = lines[line_number - 1]

    tokens = safe_tokenize(java_code)
    line_tokens = get_tokens_on_line(tokens, line_number)

    m = mutator.lower()
    d = description.lower()

    mutated_line = None

    if "conditionalsboundary" in m:
        mapping = {
            "<=": "<",
            "<": "<=",
            ">=": ">",
            ">": ">=",
        }
        mutated_line = replace_first_matching_operator(
            original_line, line_tokens, mapping
        )

    elif "negateconditional" in m:
        mapping = {
            "==": "!=",
            "!=": "==",
            "<=": ">",
            ">=": "<",
            "<": ">=",
            ">": "<=",
        }
        mutated_line = replace_first_matching_operator(
            original_line, line_tokens, mapping
        )

    elif "math" in m:
        mapping = get_math_mapping_from_description(description)

        if mapping:
            mutated_line = replace_first_matching_operator(
                original_line, line_tokens, mapping
            )

    elif "increments" in m:
        if "1 to -1" in d:
            mapping = {
                "++": "--",
                "+=": "-=",
            }
            mutated_line = replace_first_matching_operator(
                original_line, line_tokens, mapping
            )

        elif "-1 to 1" in d:
            mapping = {
                "--": "++",
                "-=": "+=",
            }
            mutated_line = replace_first_matching_operator(
                original_line, line_tokens, mapping
            )

        if mutated_line is None:
            if "++" in original_line:
                mutated_line = original_line.replace("++", "--", 1)
            elif "--" in original_line:
                mutated_line = original_line.replace("--", "++", 1)

    elif "removeconditional" in m:
        mutated_line = mutate_remove_conditional(original_line, description)

    elif (
        "returnvals" in m
        or "primitivereturns" in m
        or "emptyreturns" in m
        or "nullreturns" in m
        or "truereturns" in m
        or "falsereturns" in m
    ):
        mutated_line = mutate_return_value(original_line, description)

    elif "voidmethodcall" in m:
        stripped = original_line.strip()

        if stripped.endswith(";") and "(" in stripped and ")" in stripped:
            indentation = original_line[
                : len(original_line) - len(original_line.lstrip())
            ]
            newline = "\n" if original_line.endswith("\n") else ""
            mutated_line = indentation + "// PIT mutation removed method call" + newline

    elif "nonvoidmethodcall" in m:
        if "=" in original_line and "(" in original_line and ")" in original_line:
            left_side = original_line.split("=", 1)[0]

            if "boolean" in original_line:
                mutated_line = left_side + "= false;\n"
            elif "double" in original_line or "float" in original_line:
                mutated_line = left_side + "= 0.0;\n"
            elif (
                "int" in original_line
                or "long" in original_line
                or "short" in original_line
                or "byte" in original_line
            ):
                mutated_line = left_side + "= 0;\n"
            else:
                mutated_line = left_side + "= null;\n"

    if mutated_line is None:
        return None

    if mutated_line == original_line:
        return None

    mutated_lines = lines.copy()
    mutated_lines[line_number - 1] = mutated_line

    return "".join(mutated_lines), original_line, mutated_line


def make_safe_filename(text):
    """
    Make class/file names safe for output filenames.
    """
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", text)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 MutationApplier.py <project-root> <mutations.xml>")
        print("Example:")
        print(
            "python3 MutationApplier.py . ./commons-numbers-arrays/target/pit-reports/mutations.xml"
        )
        sys.exit(1)

    project_root = sys.argv[1]
    xml_path = sys.argv[2]

    module_name = get_module_name_from_xml_path(xml_path)

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Failed to parse XML: {e}")
        sys.exit(1)

    mutations = root.findall(".//mutation")
    print(f"Module: {module_name}")
    print(f"XML: {xml_path}")
    print(f"Total mutations found: {len(mutations)}")

    output_dir = os.path.join("mutated_output", module_name)
    os.makedirs(output_dir, exist_ok=True)

    applied = 0
    skipped = 0

    for i, mutation in enumerate(mutations):
        status = mutation.get("status", "")
        detected = mutation.get("detected", "")

        source_file = mutation.findtext("sourceFile", default="").strip()
        mutated_class = mutation.findtext("mutatedClass", default="").strip()
        mutated_method = mutation.findtext("mutatedMethod", default="").strip()
        line_number_str = mutation.findtext("lineNumber", default="").strip()
        mutator = mutation.findtext("mutator", default="").strip()
        description = mutation.findtext("description", default="").strip()

        try:
            line_number = int(line_number_str)
        except ValueError:
            print(f"\nSKIP mutation #{i + 1}: invalid line number '{line_number_str}'")
            skipped += 1
            continue

        source_path = find_source_file(
            project_root, source_file, preferred_module=module_name
        )

        if not source_path:
            print(f"\nSKIP mutation #{i + 1}: source file not found: {source_file}")
            skipped += 1
            continue

        print(f"\n--- Mutation #{i + 1} ---")
        print(f"Status:      {status}")
        print(f"Detected:    {detected}")
        print(f"Module:      {module_name}")
        print(f"Class:       {mutated_class}")
        print(f"File:        {source_file}")
        print(f"Method:      {mutated_method}")
        print(f"Line:        {line_number}")
        print(f"Mutator:     {mutator}")
        print(f"Description: {description}")

        try:
            with open(source_path, "r", encoding="utf-8") as f:
                java_code = f.read()
        except Exception as e:
            print(f"SKIP: could not read source file: {e}")
            skipped += 1
            continue

        parsed_tree = safe_parse(java_code)

        if parsed_tree is None:
            print(
                "Warning: javalang could not fully parse this file, but token-based mutation will still be attempted."
            )

        result = apply_mutation_with_javalang(
            java_code=java_code,
            line_number=line_number,
            mutator=mutator,
            description=description,
        )

        if result is None:
            print(
                "SKIP: could not apply mutation automatically with javalang/token logic."
            )
            skipped += 1
            continue

        mutated_code, original_line, mutated_line = result

        print(f"Original:    {original_line.strip()}")
        print(f"Mutated:     {mutated_line.strip()}")

        base_name = make_safe_filename(source_file.replace(".java", ""))
        class_name = make_safe_filename(
            mutated_class if mutated_class else "unknownClass"
        )
        method_name = make_safe_filename(
            mutated_method if mutated_method else "unknownMethod"
        )

        output_filename = (
            f"{class_name}_{base_name}_{method_name}_L{line_number}_M{i + 1}.java"
        )
        output_path = os.path.join(output_dir, output_filename)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(mutated_code)

            print(f"Written to:  {output_path}")
            applied += 1

        except Exception as e:
            print(f"SKIP: failed to write mutated file: {e}")
            skipped += 1

    print("\n=============================")
    print(f"Module:  {module_name}")
    print(f"Applied: {applied} mutations")
    print(f"Skipped: {skipped} mutations")
    print(f"Output:  {output_dir}")
    print("=============================")


if __name__ == "__main__":
    main()
