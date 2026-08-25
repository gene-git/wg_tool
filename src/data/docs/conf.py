#
# src/data/docs/conf.p
#
import os
import sys

#
# package version from version.txt file
#
def read_version() -> str:
    """
    Get package version from version.txt file
    """
    file = '../../version.txt'
    if os.path.exists(file):
        with open(file, 'r') as fob:
            proj_vers = fob.readlines()[0]
    else:
        proj_vers = '0.1.0-unknown'
    return proj_vers

#
# Project
#
project = "wg_tool"
copyright = '2022-present, Gene C'
author = 'Gene C'
release = read_version()

extensions = []
#html_static_path = ['_static']
#html_css_files = ['custom.css']

latex_engine = 'xelatex'
latex_use_xindy = True

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',

    # Protrusion only to prevent XeLaTeX font expansion crashes
    'passoptionstopackages': r'\PassOptionsToPackage{protrusion=true}{microtype}',

    'preamble': r'''
    \usepackage{microtype}
    \usepackage{parskip}
    \usepackage{fontspec}

    \usepackage{newunicodechar}
    \newunicodechar{␣}{\textvisiblespace}
    \tracinglostchars=0

    % Body Serif (Libertine)
    \setmainfont{Libertinus Serif}[
        Ligatures=TeX,
        Numbers=OldStyle
    ]

    % Section Headers (Sans-Serif libertine)
    \setsansfont{Libertinus Sans}[
        Ligatures=TeX
    ]

    % Verbatim/Inline (Monospace libertine)
    % Explicitly mapping it as the primary system typewriter engine (\ttdefault)
    \setmonofont{Libertinus Mono}[
        Scale=0.92,
        AutoFakeSlant=0.2
    ]

    ''',
}

latex_documents = [
    (
        'index',
        'wg-tool.tex',
        'wg-tool Documentation ',
        'Gene C',
        'manual'
    ),
]

