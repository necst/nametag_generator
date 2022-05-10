import sys
import os
import re
import copy

#############################
#############################

CSV_SEPARATOR = ','
PLACEHOLDER_NAME = "Marco Domenico"
PLACEHOLDER_LASTNAME = "Santambrogio"
PLACEHOLDER_AFFILIATION = "Politecnico di Milano"
DEFAULT_TEMPLATE_TAG = './templates/template_tag_hackaton_necstcamp.svg'
DEFAULT_EMPTY_TEMPLATE_TAG = './templates/template_tag_hackaton_necstcamp_empty.svg'
TAGS_DIR = "./tags"
OUTPUT_DIR = "./generated"

# Extra empty tags to print
NUM_EMPTY_TAGS = 2

float_pattern = '(?:\d*\.\d+|\d+)'
font_size_pattern = r'font-size\:' + "(" + float_pattern +")" + r"px"
font_size_nopars_pattern = r'font-size\:' + float_pattern + r"px"

tex_header_str = r"""
\documentclass[11pt,twoside,a4paper]{report}
\usepackage{graphicx}
\usepackage[export]{adjustbox}
\usepackage{geometry}
\geometry{
	a4paper,
	left=10mm,
	right=10mm,
	top=10mm,
	bottom=10mm,
}
\pagestyle{empty}
\usepackage{subfigure}

\begin{document}
"""

badge_height = '87mm'

#############################
#############################

def find_text_tag(lines, text):
    matches = [i for i, s in enumerate(lines) if '>' + text + '<' in s]
    if len(matches) != 1:
        print("found " + str(len(matches)) + " of " + text)
        raise Exception()

    text_pos = matches[0]
    tag_init_pos = -1
    for i in range(text_pos, -1, -1):
        if "<text" in lines[i]:
            tag_init_pos = i
            break

    tag_end_pos = -1
    for i in range(text_pos, len(lines)):
        if '/text>' in lines[i]:
            tag_end_pos = i
            break

    font_attr_matches = [i for i, s in enumerate(lines[tag_init_pos:tag_end_pos + 1]) if 'font-size:' in s]
    if len(font_attr_matches) != 1:
        print("found " + str(len(font_attr_matches)) + " of font size attributes within SVG element")
        raise Exception
    font_attr_pos = font_attr_matches[0] + tag_init_pos

    return text_pos, font_attr_pos


def find_offsets(lines):
    result = [find_text_tag(lines, PLACEHOLDER_NAME),
              find_text_tag(lines, PLACEHOLDER_LASTNAME),
              find_text_tag(lines, PLACEHOLDER_AFFILIATION)]

    return result


def get_font_size(orig_size, orig_string, new_string):
    if len(new_string) == 0:
        return 0

    result = min(orig_size, (orig_size * len(orig_string) / len(new_string)))
    return float(result)

#############################
#############################

if __name__ == "__main__":

    if sys.version_info[0] != 3:
        print("Python version should be 3!")
        sys.exit(-1)

    if len(sys.argv) < 2 or sys.argv[1] == "-h":
        print("\tUSAGE: " + sys.argv[0] + " <semi-colon-separated CSV file>")
        sys.exit(0)

    entries_file = sys.argv[1]
    with open(entries_file) as f, open(DEFAULT_TEMPLATE_TAG) as tag_template:
        template_lines = tag_template.readlines()
        offsets = find_offsets(template_lines)

        # offsets of fields within SVG template
        name_pos = offsets[0][0]
        name_font_pos = offsets[0][1]
        lastname_pos = offsets[1][0]
        lastname_font_pos = offsets[1][1]
        affil_pos = offsets[2][0]
        affil_font_pos = offsets[2][1]

        # prepare objects for computation
        content = f.readlines()
        badge_num = 0
        name_re = re.compile(PLACEHOLDER_NAME)
        lastname_re = re.compile(PLACEHOLDER_LASTNAME)
        affiliation_re = re.compile(PLACEHOLDER_AFFILIATION)
        font_size_re = re.compile(font_size_pattern)
        font_size_nopars_re = re.compile(font_size_nopars_pattern)
        name_font_size_str = font_size_re.search(template_lines[name_font_pos]).group(1)
        name_font_size_value = float(name_font_size_str)
        affil_font_size_str = font_size_re.search(template_lines[affil_font_pos]).group(1)
        affil_font_size_value = float(affil_font_size_str)
        out_files = []

        if not os.path.exists(TAGS_DIR):
            os.makedirs(TAGS_DIR)
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        ######################################
        # Read input and modify tag template #
        ######################################
        
        # for each line in names file
        for line in content:

            # parse each entry
            entry = line
            fields = entry.split(CSV_SEPARATOR)
            name = fields[0].strip() if fields else ""
            lastname = fields[1].strip() if len(fields) > 0 else ""
            affiliation = fields[2].strip() if len(fields) > 1 else ""
            print(name + " - " + lastname + " - " + affiliation)

            svg = copy.deepcopy(template_lines)

            # replace text
            svg[name_pos] = name_re.sub(name, svg[name_pos])
            svg[lastname_pos] = lastname_re.sub(lastname, svg[lastname_pos])
            svg[affil_pos] = affiliation_re.sub(affiliation, svg[affil_pos])

            # compute font sizes
            name_size = get_font_size(name_font_size_value, PLACEHOLDER_NAME, name)
            lastname_size = get_font_size(name_font_size_value, PLACEHOLDER_NAME, lastname)
            name_size = min(name_size, lastname_size)
            lastname_size = name_size
            affiliation_size = get_font_size(affil_font_size_value, PLACEHOLDER_AFFILIATION, affiliation)

            # replace font sizes
            svg[name_font_pos] = font_size_nopars_re.sub('font-size:' + str(name_size) + "px", svg[name_font_pos])
            svg[lastname_font_pos] = font_size_nopars_re.sub('font-size:' + str(lastname_size) + "px", svg[lastname_font_pos])
            svg[affil_font_pos] = font_size_nopars_re.sub('font-size:' + str(affiliation_size) + "px", svg[affil_font_pos])

            # write to file
            with open(TAGS_DIR + "/out_" + str(badge_num) + ".svg", "w") as f:
                f.writelines(svg)
            out_files.append("out_" + str(badge_num))
            badge_num = badge_num + 1
            
        #################################
        # Generate single nametag files #
        #################################
        
        empty_template_tag = os.path.join(TAGS_DIR, os.path.basename(DEFAULT_EMPTY_TEMPLATE_TAG).rstrip('.svg'))
        print(f"cp {DEFAULT_EMPTY_TEMPLATE_TAG} {empty_template_tag}.svg")
        os.system(f"cp {DEFAULT_EMPTY_TEMPLATE_TAG} {empty_template_tag}.svg")

        # convert to PDF via inkscape
        tags_path = os.path.normpath(os.getcwd() + '/' + TAGS_DIR)
        command = "for f in " + tags_path + r'/*.svg; do fn="${f%.svg}"; inkscape -z --file=${f} --export-pdf=${fn}.pdf &> /dev/null; done;'
        print(command)
        os.system(command)
        
        ####################################
        # Generate Tex file and compile it #
        ####################################

        # start from Latex header
        tex_header_lines = [tex_header_str]
        
        out_files += [os.path.basename(DEFAULT_EMPTY_TEMPLATE_TAG).rstrip('.svg')] * NUM_EMPTY_TAGS

        # add Latex figures of PDF files with 90 deg rotation and shrink their height to badge_height
        for i in range(0, len(out_files), 4):
            
            files = out_files[i:i + 4]
            figures = [r'\hspace{0em} \subfigure{ \includegraphics[angle=90,origin=c,frame,height=' +
                       badge_height +']{' + os.path.join("..", TAGS_DIR, f + ".pdf") + '} }' + "\n" for f in files]
            # Pad with empty badges
            if len(files) < 4:
                figures += [r'\hspace{0em} \subfigure{ \includegraphics[angle=90,origin=c,frame,height=' +
                       badge_height +']{' + os.path.join("..", TAGS_DIR, files[0] + ".pdf") + '} }' + "\n"] * (4 - len(files))
    
            tex_header_lines += [r'\begin{figure}' + "\n" + "\centering" + "\n"]
            
            tex_header_lines += figures[0]
            tex_header_lines += r"\hspace{-5mm}"
            tex_header_lines += figures[1]
            tex_header_lines += r"\\ \vspace{-2mm}"
            tex_header_lines += figures[2]
            tex_header_lines += r"\hspace{-5mm}"
            tex_header_lines += figures[3]
            tex_header_lines += ["\end{figure}\n\n"]
        tex_header_lines += ["\end{document}\n\n"]

        # write tex file
        tex_filename = "nametags"
        output_file = os.path.join(OUTPUT_DIR, tex_filename + ".tex")
        with open(output_file, "w") as f:
            f.writelines(tex_header_lines)

        # compile Latex
        for i in range(4):
            os.system(f"cd generated; pdflatex -shell-escape -synctex=1 {tex_filename}.tex &> /dev/null")
