import os
import shutil
import sys
from glob import glob

import sphinx_gallery.gen_gallery



HERE = os.path.realpath(os.path.dirname(__file__))


class AttrDict(dict):
    def __init__(self):
        super().__init__()
        self.__dict__ = self


from sphinx_gallery.scrapers import figure_rst
class ChemiscopeScraper(object):
    def __init__(self):
        self.seen = set()

    def __repr__(self):
        return 'ChemiscopeScraper'

    def __call__(self, block, block_vars, gallery_conf):
        # Find all chemiscope files (compressed json) in the directory of this example.
        path_current_example = os.path.dirname(block_vars['src_file'])
        cs_files = sorted(glob(os.path.join(path_current_example, '*.json.gz')))

        print("FOUND ", cs_files)
        # Iterate through chsmiscope files, copy them to the sphinx-gallery output directory
        rst_string = ""
        gallery_dir = gallery_conf['gallery_dirs']
        print("GALLERY ", gallery_dir)
        for cs in cs_files:
            if cs not in self.seen:
                self.seen |= set(cs)
                print(list(block_vars.keys()))
                this_path = os.path.join(gallery_dir, os.path.basename(cs))
                print("file ", cs)
                shutil.move(cs, this_path)
                print("moving to ", this_path)
                rst_string += f"""
.. note::
    You can download the example data file here: 
    :download:`{cs} <{this_path}>`.

"""
        return rst_string

class PseudoSphinxApp:
    """
    Class pretending to be a sphinx App, used to configure and run sphinx-gallery
    from the command line, without having an actual sphinx project.
    """

    def __init__(self, example):
        gallery_dir = os.path.join(
            HERE, "docs", "src", "examples", os.path.basename(example)
        )
        if os.path.exists(gallery_dir):
            shutil.rmtree(gallery_dir)

        # the options here are the minimal set of options to get sphinx-gallery to run
        # feel free to add more if sphinx-gallery uses more options in the future
        self.config = AttrDict()
        self.config.html_static_path = []
        self.config.source_suffix = [".rst"]
        self.config.default_role = ""
        self.config.sphinx_gallery_conf = {
            "filename_pattern": ".*",
            "examples_dirs": os.path.join(HERE, example),
            "gallery_dirs": gallery_dir,
            "min_reported_time": 60,
            "copyfile_regex": r".*\.(sh|xyz|cp2k|json|json.gz)",
            "matplotlib_animations": True,
            'image_scrapers': ('matplotlib', ChemiscopeScraper()),
        }

        self.builder = AttrDict()
        self.builder.srcdir = os.path.join(HERE, "docs", "src")
        self.builder.outdir = ""
        self.builder.name = os.path.basename(example)

        self.extensions = []

        self.builder.config = AttrDict()
        self.builder.config.plot_gallery = "True"
        self.builder.config.abort_on_example_error = True
        self.builder.config.highlight_language = None

    def add_css_file(self, path):
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <example/dir>")
        sys.exit(1)

    app = PseudoSphinxApp(example=sys.argv[1])

    sphinx_gallery.gen_gallery.fill_gallery_conf_defaults(app, app.config)
    sphinx_gallery.gen_gallery.update_gallery_conf_builder_inited(app)
    sphinx_gallery.gen_gallery.generate_gallery_rst(app)
