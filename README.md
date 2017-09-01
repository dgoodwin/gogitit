# gogitit

gogigit parses a manifest and assembles an output directory consisting of
portions of multiple remote git repositories and sub-directories within them,
at the refs/tags/heads you specify.

It is effectively a vendoring tool but allows merging into one tree, as this is
helpful when assembling ansible roles and playbooks from many locations. Whether or
not the resulting output directory is commited to git is up to the user. (for now)

It's intended use is for an operations team which needs to consume and run
Ansible roles and playbooks from a variety of other teams. At present however
the solution is generic and not tied to Ansible.

Written in Python, not Go (though it almost was), despite how awesome the
name-play would have been.

## Behavior

  * Specify a manifest listing multiple entries of source git repo,
    sub-directory, revision/branch/tag, destination relative to the output dir.
  * Output directory defaults to current directory if not set.
  * Output directory will be created if it does not exist, it should *never* be
    deleted by this application, the user may do so explicitly if they wish.
  * Output directory will eventually contain a cache tracking the last fetched
    revision for each entry in the manifest.
  * For each entry:
    * Fetch the git repo to temporary location.
    * Handle directories intelligently:
      * Copy a source directory to a destination within output directory.
      * Copy the contents of a source directory to a destination within the
        output directory. (may be merging with other sources)
        * Check for conflicts before doing anything.
    * If source is a file, overwrite.
      * We assume that if you stop tracking a file and remove it from the
        mainfest, the user will be responsible for removing it from a long
        running output directory.
  * Be sure to never copy in nested .git directories.
  * Support multiple sub-directories coming out of one git repo without re-cloning multiple times.
  * Support keeping a cache of git clones in tmp just update them on execution. (much more time/bandwidth efficient)

## Examples

The following examples would be indented beneath the respective "copy" section
of a repo in your manifest.

Copy an entire directory, you must explicitly reference the full destination
directory name. (i.e. you cannot just use dst of 'roles' here and assume myrole
will be the resulting directory) This is to avoid confusion around cleanup when
re-executing sync.

```
- src: roles/myrole
  dst: roles/myrole
```

Copy a specific file, here you do not have to specify the full filename if you
do not wish to rename it. You must however include a trailing slash on the dst,
otherwise we have to assume you wanted to copy to a file named 'playbooks'.

```
- src: playbooks/create.yml
  dst: playbooks/
```

Copy with wildcards:

```
- src: roles/*env*
  dst: roles
```

## Example Manifest

Coming soon. See the [manifest-example.yml](manifest-example.yml) for the work in progress.

# Installation

TBD

Hoping to just distribute as a Python package. rpm via copr is also on the table.

# Hacking

Staying on Python 2 for the time being, need to run on RHEL 7 as well as Fedora.

```
virtualenv venv
. venv/bin/activate
pip install --editable .
```

Optionally check flake8 happiness:

```
pip install flake8
python setup.py flake8
```

