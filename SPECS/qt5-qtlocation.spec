%global qt_module qtlocation

%global build_tests 1

Summary: Qt5 - Location component
Name:    qt5-%{qt_module}
Version: 5.15.3
Release: 1%{?dist}

# See LGPL_EXCEPTIONS.txt, LICENSE.GPL3, respectively, for exception details
License: LGPLv2 with exceptions or GPLv3 with exceptions
Url:     http://www.qt.io
%global majmin %(echo %{version} | cut -d. -f1-2)
Source0: https://download.qt.io/official_releases/qt/%{majmin}/%{version}/submodules/%{qt_module}-everywhere-opensource-src-%{version}.tar.xz

# build failure with gcc10
# various C++ runtime headers indirectly included <string> which in turn
# included <local> and <cerrno>.  Those indirect inclusions have been
# eliminated which in turn forces packages to include the C++ headers they
# actually need.
Patch0: qtlocation-gcc10.patch

# filter plugin/qml provides
%global __provides_exclude_from ^(%{_qt5_archdatadir}/qml/.*\\.so|%{_qt5_plugindir}/.*\\.so)$

## upstreamable patches

BuildRequires: qt5-qtbase-devel >= 5.9.0
# QtPositioning core-private
BuildRequires: qt5-qtbase-private-devel
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
BuildRequires: qt5-qtdeclarative-devel >= 5.9.0

BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(icu-i18n)
BuildRequires: pkgconfig(libssl)
BuildRequires: pkgconfig(libcrypto)

%description
The Qt Location and Qt Positioning APIs gives developers the ability to
determine a position by using a variety of possible sources, including
satellite, or wifi, or text file, and so on.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: qt5-qtbase-devel%{?_isa}
%description devel
%{summary}.

%package examples
Summary: Programming examples for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
%description examples
%{summary}.

%if 0%{?build_tests}
%package tests
Summary: Unit tests for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description tests
%{summary}.
%endif

%prep
%setup -q -n %{qt_module}-everywhere-src-%{version}
%patch0 -p1 -b .gcc10


%build
# no shadow builds until fixed: https://bugreports.qt.io/browse/QTBUG-37417
%{qmake_qt5}

%make_build

%if 0%{?build_tests}
make sub-tests %{?_smp_mflags} -k ||:
%endif

%install
make install INSTALL_ROOT=%{buildroot}

%if 0%{?build_tests}
# Install tests for gating
mkdir -p %{buildroot}%{_qt5_libdir}/qt5
find ./tests -not -path '*/\.*' -type d | while read LINE
do
    mkdir -p "%{buildroot}%{_qt5_libdir}/qt5/$LINE"
done
find ./tests -not -path '*/\.*' -not -name '*.h' -not -name '*.cpp' -not -name '*.pro' -not -name 'uic_wrapper.sh' -not -name 'Makefile' -not -name 'target_wrapper.sh' -type f | while read LINE
do
    cp -r --parents "$LINE" %{buildroot}%{_qt5_libdir}/qt5/
done
%endif

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd


%ldconfig_scriptlets

%files
%license LICENSE.GPL* LICENSE.LGPL*
%{_qt5_libdir}/libQt5Location.so.5*
%{_qt5_archdatadir}/qml/QtLocation/
%{_qt5_plugindir}/geoservices/
%{_qt5_libdir}/libQt5Positioning.so.5*
%dir %{_qt5_archdatadir}/qml/QtPositioning
%{_qt5_archdatadir}/qml/QtPositioning/*
%{_qt5_plugindir}/position/
%{_qt5_libdir}/libQt5PositioningQuick.so.5*

%files devel
%{_qt5_headerdir}/QtLocation/
%{_qt5_libdir}/libQt5Location.so
%{_qt5_libdir}/libQt5Location.prl
%{_qt5_headerdir}/QtPositioning/
%{_qt5_libdir}/libQt5Positioning.so
%{_qt5_libdir}/libQt5Positioning.prl
%{_qt5_headerdir}/QtPositioningQuick/
%{_qt5_libdir}/libQt5PositioningQuick.so
%{_qt5_libdir}/libQt5PositioningQuick.prl
%{_qt5_libdir}/pkgconfig/Qt5Location.pc
%dir %{_qt5_libdir}/cmake/Qt5Location
%{_qt5_libdir}/cmake/Qt5Location/Qt5Location*.cmake
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_location*.pri
%{_qt5_libdir}/pkgconfig/Qt5Positioning.pc
%dir %{_qt5_libdir}/cmake/Qt5Positioning
%{_qt5_libdir}/cmake/Qt5Positioning/Qt5Positioning*.cmake
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_positioning*.pri
%{_qt5_libdir}/pkgconfig/Qt5PositioningQuick.pc
%dir %{_qt5_libdir}/cmake/Qt5PositioningQuick/
%{_qt5_libdir}/cmake/Qt5PositioningQuick/Qt5PositioningQuick*.cmake
%{_qt5_archdatadir}/mkspecs/modules/qt_lib_positioning*.pri


%files examples
%{_qt5_examplesdir}/

%if 0%{?build_tests}
%files tests
%{_qt5_libdir}/qt5/tests
%endif

%changelog
* Mon Mar 28 2022 Jan Grulich <jgrulich@redhat.com> - 5.15.3-1
- 5.15.3
  Resolves: bz#2061396

* Wed Apr 28 2021 Jan Grulich <jgrulich@redhat.com> - 5.15.2-2
- Rebuild (binutils)
  Resolves: bz#1930047

* Sun Apr 04 2021 Jan Grulich <jgrulich@redhat.com> - 5.15.2-1
- 5.15.2
  Resolves: bz#1930047

* Mon Nov 18 2019 Jan Grulich <jgrulich@redhat.com> - 5.12.5-1
- 5.12.5
  Resolves: bz#1733143

* Mon Dec 10 2018 Jan Grulich <jgrulich@redhat.com> - 5.11.1-2
- Rebuild to fix CET notes
  Resolves: bz#1657251

* Tue Jul 03 2018 Jan Grulich <jgrulich@redhat.com> - 5.11.1-1
- 5.11.1

* Wed Mar 07 2018 Adam Williamson <awilliam@redhat.com> - 5.10.1-3
- Rebuild to fix GCC 8 mis-compilation
  See https://da.gd/YJVwk ("GCC 8 ABI change on x86_64")

* Wed Mar 07 2018 Rex Dieter <rdieter@fedoraproject.org> - 5.10.1-2
- rebuild (gcc)
- use %%make_build %%ldconfig_scriptlets

* Wed Feb 14 2018 Jan Grulich <jgrulich@redhat.com> - 5.10.1-1
- 5.10.1

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 5.10.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Dec 19 2017 Jan Grulich <jgrulich@redhat.com> - 5.10.0-1
- 5.10.0

* Thu Nov 30 2017 Pete Walter <pwalter@fedoraproject.org> - 5.9.3-2
- Rebuild for ICU 60.1

* Thu Nov 23 2017 Jan Grulich <jgrulich@redhat.com> - 5.9.3-1
- 5.9.3

* Mon Oct 09 2017 Jan Grulich <jgrulich@redhat.com> - 5.9.2-1
- 5.9.2

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.9.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 19 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.9.1-1
- 5.9.1

* Fri Jun 16 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.9.0-2
- drop shadow/out-of-tree builds (#1456211,QTBUG-37417)
- directly reference other qt5-related build deps

* Wed May 31 2017 Helio Chissini de Castro <helio@kde.org> - 5.9.0-1
- Upstream official release

* Fri May 26 2017 Helio Chissini de Castro <helio@kde.org> - 5.9.0-0.1.rc
- Upstream Release Candidate retagged

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.9.0-0.beta.3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Tue May 09 2017 Helio Chissini de Castro <helio@kde.org> - 5.9.0-0.beta.3
- Upstream beta 3

* Mon Apr 03 2017 Rex Dieter <rdieter@fedoraproject.org> - 5.8.0-2
- build docs on all archs

* Mon Jan 30 2017 Helio Chissini de Castro <helio@kde.org> - 5.8.0-1
- New upstream version

* Mon Jan 02 2017 Rex Dieter <rdieter@math.unl.edu> - 5.7.1-4
- filter plugins too

* Mon Jan 02 2017 Rex Dieter <rdieter@math.unl.edu> - 5.7.1-3
- filter qml provides, BR: qt5-qtdeclarative explicitly

* Sat Dec 10 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.7.1-2
- drop BR: cmake (handled by qt5-rpm-macros now)
- 5.7.1 dec5 snapshot

* Wed Nov 09 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.1-1
- New upstream version

* Mon Jul 04 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.0-2
- Compiled with gcc

* Tue Jun 14 2016 Helio Chissini de Castro <helio@kde.org> - 5.7.0-1
- Qt 5.7.0 release

* Thu Jun 09 2016 Jan Grulich <jgrulich@redhat.com> - 5.6.1-1
- Update to 5.6.1

* Thu Apr 21 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-4
- BR: qt5-qtbase-private-devel

* Sun Mar 20 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-3
- rebuild

* Fri Mar 18 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-2
- rebuild

* Mon Mar 14 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-1
- 5.6.0 final release

* Tue Feb 23 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.10.rc
- Update to final RC

* Sun Feb 21 2016 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.9.rc
- rebuild

* Mon Feb 15 2016 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.8
- Update RC release

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.6.0-0.7.beta
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 28 2015 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.6.beta
- update source URL, use %%license, BR: cmake

* Mon Dec 21 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.5
- Update to final beta release

* Fri Dec 11 2015 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-0.4
- (re) add bootstrap macro support
- drop geoclue(1) dep (unused at build time anyway (#1286886)
- drop (deprecated) gypsy support (#1069225)

* Thu Dec 10 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.3
- Official beta release

* Sun Dec 06 2015 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-0.2
- (re)add bootstrap macro support

* Tue Nov 03 2015 Helio Chissini de Castro <helio@kde.org> - 5.6.0-0.1
- Start to implement 5.6.0 beta

* Thu Oct 15 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.1-2
- Update to final release 5.5.1

* Tue Sep 29 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.1-1
- Update to Qt 5.5.1 RC1

* Wed Jul 29 2015 Rex Dieter <rdieter@fedoraproject.org> 5.5.0-3
- -docs: BuildRequires: qt5-qhelpgenerator, standardize bootstrapping

* Thu Jul 16 2015 Rex Dieter <rdieter@fedoraproject.org> 5.5.0-2
- tighten qtbase dep (#1233829), .spec cosmetics, (re)enable docs

* Wed Jul 1 2015 Helio Chissini de Castro <helio@kde.org> 5.5.0-1
- New final upstream release Qt 5.5.0

* Wed Jun 24 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-0.2.rc
- Update for official RC1 released packages

* Mon Jun 15 2015 Daniel Vrátil <dvratil@redhat.com> - 5.5.0-0.1.rc
- Qt 5.5.0 RC1

* Wed Jun 03 2015 Jan Grulich <jgrulich@redhat.com> - 5.4.2-1
- 5.4.2

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 5.4.1-3
- Rebuilt for GCC 5 C++11 ABI change

* Fri Feb 27 2015 Rex Dieter <rdieter@fedoraproject.org> - 5.4.1-2
- rebuild (gcc5)

* Tue Feb 24 2015 Jan Grulich <jgrulich@redhat.com> 5.4.1-1
- 5.4.1

* Mon Feb 16 2015 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-3
- rebuild (gcc5)

* Wed Dec 31 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-2
- BR: pkgconfig(Qt5Qml) > 5.4.0 (#1177986)

* Wed Dec 10 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-1
- 5.4.0 (final)

* Fri Nov 28 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.3.rc
- 5.4.0-rc

* Mon Nov 03 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.2.beta
- out-of-tree build, use %%qmake_qt5

* Sun Oct 19 2014 Rex Dieter <rdieter@fedoraproject.org> 5.4.0-0.1.beta
- 5.4.0-beta

* Tue Sep 16 2014 Rex Dieter <rdieter@fedoraproject.org> 5.3.2-1
- 5.3.2

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 17 2014 Jan Grulich <jgrulich@redhat.com> - 5.3.1-1
- 5.3.1

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 21 2014 Jan Grulich <jgrulich@redhat.com> 5.3.0-1
- 5.3.0

* Mon May 05 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.1-2
- sanitize .prl file(s)

* Wed Feb 05 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.1-1
- 5.2.1

* Mon Jan 27 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-3
- build -examples only when supported

* Sun Jan 26 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-2
- -examples subpkg

* Thu Jan 02 2014 Rex Dieter <rdieter@fedoraproject.org> 5.2.0-1
- first try
