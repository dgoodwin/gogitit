"""Integration tests for the sync CLI command."""

import os.path

import fixture


class SyncTests(fixture.IntegrationFixture):

    def _assert_exists(self, output_path, exists=True, i=1):
        if exists:
            self.assertTrue(os.path.exists(os.path.join(self.output_dir,
                output_path)), "%s does not exist on loop %s" % (output_path, i))
        else:
            self.assertFalse(os.path.exists(os.path.join(self.output_dir,
                output_path)), "%s exists on loop %s" % (output_path, i))

    def test_file_from_tag(self):
        manifest = self.build_manifest_str('v0.2', [('playbooks/playbook1.yml', 'playbook1.yml')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('playbook1.yml')

    def test_file_to_dir(self):
        manifest = self.build_manifest_str('master', [('playbooks/playbook1.yml', 'playbooks/')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('playbooks/playbook1.yml')

    def test_file_to_top_lvl_dir(self):
        manifest = self.build_manifest_str('master', [('playbooks/playbook1.yml', '')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('playbook1.yml')

    def test_file_glob_to_dir(self):
        manifest = self.build_manifest_str('v0.2', [('playbooks/*.yml', 'playbooks/')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('playbooks/playbook1.yml')

    def test_dir_from_tag(self):
        manifest = self.build_manifest_str('v0.2', [('roles/', 'roles')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml')

        # Doesn't exist in v0.2 tag.
        self._assert_exists('roles/dummyrole3/tasks/main.yml', False)

    def test_dir_from_branch(self):
        manifest = self.build_manifest_str('master', [('roles/', 'roles')])
        for i in range(2):
            result = self._run_sync(manifest)
            self.assertEqual(0, result.exit_code)
            self._assert_exists('roles/dummyrole1/tasks/main.yml', i=i)
            self._assert_exists('roles/dummyrole2/tasks/main.yml', i=i)
            self._assert_exists('roles/dummyrole3/tasks/main.yml', i=i)
            self._assert_exists('roles/roles/dummyrole1/tasks/main.yml', False, i=i)

    def test_dir_from_branch_trailing_dst_slash(self):
        manifest = self.build_manifest_str('master', [('roles/', 'roles/')])
        for i in range(2):
            result = self._run_sync(manifest)
            self.assertEqual(0, result.exit_code)
            self._assert_exists('roles/dummyrole1/tasks/main.yml', i=i)
            self._assert_exists('roles/dummyrole2/tasks/main.yml', i=i)

    def test_dir_top_level_dst(self):
        manifest = self.build_manifest_str('master', [('roles', '')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('dummyrole1/tasks/main.yml')
        self._assert_exists('dummyrole2/tasks/main.yml')
        self._assert_exists('roles/dummyrole1/tasks/main.yml', False)
        self._assert_exists('roles/dummyrole2/tasks/main.yml', False)

    def test_glob_dir(self):
        manifest = self.build_manifest_str('master', [('roles/*', 'roles')])
        for i in range(2):
            result = self._run_sync(manifest)
            self.assertEqual(0, result.exit_code)
            self._assert_exists('roles/dummyrole1/tasks/main.yml', i=i)
            self._assert_exists('roles/dummyrole2/tasks/main.yml', i=i)
            self._assert_exists('roles/roles/dummyrole1/tasks/main.yml', False, i=i)
            self._assert_exists('dummyrole1/tasks/main.yml', False, i=i)

    def test_glob_dir_dst_slash(self):
        manifest = self.build_manifest_str('v0.2', [('roles/*', 'roles/')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml')

    def test_subdir(self):
        manifest = self.build_manifest_str('master', [('roles/dummyrole1', 'roles/dummyrole1')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('roles/dummyrole1/tasks/main.yml')
        self._assert_exists('roles/dummyrole2/tasks/main.yml', False)

    def test_top_level_dir(self):
        manifest = self.build_manifest_str('master', [('./', 'vendor/output')])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('vendor/output/roles/dummyrole1/tasks/main.yml')
        self._assert_exists('vendor/output/roles/dummyrole2/tasks/main.yml')
        self._assert_exists('vendor/output/.git', False)

    def test_subdir_dst_slash(self):
        manifest = self.build_manifest_str('master', [('roles/dummyrole1', 'roles/dummyrole1/')])
        result = self._run_sync(manifest)
        for i in range(2):
            self.assertEqual(0, result.exit_code)
            self._assert_exists('roles/dummyrole1/tasks/main.yml', i=i)
            self._assert_exists('roles/dummyrole2/tasks/main.yml', False, i=i)
            self._assert_exists('roles/dummyrole1/dummyrole1/tasks/main.yml', False, i=i)
            self._assert_exists('roles/dummyrole1/roles/dummyrole1/tasks/main.yml', False, i=i)

    def test_dir_rename_dst_exists(self):
        m1 = self.build_manifest_str('master', [('roles', 'roles2')])
        m2 = self.build_manifest_str('master', [('roles', 'roles2/')])
        for manifest in [m1, m2]:
            for i in range(2):
                result = self._run_sync(manifest)
                self.assertEqual(0, result.exit_code)
                self._assert_exists('roles2/dummyrole1/tasks/main.yml', i=i)
                self._assert_exists('roles2/dummyrole2/tasks/main.yml', i=i)
                self._assert_exists('roles2/roles/dummyrole1/tasks/main.yml', False, i=i)
                self._assert_exists('roles2/roles2/dummyrole1/tasks/main.yml', False, i=i)
                self._assert_exists('roles2/roles/dummyrole2/tasks/main.yml', False, i=i)

                # If we run again, make sure we don't nest:
                result = self._run_sync(manifest)
                self.assertEqual(0, result.exit_code)
                self._assert_exists('roles2/dummyrole1/tasks/main.yml', i=i)
                self._assert_exists('roles2/dummyrole2/tasks/main.yml', i=i)
                self._assert_exists('roles2/roles/dummyrole1/tasks/main.yml', False, i=i)
                self._assert_exists('roles2/roles/dummyrole2/tasks/main.yml', False, i=i)

    def test_merge_two_dirs(self):
        manifest = self.build_manifest_str('master', [
            ('roles/', 'merged/'),
            ('playbooks/*', 'merged/'),
        ])
        result = self._run_sync(manifest)
        self.assertEqual(0, result.exit_code)
        self._assert_exists('merged/dummyrole1/tasks/main.yml')
        self._assert_exists('merged/dummyrole2/tasks/main.yml')
        self._assert_exists('merged/playbook1.yml')


