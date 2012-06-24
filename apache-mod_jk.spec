# TODO:
# - logrotate file
%define		mod_name	jk
%define		apxs		/usr/sbin/apxs
Summary:	Apache module that handles communication between Tomcat and Apache
Summary(pl):	Modu� Apache'a obs�uguj�cy komunikacj� mi�dzy Tomcatem a Apachem
Name:		apache-mod_%{mod_name}
Version:	1.2.15
Release:	0.1
License:	Apache License 2.0
Group:		Networking/Daemons
Source0:	http://www.apache.org/dist/tomcat/tomcat-connectors/jk/source/jk-%{version}/jakarta-tomcat-connectors-%{version}-src.tar.gz
# Source0-md5:	b815a666329f7de097775113547539e0
Source1:	%{name}.conf
Patch0:		%{name}-libtool.patch
URL:		http://tomcat.apache.org/connectors-doc/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.2.0-6.8
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	perl-base
BuildRequires:	rpmbuild(macros) >= 1.120
Requires:	apache(modules-api) = %{apache_modules_api}
Obsoletes:	jakarta-tomcat-connectors-jk
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
JK is a replacement to the elderly mod_jserv. It was a completely new
Tomcat-Apache plug-in that handles the communication between Tomcat
and Apache.

%description -l pl
JK jest zamiennikiem starego mod_jserv. Jest ca�kowicie now� wtyczk�
Tomcat-Apache obs�uguj�c� komunikacj� mi�dzy Tomcatem a Apachem.

%prep
%setup -q -n jakarta-tomcat-connectors-%{version}-src
%patch0 -p1

%build
cd jk/native
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
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/httpd.conf,/var/{lock/mod_jk,log/httpd}}

%{__make} -C jk/native install \
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
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc jk/native/{README,CHANGES}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*.so
%attr(770,root,http) /var/lock/mod_jk
%attr(640,root,logs) %ghost /var/log/httpd/mod_jk.log
