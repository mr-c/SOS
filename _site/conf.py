# -*- coding: utf-8 -*-

import sys, os

source_suffix = '.md'
master_doc = 'Documentation'

project = u'Script of Scripts'
copyright = u'2016, Bo Peng'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    ]

pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------

html_theme = 'traditional'
html_theme_path = ['themes']
html_title = "Script of Scripts"
#html_short_title = None
#html_logo = None
#html_favicon = None
html_domain_indices = False
html_use_index = False
html_show_sphinx = False

################################################################################


