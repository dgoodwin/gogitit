""" Tests for the gogitit check CLI command. """

import os
import os.path

import yaml

import fixture
import gogitit.manifest
from gogitit import cli
from fixture import build_manifest_str


class CheckTests(fixture.IntegrationFixture):

    def _load_status(self):
        status = yaml.load(open(os.path.join(self.output_dir, cli.CACHE_FILE)))
        return status

    def test_no_changes(self):
        manifest = build_manifest_str('v0.2', [('playbooks/playbook1.yml', 'playbook1.yml')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, cli.CACHE_FILE)))
        status = self._load_status()
        self.assertTrue('manifest_sha' in status)

        # This SHA matches the tag for v0.2:
        self.assertEqual('3bc5b2de2dcd73402f968ddbb7d15687fb9d1bb5',
                status['paths'][os.path.join(self.output_dir, 'playbook1.yml')])
        result = self._run_check(manifest)
        self.assertEqual(0, result.exit_code)

    def test_no_cache(self):
        manifest = build_manifest_str('v0.2', [('playbooks/playbook1.yml', 'playbook1.yml')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        os.remove(os.path.join(self.output_dir, cli.CACHE_FILE))

        result = self._run_check(manifest)
        self.assertEqual(gogitit.manifest.CHECK_STATUS_NO_STATUS_FILE, result.exit_code)

    def test_manifest_changed(self):
        manifest = build_manifest_str('v0.2', [('playbooks/playbook1.yml', 'playbook1.yml')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)

        # Modify the manifest:
        manifest = build_manifest_str('master', [('playbooks/playbook1.yml', 'playbook1.yml')])

        result = self._run_check(manifest)
        self.assertEqual(gogitit.manifest.CHECK_STATUS_MANIFEST_CHANGED, result.exit_code)

    def test_sha1_changed(self):
        # When using a branch in manifest, new commits to the branch mean we don't
        # know if we have the latest or not, thus we should require a sync to be sure.
        # When this is not desired, users should use tags or commit SHAs instead.
        manifest = build_manifest_str('master', [('playbooks/playbook1.yml', 'playbook1.yml')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)

        # Edit the last status to appear as if it's an older commit:
        status = self._load_status()
        for k in status['paths']:
            status['paths'][k] = u'3bc5b2de2dcd73402f968ddbb7d15687fb9d1bb5'
        f = open(os.path.join(self.output_dir, cli.CACHE_FILE), 'w')
        f.write(yaml.dump(status))
        f.close()

        result = self._run_check(manifest)
        self.assertEqual(gogitit.manifest.CHECK_STATUS_SHA_CHANGED, result.exit_code)


