"""Integration tests for the sync CLI command."""

import os.path
import shutil
import tempfile
import unittest

from gogitit import cli
from click.testing import CliRunner

class IntegrationFixture(unittest.TestCase):
    """
    A test fixture that creates and cleans up a temporary directory for both
    gogitit output, and it's cache.

    Individual tests can re-use the directory as necessary by utilizing sub-tests.
    """
    def setUp(self):
        self.output_dir = tempfile.mkdtemp(prefix='gogigit-test-output-')
        self.cache_dir = tempfile.mkdtemp(prefix='gogigit-test-cache-')
        print("Temp output_dir = %s" % self.output_dir)
        print("Temp cache_dir = %s" % self.cache_dir)

        # Set to last CliRunner invocation result for use in teardown:
        self.result = None

    def tearDown(self):
        shutil.rmtree(self.output_dir)
        shutil.rmtree(self.cache_dir)

    def write_manifest(self, manifest_str):
        """ Writes a test manifest to output_dir/manifest.yml. Will be cleaned up automatically
        with the directory itself. """
        manifest_path = os.path.join(self.output_dir, 'manifest.yml')
        manifest_file = open(manifest_path, 'w')
        manifest_file.write(manifest_str)
        manifest_file.close()
        return manifest_path

    def debug_result(self, result):
        """ Method to print debug info from the result and show the contents of
        the test output directory. Hack it in when your test is failing, otherwise
        likely not used. """
        print("CLI result exit code: %s" % result.exit_code)
        print("CLI output:\n\n%s" % result.output)
        if result.exc_info:
            import traceback
            exc_type, exc_value, exc_traceback = result.exc_info
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print(''.join('!! ' + line for line in lines))
        print("Output directory contents:\n")
        for root, dirs, files in os.walk(self.output_dir):
            path = root.split(os.sep)
            print("%s %s" % ((len(path) - 1) * '-', os.path.basename(root)))
            for file in files:
                print("%s %s" % (len(path) * '-', file))


class SyncTests(IntegrationFixture):

    def _run_sync(self, manifest):
        manifest_path = self.write_manifest(manifest)
        runner = CliRunner()
        result = runner.invoke(cli.main, ['sync', '-m', manifest_path, "-o", self.output_dir])
        self.debug_result(result)
        return result

    def _assert_exists(self, output_path, exists=True):
        if exists:
            self.assertTrue(os.path.exists(os.path.join(self.output_dir,
                output_path)), "%s does not exist" % output_path)
        else:
            self.assertFalse(os.path.exists(os.path.join(self.output_dir,
                output_path)), "%s exists" % output_path)

    def test_file_from_tag(self):
        """ Copy single file from git tag. """
        manifest = build_manifest_str('v0.2', [('playbooks/playbook1.yml', 'playbook1.yml')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('playbook1.yml')

    def test_dir_from_tag(self):
        """ Copy directory from git tag. """
        manifest = build_manifest_str('v0.2', [('roles/', 'roles')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml')

    def test_dir_from_branch(self):
        """ Copy directory from git branch. """
        manifest = build_manifest_str('master', [('roles/', 'roles')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml')

    def test_dir_from_branch_trailing_dst_slash(self):
        """
        Copy directory from git tag with trailing dst slash.

        This one is a bit tricky but I expect we will see this as such.
        """
        manifest = build_manifest_str('master', [('roles/', 'roles/')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml')

    def test_dir_top_level_dst(self):
        """
        Copy directory from git tag to top level at dst.
        """
        manifest = build_manifest_str('master', [('roles', '')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml')

    def test_wildcard_dir(self):
        """ Copy directory from git branch with wildcard. """
        manifest = build_manifest_str('master', [('roles/*', 'roles')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml')

    def test_wildcard_dir_dst_slash(self):
        """ Copy directory from git branch with wildcard and trailing dst slash. """
        manifest = build_manifest_str('v0.2', [('roles/*', 'roles/')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml')

    def test_subdir(self):
        """ Copy sub-directory from git branch. """
        manifest = build_manifest_str('master', [('roles/dummyrole1', 'roles')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml', False)

    def test_subdir_dst_slash(self):
        """ Copy sub-directory from git branch with trailing dst slash. """
        manifest = build_manifest_str('master', [('roles/dummyrole1', 'roles/')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml', False)


def build_manifest_str(version, src_dest_pairs):
    """ Build a manifest string from given git version (commit, branch, or tag)
    and src/dst tuple pairs. """
    base = """---
repos:
- id: testrepo
  url: https://github.com/dgoodwin/gogitit-test.git
  version: %s
  copy:""" % version
    for src, dst in src_dest_pairs:
        base += """
  - src: %s
    dst: %s""" % (src, dst)
    return base
