%global release_name Denali
# If you're not building this on Fedora, you're going to have a bad day.... but whatever.
%if 0%{?fedora}
%global dist_version %{fedora}
%else
%global dist_version 41
%endif

%global horizon_codename Denali

Summary:	Horizon Denali relase files
Name:		horizon-release
Version:	%{dist_version}
Release:	denali-f41
License:	MIT
Source0:	LICENSE
Source1:	README.developers
Source2:	README.Horizon-Release-Notes
Source3:	README.license

Source6:	85-display-manager.preset
Source7:	90-default.preset
Source8:	99-default-disable.preset
Source9:	90-default-user.preset

BuildArch: noarch

Provides: horizon-release = %{version}-%{release}
Provides: horizon-release-variant = %{version}-%{release}
Provides: horizon-release-identity = %{version}-%{release}

# We need to Provides: and Conflicts: system release here and in each
# of the horizon-release-$VARIANT subpackages to ensure that only one
# may be installed on the system at a time.
Conflicts: system-release
Provides: system-release
Provides: system-release(%{version})
Conflicts:	fedora-release
Conflicts:	fedora-release-identity
Requires: horizon-release-common = %{version}-%{release}

%description
Horizon release files such as yum configs and various /etc/ files that
define the release. This package explicitly is a replacement for the 
trademarked release package, if you are unable for any reason to abide by the 
trademark restrictions on that release package.


%package common
Summary: Horizon release files

Requires:   horizon-release-variant = %{version}-%{release}
Suggests:   horizon-release

Obsoletes:  horizon-release < 30-0.1

Obsoletes:  convert-to-edition < 30-0.7
Requires:   fedora-repos(%{version})

Conflicts: fedora-release-common

%description common
Release files common to all Horizon Editions


%package notes
Summary:	Release Notes
License:	Open Publication
Provides:	system-release-notes = %{version}-%{release}
Conflicts:	fedora-release-notes

%description notes
Horizon release notes package.
%prep

%build

%install
install -d %{buildroot}%{_prefix}/lib
echo "Horizon %{horizon_codename} based on Fedora %{version}" > %{buildroot}%{_prefix}/lib/fedora-release
echo "cpe:/o:horizon:%{horizon_codename}:f%{version}" > %{buildroot}%{_prefix}/lib/system-release-cpe

# Symlink the -release files
install -d %{buildroot}%{_sysconfdir}
ln -s ../usr/lib/fedora-release %{buildroot}%{_sysconfdir}/fedora-release
ln -s ../usr/lib/system-release-cpe %{buildroot}%{_sysconfdir}/system-release-cpe
ln -s fedora-release %{buildroot}%{_sysconfdir}/redhat-release
ln -s fedora-release %{buildroot}%{_sysconfdir}/system-release

# Create the common os-release file
install -d $RPM_BUILD_ROOT/usr/lib/os.release.d/
cat << EOF >>%{buildroot}%{_prefix}/lib/os-release
NAME=Horizon
VERSION="%{horizon_codename}"
ID=horizon
ID_LIKE=fedora
VERSION_ID=%{dist_version}
PRETTY_NAME="Horizon %{horizon_codename}"
ANSI_COLOR="0;34"
LOGO=fedora-logo-icon
CPE_NAME="cpe:/o:horizon:%{horizon_codename}:f%{version}"
HOME_URL="https://github.com/horizonlinux"
#SUPPORT_URL="https://en.wikipedia.org/wiki/Help!_(album)"
#BUG_REPORT_URL="https://youtu.be/CSemARaqGqE"
REDHAT_BUGZILLA_PRODUCT="Horizon"
REDHAT_BUGZILLA_PRODUCT_VERSION=%{bug_version}
REDHAT_SUPPORT_PRODUCT="Horizon"
REDHAT_SUPPORT_PRODUCT_VERSION=%{bug_version}
EOF

# Create the common /etc/issue
echo "\S" > %{buildroot}%{_prefix}/lib/issue
echo "Kernel \r on an \m (\l)" >> %{buildroot}%{_prefix}/lib/issue
echo >> %{buildroot}%{_prefix}/lib/issue
ln -s ../usr/lib/issue %{buildroot}%{_sysconfdir}/issue

# Create /etc/issue.net
echo "\S" > %{buildroot}%{_prefix}/lib/issue.net
echo "Kernel \r on an \m (\l)" >> %{buildroot}%{_prefix}/lib/issue.net
ln -s ../usr/lib/issue.net %{buildroot}%{_sysconfdir}/issue.net

# Create os-release and issue files for the different editions here
# There are no separate editions for generic-release

# Create the symlink for /etc/os-release
ln -s ../usr/lib/os-release $RPM_BUILD_ROOT/etc/os-release

# Set up the dist tag macros
install -d -m 755 $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d
cat >> $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/macros.dist << EOF
# dist macros.

%%fedora                %{dist_version}
%%dist                %%{?distprefix}.fc%{dist_version}%%{?with_bootstrap:~bootstrap}
%%fc%{dist_version}                1
EOF

# Install readme
mkdir -p readme
install -pm 0644 %{SOURCE3} readme/README.Horizon-Release-Notes

# Install licenses
mkdir -p licenses
install -pm 0644 %{SOURCE0} licenses/LICENSE
install -pm 0644 %{SOURCE2} licenses/README.license

# Add presets
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/user-preset/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/

# Default system wide
install -Dm0644 %{SOURCE6} -t $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %{SOURCE7} -t $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %{SOURCE8} -t $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system-preset/
install -Dm0644 %{SOURCE9} -t $RPM_BUILD_ROOT%{_prefix}/lib/systemd/user-preset/


%files common
%license licenses/LICENSE licenses/README.license
%{_prefix}/lib/fedora-release
%{_prefix}/lib/system-release-cpe
%{_sysconfdir}/os-release
%{_sysconfdir}/fedora-release
%{_sysconfdir}/redhat-release
%{_sysconfdir}/system-release
%{_sysconfdir}/system-release-cpe
%attr(0644,root,root) %{_prefix}/lib/issue
%config(noreplace) %{_sysconfdir}/issue
%attr(0644,root,root) %{_prefix}/lib/issue.net
%config(noreplace) %{_sysconfdir}/issue.net
%attr(0644,root,root) %{_rpmconfigdir}/macros.d/macros.dist
%dir %{_prefix}/lib/systemd/user-preset/
%{_prefix}/lib/systemd/user-preset/90-default-user.preset
%dir %{_prefix}/lib/systemd/system-preset/
%{_prefix}/lib/systemd/system-preset/85-display-manager.preset
%{_prefix}/lib/systemd/system-preset/90-default.preset
%{_prefix}/lib/systemd/system-preset/99-default-disable.preset


%files
%{_prefix}/lib/os-release


%files notes
%doc readme/README.Horizon-Release-Notes


%changelog
* Sun Feb 02 2025 Marcel Mrówka <micro.mail88@gmail.com>
- create horizon-release package
