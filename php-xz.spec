#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	xz
Summary:	PHP Extension providing xz (LZMA2) compression/decompression via PHP streams
Name:		%{php_name}-pecl-%{modname}
Version:	0.1
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://github.com/payden/php-xz/archive/master/php-%{modname}-%{version}.tar.gz
# Source0-md5:	2a110f97e3646f61ce81c66d8ef77a35
URL:		https://github.com/payden/php-xz
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel
BuildRequires:	rpmbuild(macros) >= 1.666
BuildRequires:	xz-devel
%if %{with tests}
BuildRequires:	%{php_name}-cli
%endif
%{?requires_php_extension}
Provides:	php(xz) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PHP Extension providing xz (LZMA2) compression/decompression via PHP
streams.

%prep
%setup -qc
mv php-%{modname}-*/* .

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="" \
	PHP_EXECUTABLE=%{__php}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
