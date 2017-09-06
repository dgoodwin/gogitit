""" Integration test fixture. """

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

    def _run_check(self, manifest, output_dir=None):
        manifest_path = self.write_manifest(manifest)
        runner = CliRunner()
        args = ['check', '-m', manifest_path,
            "--cache-dir", self.cache_dir]
        if output_dir:
            args = args.extend(["-o", output_dir])
        result = runner.invoke(cli.main, args)
        self.debug_result(result)
        return result

    def _run_sync(self, manifest):
        manifest_path = self.write_manifest(manifest)
        runner = CliRunner()
        result = runner.invoke(cli.main, ['sync', '-m', manifest_path, "-o", self.output_dir,
            "--cache-dir", self.cache_dir])
        self.debug_result(result)
        return result

    def debug_result(self, result):
        """ Method to print debug info from the result and show the contents of
        the test output directory. Hack it in when your test is failing, otherwise
        likely not used. """
        print("CLI result exit code: %s" % result.exit_code)
        print("CLI output:\n\n%s" % result.output)

        if result.exit_code:
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

    def build_manifest_str(self, version, src_dest_pairs):
        """ Build a manifest string from given git version (commit, branch, or tag)
        and src/dst tuple pairs. """
        base = """---
output_dir: ./
repos:
- id: testrepo
  url: https://github.com/dgoodwin/gogitit-test.git
  version: %s
  copy:""" % (version)

        for src, dst in src_dest_pairs:
            base += """
      - src: %s
        dst: %s""" % (src, dst)
        return base


