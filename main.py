with open("test.txt") as file:
    lines = file.readlines()

header_output = ""
header_filename = ".h"
code_output = ""
code_filename = ".cpp"

code_folder = ""

index = 0
len_lines = len(lines)
text_mode = 0
class_name = ""
class_properties = []
class_constants = []

commands = {}

def command(name):
    def wrapper(func):
        commands[name] = func
        return func
    return wrapper

def run():
    global header_output
    global code_output
    global index
    global text_mode
    while index < len_lines:
        line = lines[index].rstrip()
        lines_split = line.split()
        if len(lines_split) > 0:
            if text_mode:
                if lines_split[0] == "text_end":
                    if text_mode == 2:
                        code_output += '\n'
                    text_mode = 0
                else:
                    if text_mode == 1:
                        header_output += line + '\n'
                    else:
                        code_output += line + '\n'
            else:
                current_command = lines[index].split()[0]
                if current_command in commands:
                    output = commands[current_command](line)
                    if output:
                        header_output += output[0]
                        code_output += output[1]
                else:
                    header_output += f"(Unknown command: {current_command})\n"
                    code_output += f"(Unknown command: {current_command})\n"
        else:
            header_output += '\n'
        index += 1

@command("name")
def cmd_name(line):
    global header_filename
    global code_filename
    global code_folder
    split = line.split()
    filename = split[1]
    code_folder = split[2]

    header_filename_for_copyright = filename.replace("\\", "/").split("/")[-1] + header_filename
    code_filename_for_copyright = filename.replace("\\", "/").split("/")[-1] + code_filename

    header_filename = filename + header_filename
    code_filename = filename + code_filename
    
    output = ""
    output += "/**************************************************************************/\n"
    output += ("/*  " + header_filename_for_copyright).ljust(len(output) - 3) + "*/\n"
    output += "/**************************************************************************/\n"
    output += """/*                         This file is part of:                          */
/*                             GODOT ENGINE                               */
/*                        https://godotengine.org                         */
/**************************************************************************/
/* Copyright (c) 2014-present Godot Engine contributors (see AUTHORS.md). */
/* Copyright (c) 2007-2014 Juan Linietsky, Ariel Manzur.                  */
/*                                                                        */
/* Permission is hereby granted, free of charge, to any person obtaining  */
/* a copy of this software and associated documentation files (the        */
/* "Software"), to deal in the Software without restriction, including    */
/* without limitation the rights to use, copy, modify, merge, publish,    */
/* distribute, sublicense, and/or sell copies of the Software, and to     */
/* permit persons to whom the Software is furnished to do so, subject to  */
/* the following conditions:                                              */
/*                                                                        */
/* The above copyright notice and this permission notice shall be         */
/* included in all copies or substantial portions of the Software.        */
/*                                                                        */
/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,        */
/* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF     */
/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. */
/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY   */
/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,   */
/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE      */
/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                 */
/**************************************************************************/

#pragma once
"""

    header_output = output
    output = ""
    output += "/**************************************************************************/\n"
    output += ("/*  " + code_filename_for_copyright).ljust(len(output) - 3) + "*/\n"
    output += "/**************************************************************************/\n"
    output += """/*                         This file is part of:                          */
/*                             GODOT ENGINE                               */
/*                        https://godotengine.org                         */
/**************************************************************************/
/* Copyright (c) 2014-present Godot Engine contributors (see AUTHORS.md). */
/* Copyright (c) 2007-2014 Juan Linietsky, Ariel Manzur.                  */
/*                                                                        */
/* Permission is hereby granted, free of charge, to any person obtaining  */
/* a copy of this software and associated documentation files (the        */
/* "Software"), to deal in the Software without restriction, including    */
/* without limitation the rights to use, copy, modify, merge, publish,    */
/* distribute, sublicense, and/or sell copies of the Software, and to     */
/* permit persons to whom the Software is furnished to do so, subject to  */
/* the following conditions:                                              */
/*                                                                        */
/* The above copyright notice and this permission notice shall be         */
/* included in all copies or substantial portions of the Software.        */
/*                                                                        */
/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,        */
/* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF     */
/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. */
/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY   */
/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,   */
/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE      */
/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                 */
/**************************************************************************/

"""
    output += "#include \"" + code_folder + header_filename_for_copyright.strip('"') + '"\n\n'
    code_output = output

    return [header_output, code_output]

@command("include")
def cmd_include(line):
    header_name = line.split()[1]
    return ["#include " + header_name + '\n', ""]

@command("class")
def cmd_class(line: str):
    global class_name
    split = line.split()
    class_name = split[1]
    output = "class " + class_name
    base_class = ""
    if len(split) > 2:
        base_class = split[3]
        output += " : public " + base_class
    output += " {\n"
    if base_class:
        output += f"\tGDCLASS({class_name}, {base_class});"
    return [output + '\n', ""]

@command("header_text")
def cmd_text_start(line):
    global text_mode
    text_mode = 1

@command("code_text")
def cmd_text_start(line):
    global text_mode
    text_mode = 2

@command("_bind_methods")
def cmd_bind_methods(line):
    code_output = "void " + class_name + "::_bind_methods() {\n"

    for prop in class_properties:
        code_output += f'\tClassDB::bind_method(D_METHOD("set_{prop[1]}", "{prop[1]}"), &{class_name}::set_{prop[1]});\n'
        code_output += f'\tClassDB::bind_method(D_METHOD("get_{prop[1]}"), &{class_name}::get_{prop[1]});\n\n'

    prop_types = {
        "float": "FLOAT",
        "int": "INT",
        "PackedByteArray": "PACKED_BYTE_ARRAY",
        "PackedInt32Array": "PACKED_INT32_ARRAY",
        "Vector3": "VECTOR3"
    }
    for prop in class_properties:
        code_output += "\tADD_PROPERTY(PropertyInfo(Variant::"
        prop_type = prop[0]
        if prop_type in prop_types:
            code_output += prop_types[prop_type]
        else:
            code_output += f"\n\n(Unknown prop_type for _bind_methods: {prop_type})\n\n"
        code_output += f', "{prop[1]}"), "set_{prop[1]}", "get_{prop[1]}");\n'

    code_output += "\n"

    for const in class_constants:
        code_output += "\tBIND_CONSTANT(" + const + ");\n"

    code_output = code_output.rstrip() + "\n}\n\n"
    return ["""
protected:
	static void _bind_methods();

""", code_output]

@command("prop")
def cmd_prop(line: str):
    global class_properties
    split_parts = line.split(';')
    split = split_parts[0].split()
    prop_type = split[1]
    prop_name = split[2]
    result = [prop_type, prop_name]
    if len(split_parts) > 1:
        result.extend([x.strip() for x in split_parts[1:]])
    class_properties.append(result)
    return ["\t" + split_parts[0][len(split[0])+1:] + ';\n', ""]

@command("enum")
def cmd_enum(line: str):
    global class_constants
    global index
    enum_name = line.split()[1]
    output = "\tenum " + enum_name + " {\n"
    while True:
        index += 1
        line = lines[index].rstrip()
        if line == "enum_end":
            break
        class_constants.append(line)
        output += "\t\t" + line + ",\n"
    output += "\t};\n\n"
    return [output, ""]

@command("class_end")
def class_end(line):
    global class_properties
    global class_constants

    header_output = ""
    for prop in class_properties:
        parameter = f"{prop[0]} p_{prop[1]}"
        if prop[0] not in ["int", "float"]:
            parameter = f"const {prop[0]} &p_{prop[1]}"
        header_output += f"\tvoid set_{prop[1]}({parameter});\n"
        header_output += f"\t{prop[0]} get_{prop[1]}() const;\n\n"
    header_output = header_output.rstrip() + "\n};\n"

    code_output = ""
    for prop in class_properties:
        parameter = f"{prop[0]} p_{prop[1]}"
        if prop[0] not in ["int", "float"]:
            parameter = f"const {prop[0]} &p_{prop[1]}"
        code_output += f"void {class_name}::set_{prop[1]}({parameter}) " + "{\n"
        if len(prop) == 2:
            code_output += f"\t{prop[1]} = p_{prop[1]};\n"
        elif len(prop) == 3 and prop[2] == "rad":
            code_output += f"\t{prop[1]} = Math::fmod(p_{prop[1]}, (float)Math::TAU);\n"
            code_output += f"\tif ({prop[1]} < 0.0f) " + "{\n"
            code_output += f"\t\t{prop[1]} += (float)Math::TAU;\n"
            code_output += "\t}\n"
        elif len(prop) == 4:
            if prop[0] == "float" or prop[0] == "int":
                code_output += f"\t{prop[1]} = CLAMP(p_{prop[1]}, {prop[2]}, {prop[3]});\n"
            elif prop[0] == "Vector3":
                code_output += f"\t{prop[1]} = p_{prop[1]}.clampf({prop[2]}, {prop[3]});\n"
            else:
                code_output += f"\n\n(Unknown type for clamp: {prop[0]})\n\n"
        else:
            code_output += f"\n\n(Unknown prop parameters for prop {prop[1]})\n\n"
        code_output += "}\n\n"

        code_output += f"{prop[0]} {class_name}::get_{prop[1]}() const " + "{\n"
        code_output += f"\treturn {prop[1]};\n"
        code_output += "}\n\n"

    code_output += "///////////////////////////////////\n\n"

    class_properties = []
    class_constants = []

    return [header_output, code_output]
    

run()

with open(header_filename, "w") as file:
    file.write(header_output)

with open(code_filename, "w") as file:
    file.write(code_output.rstrip() + '\n')