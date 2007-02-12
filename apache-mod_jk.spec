# TODO:
# - logrotate file
%define		mod_name	jk
%define		apxs		/usr/sbin/apxs
Summary:	Apache module that handles communication between Tomcat and Apache
Summary(pl.UTF-8):   Moduł Apache'a obsługujący komunikację między Tomcatem a Apachem
Name:		apache-mod_%{mod_name}
Version:	1.2.20
Release:	0.1
License:	Apache License 2.0
Group:		Networking/Daemons
Source0: 	http://www.apache.org/dist/tomcat/tomcat-connectors/jk/source/jk-%{version}/tomcat-connectors-%{version}-src.tar.gz
# Source0-md5:	f10709339009b3be9398d3a838d9cabd
Source1:	%{name}.conf
Patch0:		%{name}-libtool.patch
Patch1:		%{name}-apxs.patch
URL:		http://tomcat.apache.org/connectors-doc/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.2.0-6.8
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	perl-base
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	apache(modules-api) = %{apache_modules_api}
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
#%patch0 -p1
%patch1 -p1

%build
cd native
%{__libtoolize}
%{__aclocal}
%{__autoheader}
%{__automake}
%{__autoconf}
%configure \
	--with-apxs=%{apxs} \
	--with-java-home="${JAVA_HOME:-%{_libdir}/java}"
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/httpd.conf,/var/{lock/mod_jk,log/httpd}}

%{__make} -C native install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/80_mod_jk.conf
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
%doc native/{README,CHANGES,NEWS}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*.so
%attr(770,root,http) /var/lock/mod_jk
%attr(640,root,logs) %ghost /var/log/httpd/mod_jk.log
