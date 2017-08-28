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


class SyncTests(IntegrationFixture):

    def test_file_master(self):
        manifest = """---
repos:
- id: testrepo
  url: https://github.com/dgoodwin/gogitit-test.git
  version: master
  copy:
  - src: playbooks/playbook1.yml
    dst: playbook1.yml
"""
        manifest_path = self.write_manifest(manifest)
        runner = CliRunner()
        result = runner.invoke(cli.main, ['sync', '-m', manifest_path, "-o", self.output_dir])
        self.assertEqual(0, result.exit_code)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'playbook1.yml')))

    def test_dir_master(self):
        manifest = """---
repos:
- id: testrepo
  url: https://github.com/dgoodwin/gogitit-test.git
  version: master
  copy:
  - src: roles/
    dst: roles
"""
        manifest_path = self.write_manifest(manifest)
        runner = CliRunner()
        result = runner.invoke(cli.main, ['sync', '-m', manifest_path, "-o", self.output_dir])
        self.assertEqual(0, result.exit_code)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'roles/dummyrole1/tasks/main.yml')))

