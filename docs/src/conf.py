from datetime import datetime


# Add any Sphinx extension module names here, as strings.
extensions = [
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_gallery.load_style",
    "chemiscope.sphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

project = "cosmo-software-cookbook"
copyright = (
    "BSD 3-Clause License, "
    f"Copyright (c) {datetime.now().date().year}, "
    "COSMO software cookbook team"
)

htmlhelp_basename = "COSMO software-cookbook"
html_theme = "furo"


intersphinx_mapping = {
    "ase": ("https://wiki.fysik.dtu.dk/ase/", None),
    "metatensor": ("https://lab-cosmo.github.io/metatensor/latest/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "python": ("https://docs.python.org/3", None),
    "rascaline": ("https://luthaf.fr/rascaline/latest/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
}
