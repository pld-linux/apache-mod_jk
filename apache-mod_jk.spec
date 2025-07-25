# TODO:
# - logrotate file
%define		mod_name	jk
%define		apxs		/usr/sbin/apxs
Summary:	Apache module that handles communication between Tomcat and Apache
Summary(pl.UTF-8):	Moduł Apache'a obsługujący komunikację między Tomcatem a Apachem
Name:		apache-mod_%{mod_name}
Version:	1.2.37
Release:	2
License:	Apache v2.0
Group:		Networking/Daemons/HTTP
Source0:	http://www.apache.org/dist/tomcat/tomcat-connectors/jk/tomcat-connectors-%{version}-src.tar.gz
# Source0-md5:	64c3803477b47c5b7ef7f0e4a416e45e
Source1:	%{name}.conf
Source2:	%{name}-workers.properties
Patch0:		%{name}-apxs.patch
Patch1:		%{name}-libtool.patch
URL:		http://tomcat.apache.org/connectors-doc/
BuildRequires:	apache-devel >= 2.4
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	jpackage-utils
BuildRequires:	libtool
BuildRequires:	perl-base
BuildRequires:	rpmbuild(macros) >= 1.300
Requires:	apache(modules-api) = %{apache_modules_api}
Obsoletes:	apache-mod_jk2
Obsoletes:	jakarta-tomcat-connectors-jk
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
JK is a replacement to the elderly mod_jserv. It was a completely new
Tomcat-Apache plug-in that handles the communication between Tomcat
and Apache.

%description -l pl.UTF-8
JK jest zamiennikiem starego mod_jserv. Jest całkowicie nową wtyczką
Tomcat-Apache obsługującą komunikację między Tomcatem a Apachem.

%prep
%setup -q -n tomcat-connectors-%{version}-src
%patch -P0 -p1
%patch -P1 -p1

%build
cd native
%{__libtoolize}
%{__aclocal}
%{__autoheader}
%{__automake}
%{__autoconf}
%configure \
	--with-apxs=%{apxs}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/conf.d,/var/{lock/mod_jk,log/httpd}}
%{__make} -C native install \
	DESTDIR=$RPM_BUILD_ROOT

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/conf.d/80_mod_jk.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/workers.properties
touch $RPM_BUILD_ROOT/var/log/httpd/mod_jk.log

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f /var/log/httpd/mod_jk.log ]; then
	umask 027
	touch /var/log/httpd/mod_jk.log
	chown root:logs /var/log/httpd/mod_jk.log
fi
%service -q httpd restart

%postun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%doc native/{README.txt,STATUS.txt,TODO.txt} conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/workers.properties
%attr(755,root,root) %{_pkglibdir}/*.so
%attr(770,root,http) /var/lock/mod_jk
%attr(640,root,logs) %ghost /var/log/httpd/mod_jk.log
