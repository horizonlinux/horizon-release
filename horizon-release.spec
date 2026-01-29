%global distro          Horizon
%define release_type    stable
%global major           10
%global minor           0

Name:           horizon-release
Version:        %{major}.%{minor}
Release:        19%{?dist}
Summary:        %{distro} release files
License:        GPL-2.0-or-later
URL:            https://github.com/horizonlinux/horizon-release
BuildArch:      noarch

Provides:       centos-release = %{version}-%{release}
Provides:       centos-stream-release = %{version}-%{release}

# When running a compose for ELN, we want to make sure that we pull in the
# correct templates when lorax is installed. This Suggests: will clue
# libdnf to use this set of templates instead of lorax-templates-generic.
Suggests: lorax-templates-rhel

# Required for a lorax run (to generate install media)
Requires:       centos-stream-repos(%{major})
Provides:       centos-release-eula
Provides:       redhat-release-eula

# required by epel-release
Provides:       redhat-release = %{version}-%{release}

# required by dnf
# https://github.com/rpm-software-management/dnf/blob/4.2.23/dnf/const.py.in#L26
Provides:       system-release = %{version}-%{release}
Provides:       system-release(releasever) = %{major}
# only have releasever_major, do not add releasever_minor
# https://issues.redhat.com/browse/RHEL-68034
Provides:       system-release(releasever_major) = %{major}
Conflicts:      system-release

# required by libdnf
# https://github.com/rpm-software-management/libdnf/blob/0.48.0/libdnf/module/ModulePackage.cpp#L472
Provides:       base-module(platform:el%{major})

Source200:      EULA
Source201:      LICENSE
Source202:      Contributors

Source300:      85-display-manager.preset
Source301:      90-default.preset
Source302:      90-default-user.preset
Source303:      99-default-disable.preset
Source304:      50-redhat.conf

%description
%{distro} release files.

%install
# copy license and contributors doc here for %%license and %%doc macros
mkdir -p ./docs
cp %{SOURCE201} %{SOURCE202} ./docs

# create /etc/system-release and /etc/redhat-release
install -d -m 0755 %{buildroot}%{_sysconfdir}
echo "%{distro}" > %{buildroot}%{_sysconfdir}/centos-release
ln -s centos-release %{buildroot}%{_sysconfdir}/system-release
ln -s centos-release %{buildroot}%{_sysconfdir}/redhat-release

# -------------------------------------------------------------------------
# Definitions for /etc/os-release and for macros in macros.dist.  These
# macros are useful for spec files where distribution-specific identifiers
# are used to customize packages.

# Name of vendor / name of distribution. Typically used to identify where
# the binary comes from in --help or --version messages of programs.
# Examples: gdb.spec, clang.spec
%global dist_vendor Horizon
%global dist_name   %{distro}

# The namespace for purl
# https://github.com/package-url/purl-spec
# for example as in: pkg:rpm/centos/python-setuptools@69.2.0-10.el10?arch=src"
%global dist_purl_namespace horizon

# URL of the homepage of the distribution
# Example: gstreamer1-plugins-base.spec
%global dist_home_url https://horizon.is-a.dev

# Bugzilla / bug reporting URLs shown to users.
# Examples: gcc.spec
%global dist_bug_report_url https://github.com/horizonlinux/horizon/issues
# -------------------------------------------------------------------------


# Create the os-release file
install -d -m 0755 %{buildroot}%{_prefix}/lib
cat > %{buildroot}%{_prefix}/lib/os-release << EOF
NAME="%{dist_name}"
VERSION="Based on CentOS %{major} (%{release_name})"
RELEASE_TYPE=%{release_type}
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="%{major}"
PLATFORM_ID="platform:el%{major}"
PRETTY_NAME="%{distro}"
ANSI_COLOR="0;31"
LOGO="fedora-logo-icon"
CPE_NAME="cpe:/o:horizon:horizon"
HOME_URL="%{dist_home_url}"
VENDOR_NAME="Horizon"
VENDOR_URL="%{dist_home_url}"
BUG_REPORT_URL="%{dist_bug_report_url}"
REDHAT_SUPPORT_PRODUCT="Red Hat Enterprise Linux %{major}"
REDHAT_SUPPORT_PRODUCT_VERSION="%{distro}"
EOF

# Create the symlink for /etc/os-release
ln -s ../usr/lib/os-release %{buildroot}%{_sysconfdir}/os-release

# write cpe to /etc/system/release-cpe
echo "cpe:/o:horizon:horizon" > %{buildroot}%{_sysconfdir}/system-release-cpe

# create /etc/issue, /etc/issue.net and /etc/issue.d
echo '\S' > %{buildroot}%{_sysconfdir}/issue
echo 'Kernel \r on \m' >> %{buildroot}%{_sysconfdir}/issue
cp %{buildroot}%{_sysconfdir}/issue{,.net}
echo >> %{buildroot}%{_sysconfdir}/issue
mkdir -p %{buildroot}%{_sysconfdir}/issue.d

# set up the dist tag macros
mkdir -p %{buildroot}%{_rpmmacrodir}
cat > %{buildroot}%{_rpmmacrodir}/macros.dist << EOF
# dist macros.

%%__bootstrap ~bootstrap
%%centos_ver %{major}
%%centos %{major}
%%rhel %{major}
%%el%{major} 1
%%distcore            .el%{major}
%%dist %%{!?distprefix0:%%{?distprefix}}%%{expand:%%{lua:for i=0,9999 do print("%%{?distprefix" .. i .."}") end}}%%{distcore}%%{?distsuffix}%%{?with_bootstrap:%{__bootstrap}}
%%dist_vendor         %{dist_vendor}
%%dist_name           %{dist_name}
%%dist_purl_namespace %{dist_purl_namespace}
%%dist_home_url       %{dist_home_url}
%%dist_bug_report_url %{dist_bug_report_url}
%%dist_debuginfod_url %{dist_debuginfod_url}
EOF

# use unbranded datadir
install -d -m 0755 %{buildroot}%{_datadir}/centos-release
ln -s centos-release %{buildroot}%{_datadir}/redhat-release
install -p -m 0644 %{SOURCE200} %{buildroot}%{_datadir}/centos-release/

# copy systemd presets
install -d -m 0755 %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -d -m 0755 %{buildroot}%{_prefix}/lib/systemd/user-preset
install -p -m 0644 %{SOURCE300} %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -p -m 0644 %{SOURCE301} %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -p -m 0644 %{SOURCE302} %{buildroot}%{_prefix}/lib/systemd/user-preset/

# installing the same file for both system and user presets to set the same behavior for both
install -p -m 0644 %{SOURCE303} %{buildroot}%{_prefix}/lib/systemd/system-preset/
install -p -m 0644 %{SOURCE303} %{buildroot}%{_prefix}/lib/systemd/user-preset/

# copy sysctl presets
mkdir -p %{buildroot}/%{_prefix}/lib/sysctl.d/
install -m 0644 %{SOURCE304} %{buildroot}/%{_prefix}/lib/sysctl.d/

%files
%license docs/LICENSE
%doc docs/Contributors
%{_sysconfdir}/redhat-release
%{_sysconfdir}/system-release
%{_sysconfdir}/centos-release
%config(noreplace) %{_sysconfdir}/os-release
%config %{_sysconfdir}/system-release-cpe
%config(noreplace) %{_sysconfdir}/issue
%config(noreplace) %{_sysconfdir}/issue.net
%dir %{_sysconfdir}/issue.d
%dir %{_sysconfdir}/yum.repos.d
%ghost %{_sysconfdir}/yum.repos.d/redhat.repo
%{_rpmmacrodir}/macros.dist
%{_datadir}/redhat-release
%{_datadir}/centos-release
%{_prefix}/lib/os-release
%{_prefix}/lib/systemd/system-preset/*
%{_prefix}/lib/systemd/user-preset/*
%{_prefix}/lib/sysctl.d/50-redhat.conf

%changelog
* Thu Jan 29 2026 Marcel Mrówka <micro.mail88@gmail.com>
- Create package
