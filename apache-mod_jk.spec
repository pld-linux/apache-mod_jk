# TODO:
# - logrotate file
%define		mod_name	jk
%define		apxs		/usr/sbin/apxs
Summary:	Apache module that handles communication between Tomcat and Apache
Summary(pl):	Modu³ Apache'a obs³uguj±cy komunikacjê miêdzy Tomcatem a Apachem
Name:		apache-mod_%{mod_name}
Version:	1.2.14.1
Release:	0.1
License:	Apache
Group:		Networking/Daemons
Source0:	http://www.apache.org/dist/jakarta/tomcat-connectors/jk/source/jk-1.2.14/jakarta-tomcat-connectors-%{version}-src.tar.gz
# Source0-md5:	41a90c633088e0f1ba422c10546a028a
Source1:	%{name}.conf
Patch0:		%{name}-libtool.patch
URL:		http://jakarta.apache.org/builds/jakarta-tomcat-connectors/jk/doc/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.0.40
BuildRequires:	apr-devel >= 1:1.0
BuildRequires:	apr-util-devel >= 1:1.0
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
JK jest zamiennikiem starego mod_jserv. Jest ca³kowicie now± wtyczk±
Tomcat-Apache obs³uguj±c± komunikacjê miêdzy Tomcatem a Apachem.

%prep
%setup -q -n jakarta-tomcat-connectors-%{version}-src
%patch0 -p1

%build
cd jk/native

if [ -z "$JAVA_HOME" ]; then
	JAVA_HOME=%{_libdir}/java
fi
export JAVA_HOME

# temp hack for broken apxs (fixed in apache-apxs-2.2.0-6.1)
sed -i -e 's#`.*exp_installbuilddir`#%{_prefix}/lib/apache/build/#' configure.in

./buildconf.sh

%configure \
	--enable-EAPI \
	--with-apxs=%{apxs} \
	--with-java-home=${JAVA_HOME}

%{__make} \
	EXTRA_CFLAGS="`apr-1-config --includes` `apu-1-config --includes`"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/httpd.conf,/var/{lock/mod_jk,log/httpd}}

%{__make} -C jk/native install \
	DESTDIR=$RPM_BUILD_ROOT \
	APXS="%{apxs} -S LIBEXECDIR=$RPM_BUILD_ROOT%{_pkglibdir}" \
	libexecdir=$RPM_BUILD_ROOT%{_pkglibdir}

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/80_mod_jk.conf
touch $RPM_BUILD_ROOT/var/log/httpd/mod_jk.log

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi
if [ ! -f /var/log/httpd/mod_jk.log ]; then
	umask 027
	touch /var/log/httpd/mod_jk.log
	chown root:logs /var/log/httpd/mod_jk.log
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
