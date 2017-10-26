""" Unit tests for manifest module. """

import unittest

import gogitit.manifest as manifest

class RepoUrlToCacheDirTests(unittest.TestCase):

    def test_github_https(self):
        self.assertEquals("github.com/openshift/online-archivist",
                manifest.repo_url_to_dir("https://github.com/openshift/online-archivist.git"))

    def test_github_https_trailing_slash(self):
        self.assertEquals("github.com/openshift/online-archivist",
                manifest.repo_url_to_dir("https://github.com/openshift/online-archivist.git/"))

    def test_github_https_no_git_suffix(self):
        self.assertEquals("github.com/openshift/online-archivist",
                manifest.repo_url_to_dir("https://github.com/openshift/online-archivist"))

    def test_github_ssh(self):
        self.assertEquals("github.com/openshift/online-archivist",
                manifest.repo_url_to_dir("git@github.com:openshift/online-archivist.git"))

    def test_https(self):
        self.assertEquals("example.com/gitproject",
                manifest.repo_url_to_dir("https://example.com/gitproject.git"))

    def test_local(self):
        self.assertEquals("srv/git/project",
                manifest.repo_url_to_dir("/srv/git/project.git"))

    def test_local_uri(self):
        self.assertEquals("srv/git/project",
                manifest.repo_url_to_dir("file:///srv/git/project.git"))

    def test_ssh_user(self):
        self.assertEquals("server/project",
                manifest.repo_url_to_dir("ssh://user@server/project.git"))

    def test_ssh(self):
        self.assertEquals("server/project",
                manifest.repo_url_to_dir("ssh://server/project.git"))

    def test_ssh_scp_syntax_user(self):
        self.assertEquals("server/project",
                manifest.repo_url_to_dir("user@server:project.git"))

    def test_ssh_scp_syntax_no_user(self):
        self.assertEquals("server/project",
                manifest.repo_url_to_dir("server:project.git"))
