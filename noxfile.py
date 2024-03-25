import glob
import hashlib
import json
import os

import nox


# global nox options
nox.options.reuse_venv = "yes"
nox.options.sessions = ["lint", "docs"]


# Files that need to be linted & formatted
LINT_FILES = [
    "ipynb-to-gallery.py",
    "generate-gallery.py",
    "noxfile.py",
    "docs/src/conf.py",
    "examples",
]

# the current list of examples, determined from the directories on disk
EXAMPLES = [
    os.path.basename(os.path.normpath(file)) for file in glob.glob("examples/*/")
]

# ==================================================================================== #
#                                 helper functions                                     #
# ==================================================================================== #


def should_reinstall_dependencies(session, **metadata):
    """
    Returns a bool indicating whether the dependencies should be re-installed in the
    venv.

    This works by hashing everything in metadata, and storing the hash in the session
    virtualenv. If the hash changes, we'll have to re-install!
    """

    to_hash = {}
    for key, value in metadata.items():
        if os.path.exists(value):
            with open(value) as fd:
                to_hash[key] = fd.read()
        else:
            to_hash[key] = value

    to_hash = json.dumps(to_hash).encode("utf8")
    sha1 = hashlib.sha1(to_hash).hexdigest()
    sha1_path = os.path.join(session.virtualenv.location, "metadata.sha1")

    if session.virtualenv._reused:
        if os.path.exists(sha1_path):
            with open(sha1_path) as fd:
                should_reinstall = fd.read().strip() != sha1
        else:
            should_reinstall = True
    else:
        should_reinstall = True

    with open(sha1_path, "w") as fd:
        fd.write(sha1)

    if should_reinstall:
        session.debug("updating environment since the dependencies changed")

    return should_reinstall


# ==================================================================================== #
#                              nox sessions definitions                                #
# ==================================================================================== #


for name in EXAMPLES:

    @nox.session(name=name, venv_backend="conda")
    def example(session, name=name):
        environment_yml = f"examples/{name}/environment.yml"
        if should_reinstall_dependencies(session, environment_yml=environment_yml):
            session.run(
                "conda",
                "env",
                "update",
                "--prune",
                f"--file={environment_yml}",
                f"--prefix={session.virtualenv.location}",
            )

            # install sphinx-gallery and its dependencies
            session.install("sphinx-gallery", "sphinx", "pillow", "matplotlib")

        session.run("python", "generate-gallery.py", f"examples/{name}")
        os.unlink(f"docs/src/examples/{name}/index.rst")


@nox.session(venv_backend="none")
def docs(session):
    """Run all examples and build the documentation"""

    for example in EXAMPLES:
        session.run("nox", "-e", example, external=True)
    session.run("nox", "-e", "build_docs", external=True)


@nox.session
def build_docs(session):
    """Assemble the documentation into a website, assuming pre-generated examples"""

    requirements = "docs/requirements.txt"
    if should_reinstall_dependencies(session, requirements=requirements):
        session.install("-r", requirements)

    session.run("sphinx-build", "-W", "-b", "html", "docs/src", "docs/build/html")


@nox.session
def lint(session):
    """Run linters and type checks"""

    if not session.virtualenv._reused:
        session.install("black", "blackdoc")
        session.install("flake8", "flake8-bugbear", "flake8-sphinx-links")
        session.install("isort")
        session.install("sphinx-lint")

    # Formatting
    session.run("black", "--check", "--diff", *LINT_FILES)
    session.run("blackdoc", "--check", "--diff", *LINT_FILES)
    session.run("isort", "--check-only", "--diff", *LINT_FILES)

    # Linting
    session.run(
        "flake8",
        "--max-line-length=88",
        "--exclude=docs/src/examples/",
        *LINT_FILES,
    )

    session.run(
        "sphinx-lint",
        "--enable=line-too-long",
        "--max-line-length=88",
        "--ignore=docs/src",
        "README.rst",
        "CONTRIBUTING.rst",
        *LINT_FILES,
    )


@nox.session
def format(session):
    """Automatically format all files"""

    if not session.virtualenv._reused:
        session.install("black", "blackdoc")
        session.install("isort")

    session.run("black", *LINT_FILES)
    session.run("blackdoc", *LINT_FILES)
    session.run("isort", *LINT_FILES)
