%define 	apxs	/usr/sbin/apxs
Summary:	Apache module that handles communication between Tomcat and Apache
Summary(pl):	Modu³ Apache'a obs³uguj±cy komunikacjê miêdzy Tomcatem a Apachem
%define		mod_name	jk
Name:		apache-mod_%{mod_name}
Version:	1.2.4
Release:	0.1
License:	Apache
Group:		Networking/Daemons
Source0:	http://jakarta.apache.org/builds/jakarta-tomcat-connectors/jk/release/v%{version}/src/jakarta-tomcat-connectors-jk-%{version}-src.tar.gz
# Source0-md5:	9641a826b87e64692377161215cfd5e1
Source1:	%{name}.conf
URL:		http://jakarta.apache.org/builds/jakarta-tomcat-connectors/jk/doc/
BuildRequires:	%{apxs}
Requires:       apache(modules-api) = %{apache_modules_api}
BuildRequires:	libtool
BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	perl-base
Requires(post,preun):	%{apxs}
Requires(post,preun):	grep
Requires(preun):	fileutils
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	jakarta-tomcat-connectors-jk

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)
%define         _javalibdir     /usr/share/java
%define         _tomcatdir      %{_libdir}/tomcat

%description
JK is a replacement to the elderly mod_jserv. It was a completely new
Tomcat-Apache plug-in that handles the communication between Tomcat
and Apache.

%description -l pl
JK jest zamiennikiem starego mod_jserv. Jest ca³kowicie now± wtyczk±
Tomcat-Apache obs³uguj±c± komunikacjê miêdzy Tomcatem a Apachem.

%prep
%setup -q -n jakarta-tomcat-connectors-jk-%{version}-src

%build
cd jk/native

if [ -z "$JAVA_HOME" ]; then
        JAVA_HOME=/usr/lib/java
fi
export JAVA_HOME
./buildconf.sh

%configure \
	--enable-EAPI \
	--with-apxs=%{apxs} \
	--with-java-home=${JAVA_HOME}

%{__make} \
	LIBTOOL=%{_bindir}/libtool

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/httpd,/var/lock/mod_jk}

cd jk/native

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	APXS="%{apxs} -S LIBEXECDIR=$RPM_BUILD_ROOT$(%{apxs} -q LIBEXECDIR)" \
	libexecdir=$RPM_BUILD_ROOT%{_pkglibdir}

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/mod_jk.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{apxs} -e -a -n %{mod_name} %{_pkglibdir}/lib%{mod_name}.so 1>&2
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*mod_jk.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/mod_jk.conf" >> /etc/httpd/httpd.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/lib%{mod_name}.so 1>&2
	umask 027
	grep -v "^Include.*mod_jk.conf" /etc/httpd/httpd.conf > \
		/etc/httpd/httpd.conf.tmp
	mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc jk/native/{README,CHANGES.txt} jk/docs/*
%config(noreplace) %{_sysconfdir}/httpd/mod_jk.conf
%attr(755,root,root) %{_pkglibdir}/*
%attr(750,http,http) /var/lock/mod_jk
