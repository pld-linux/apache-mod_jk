%define 	apxs	/usr/sbin/apxs
Summary:	Apache module that handles communication between Tomcat and Apache
%define		apache_version	1.3.27
%define		mod_name	jk
Name:		apache-mod_%{mod_name}
Version:	1.2.1
Release:	1
License:	Apache
Group:		Networking/Daemons
Source0:	http://jakarta.apache.org/builds/jakarta-tomcat-connectors/jk/release/v1.2.1/src/jakarta-tomcat-connectors-jk-1.2.1-src.tar.gz
Source1:	%{name}.conf
URL:		http://jakarta.apache.org/builds/jakarta-tomcat-connectors/jk/doc/
Prereq:		%{_sbindir}/apxs
BuildRequires:	%{apxs}
BuildRequires:	apache(EAPI)-devel	>= %{apache_version}
BuildRequires:	jakarta-ant >= 1.5.1
BuildRequires:	jakarta-tomcat
Requires:	apache(EAPI)		>= %{apache_version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	jakarta-tomcat-connectors-jk

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)
%define         _javalibdir     /usr/share/java
%define         _tomcatdir      %{_libdir}/tomcat

%description
JK  is a replacement to the elderly mod_jserv. It was a completely new Tomcat-Apache plug-in that handles the communication between Tomcat and Apache.

%prep
%setup -q -n jakarta-tomcat-connectors-jk-%{version}-src

%build
cd jk

if [ -z "$JAVA_HOME" ]; then
        JAVA_HOME=/usr/lib/java
fi
ANT_HOME=%{_javalibdir}
export JAVA_HOME ANT_HOME
	
cat > build.properties << EOF
#tomcat5.home=%{_libdir}/tomcat
tomcat40.home=%{_tomcatdir}
#tomcat41.home==%{_libdir}/tomcat
#apache2.home=/opt/apache2
apache13.home=%{_libdir}
apr.home=\${apache2.home}
apr.include=%{_includedir}/apache
apr-util.include=%{_includedir}/apache
apr.lib=%{_libdir}
apr-util.lib=%{_libdir}
#apache2.lib=%{_libdir}
so.debug=false
so.optimize=true
so.profile=false
EOF

ant native

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},/etc/httpd,/var/lock/mod_dav}

install lib%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}/
install %{SOURCE1} $RPM_BUILD_ROOT/etc/httpd/mod_dav.conf

%post
%{apxs} -e -a -n %{mod_name} %{_pkglibdir}/lib%{mod_name}.so 1>&2
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*mod_dav.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/mod_dav.conf" >> /etc/httpd/httpd.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	%{_sysconfdir}/rc.d/init.d/httpd restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/lib%{mod_name}.so 1>&2
	grep -v "^Include.*mod_dav.conf" /etc/httpd/httpd.conf > \
		/etc/httpd/httpd.conf.tmp
	mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README CHANGES INSTALL LICENSE.html
%config(noreplace) /etc/httpd/mod_dav.conf
%attr(755,root,root) %{_pkglibdir}/*
%attr(750,http,http) /var/lock/mod_dav
