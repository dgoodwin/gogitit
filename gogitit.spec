%global pythonbin %{__python2}
%global python_sitelib %{python2_sitelib}
%{!?python_sitelib: %define python_sitelib %(%{pythonbin} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: gogitit
Version: 0.4
Release: 1
Summary: A tool for fetching files from a number of git repositories and versions.
Source0: gogitit-%{version}.tar.gz

Group: Development/Tools
License: GPLv2
URL: https://github.com/dgoodwin/gogitit

BuildArch: noarch

Requires: python-setuptools
Requires: GitPython
Requires: python-click

# NOTE: should be python3-PyYAML if we got back to Python 3.
Requires: PyYAML

BuildRequires: python2-devel
BuildRequires: python-setuptools

%description
Gogitit is a tool for fetching files and directories from various git
repositories and branches, and assembling them all into an output directory.

%prep
%setup -q -n gogitit-%{version}

%build
%{pythonbin} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{pythonbin} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{python_sitelib}/*egg-info/requires.txt

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{_bindir}/gogitit
%dir %{python_sitelib}/gogitit
%{python_sitelib}/gogitit/*
%{python_sitelib}/gogitit-*.egg-info


%changelog
* Wed Sep 06 2017 Devan Goodwin <dgoodwin@rm-rf.ca> 0.4-1
- Set output dir in manifest by default, override with CLI optionally.
  (dgoodwin@redhat.com)
- Add check command to see if a sync is required. (dgoodwin@redhat.com)
- Do not copy .git directories. (dgoodwin@redhat.com)

* Fri Sep 01 2017 Devan Goodwin <dgoodwin@rm-rf.ca> 0.3-2
- Fix broken setuptools link on RHEL 7. (dgoodwin@redhat.com)

* Fri Sep 01 2017 Devan Goodwin <dgoodwin@rm-rf.ca> 0.3-1
- Drop Python 3 for Python 2 to better support RHEL/CentOS.
  (dgoodwin@redhat.com)

* Fri Sep 01 2017 Devan Goodwin <dgoodwin@rm-rf.ca> 0.2-1
- Require more specific dst when copying dirs. (dgoodwin@redhat.com)

* Wed Aug 30 2017 Devan Goodwin <dgoodwin@rm-rf.ca> 0.1-1
- Initial rpm build and release.

