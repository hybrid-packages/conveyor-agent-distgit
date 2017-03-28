%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%global pypi_name conveyoragent

Name:			conveyor-agent
Epoch:			1
Version:		XXX
Release:		XXX
Summary:		ConveyorAgent

License:		ASL 2.0
URL:   			https://github.com/Hybrid-Cloud/conveyor-agent
Source0:		https://github.com/Hybrid-Cloud/%{name}/%{name}-%{upstream_version}.tar.gz

Source1:        conveyoragent.logrotate
Source2:        conveyoragent.sudoers

Source10:       conveyoragent.service

BuildArch:		noarch
BuildRequires:  intltool
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-pbr
BuildRequires:  python-d2to1

%description
ConveyorAgent

%package -n python-%{pypi_name}
Summary:        ConveyorAgent

Requires:       python-babel
Requires:       python-eventlet >= 0.17.4
Requires:       python-greenlet
Requires:       python-iso8601
Requires:       python-oslo-config >= 3.4.0
Requires:       python-oslo-i18n >= 2.1.0
Requires:       python-oslo-serialization >= 2.1.0
Requires:       python-oslo-utils >= 3.4.0
Requires:       python-paste
Requires:       python-pbr
Requires:       python-retrying
Requires:       python-routes
Requires:       python-six >= 1.9.0
Requires:       python-webob >= 1.2.3

%description -n python-%{pypi_name}
ConveyorAgent


%package -n python-%{pypi_name}-tests
Summary:        ConveyorAgent tests
Requires:       python-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n python-%{pypi_name}-tests
ConveyorAgent tests

%prep
%setup -q -n conveyoragent-%{upstream_version}

find . \( -name .gitignore -o -name .placeholder \) -delete

# Let RPM handle the requirements
rm -f {,test-}requirements.txt

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/conveyoragent
install -d -m 750 %{buildroot}%{_localstatedir}/log/conveyoragent
install -d -m 750 %{buildroot}%{_sysconfdir}/conveyoragent

# Install config files
install -p -D -m 755 etc/conveyoragent/hybrid-v2v.conf %{buildroot}%{_sysconfdir}/conveyoragent/conveyoragent.conf
install -p -D -m 755 etc/conveyoragent/api-paste.ini %{buildroot}%{_sysconfdir}/conveyoragent/api-paste.ini

# Install initscripts for conveyoragent services
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/conveyoragent.service

# Install sudoers
install -p -D -m 440 %{SOURCE2} %{buildroot}%{_sysconfdir}/sudoers.d/conveyoragent

# Install logrotate
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/conveyoragent

# Remove unneeded in production stuff
rm -fr %{buildroot}%{python2_sitelib}/run-tests.*

%pre -n python-%{pypi_name}
getent group conveyor >/dev/null || groupadd -r conveyor
if ! getent passwd conveyor >/dev/null; then
    useradd -r -g conveyor -G conveyor -s /sbin/nologin -c "ConveyorAgent Daemons" conveyor
fi
exit 0

%post -n python-%{pypi_name}
%systemd_post conveyoragent

%preun -n python-%{pypi_name}
%systemd_preun conveyoragent

%postun -n python-%{pypi_name}
%systemd_postun_with_restart conveyoragent

%files -n python-%{pypi_name}
%defattr(-,root,root)
%{python2_sitelib}/conveyoragent
%{python2_sitelib}/conveyoragent-*.egg-info
%config(noreplace) %attr(0, conveyor, conveyor) %{_sysconfdir}/conveyoragent/*
%dir %attr(755, conveyor, conveyor) %{_localstatedir}/lib/conveyoragent
%{_bindir}/*
%{_unitdir}/*.service
%config(noreplace) %{_sysconfdir}/logrotate.d/conveyoragent
%config(noreplace) %{_sysconfdir}/sudoers.d/conveyoragent
%dir %attr(0750, conveyor, conveyor) %{_localstatedir}/log/conveyoragent

%files -n python-%{pypi_name}-tests
%license LICENSE
%{python2_sitelib}/conveyoragent/tests

%changelog
