%global qt_version 6.8.3

%global gst 1.0

Summary: Qt6 - Multimedia support
Name:    qt6-qtmultimedia
Version: 6.8.3
Release: 3%{?dist}

License: LGPL-3.0-only OR GPL-3.0-only WITH Qt-GPL-exception-1.0
Url:     http://www.qt.io
Source0: %{name}-%{version}.tar.bz2

Patch1: 8145cd06af7550d2b6bf765ff7e0d84eda568ca9.patch
Patch2: fix-clang-pulse-narrowing.patch

# filter plugin/qml provides
%global __provides_exclude_from ^(%{_qt6_archdatadir}/qml/.*\\.so|%{_qt6_plugindir}/.*\\.so)$

BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: ninja
BuildRequires: qt6-rpm-macros
BuildRequires: qt6-qtbase-devel >= %{qt_version}
BuildRequires: qt6-qtbase-private-devel
%{?_qt6:Requires: %{_qt6}%{?_isa} = %{_qt6_version}}
BuildRequires: qt6-qtdeclarative-devel
BuildRequires: qt6-qtshadertools-devel
BuildRequires: qt6-qtquick3d-devel
BuildRequires: pkgconfig(alsa)
BuildRequires: pulseaudio-devel
BuildRequires: pkgconfig(gstreamer-%{gst})
BuildRequires: pkgconfig(gstreamer-app-%{gst})
BuildRequires: pkgconfig(gstreamer-audio-%{gst})
BuildRequires: pkgconfig(gstreamer-base-%{gst})
BuildRequires: pkgconfig(gstreamer-pbutils-%{gst})
BuildRequires: pkgconfig(gstreamer-plugins-bad-%{gst})
BuildRequires: pkgconfig(gstreamer-video-%{gst})
BuildRequires: pkgconfig(libpulse) pkgconfig(libpulse-mainloop-glib)
BuildRequires: pkgconfig(xkbcommon) >= 0.5.0
BuildRequires: openssl-devel
BuildRequires: ffmpeg-devel

# workaround missing dep
# /usr/include/gstreamer-1.0/gst/gl/wayland/gstgldisplay_wayland.h:26:10: fatal error: wayland-client.h: No such file or directory
BuildRequires: wayland-devel

%description
The Qt Multimedia module provides a rich feature set that enables you to
easily take advantage of a platforms multimedia capabilites and hardware.
This ranges from the playback and recording of audio and video content to
the use of available devices like cameras and radios.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: qt6-qtbase-devel%{?_isa}
Requires: qt6-qtdeclarative-devel%{?_isa}
# Qt6Multimedia.pc containts:
# Libs.private: ... -lpulse-mainloop-glib -lpulse -lglib-2.0
Requires: pkgconfig(libpulse-mainloop-glib)
%description devel
%{summary}.

%prep
%autosetup -n %{name}-%{version}/upstream -p1


%build
%if 0%{?rhel} && 0%{?rhel} < 10
. /opt/rh/gcc-toolset-13/enable
%endif
%cmake_qt6 \
  -DQT_FEATURE_alsa=OFF \
  -DQT_FEATURE_ffmpeg=ON \
  -DQT_FEATURE_linux_v4l=OFF \
  -DQT_FEATURE_gstreamer=ON \
  -DQT_FEATURE_gstreamer_photography=ON \
  -DQT_FEATURE_gstreamer_gl=OFF \
  -DQT_FEATURE_gstreamer_gl_egl=ON \
  -DQT_FEATURE_gstreamer_gl_wayland=ON \
  -DQT_FEATURE_gstreamer_gl_x11=OFF \
  -DQT_FEATURE_pulseaudio=ON \
  -DQT_BUILD_EXAMPLES:BOOL=OFF \
  -DQT_INSTALL_EXAMPLES_SOURCES=OFF

%cmake_build


%install
%cmake_install

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt6_libdir}
for prl_file in *.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSES/*
%{_qt6_libdir}/libQt6Multimedia.so.6*
%{_qt6_libdir}/libQt6MultimediaQuick.so.6*
%{_qt6_libdir}/libQt6MultimediaWidgets.so.6*
%{_qt6_libdir}/libQt6SpatialAudio.so.6*
%{_qt6_libdir}/libQt6Quick3DSpatialAudio.so.6*
%{_qt6_archdatadir}/qml/QtMultimedia/
%dir %{_qt6_archdatadir}/qml/QtQuick3D/SpatialAudio
%{_qt6_archdatadir}/qml/QtQuick3D/SpatialAudio/
%dir %{_qt6_plugindir}/multimedia
%{_qt6_plugindir}/multimedia/libgstreamermediaplugin.so
%{_qt6_plugindir}/multimedia/libffmpegmediaplugin.so

%files devel
#%%{_qt6_headerdir}/QtQGstreamerMediaPlugin/
%{_qt6_headerdir}/QtMultimedia/
%{_qt6_headerdir}/QtMultimediaQuick/
%{_qt6_headerdir}/QtMultimediaWidgets/
%{_qt6_headerdir}/QtSpatialAudio/
%{_qt6_headerdir}/QtQuick3DSpatialAudio/
%{_qt6_headerdir}/QtMultimediaTestLib/
%{_qt6_headerdir}/QtFFmpegMediaPluginImpl/
%{_qt6_headerdir}/QtGstreamerMediaPluginImpl/
%{_qt6_libdir}/libQt6BundledResonanceAudio.a
#%%{_qt6_libdir}/libQt6QGstreamerMediaPlugin.a
#%%{_qt6_libdir}/libQt6QGstreamerMediaPlugin.prl
%{_qt6_libdir}/libQt6FFmpegMediaPluginImpl.a
%{_qt6_libdir}/libQt6FFmpegMediaPluginImpl.prl
%{_qt6_libdir}/libQt6GstreamerMediaPluginImpl.a
%{_qt6_libdir}/libQt6GstreamerMediaPluginImpl.prl
%{_qt6_libdir}/libQt6MultimediaTestLib.a
%{_qt6_libdir}/libQt6MultimediaTestLib.prl
%{_qt6_libdir}/libQt6Multimedia.so
%{_qt6_libdir}/libQt6Multimedia.prl
%{_qt6_libdir}/libQt6MultimediaQuick.so
%{_qt6_libdir}/libQt6MultimediaQuick.prl
%{_qt6_libdir}/libQt6MultimediaWidgets.so
%{_qt6_libdir}/libQt6MultimediaWidgets.prl
%{_qt6_libdir}/libQt6SpatialAudio.so
%{_qt6_libdir}/libQt6SpatialAudio.prl
%{_qt6_libdir}/libQt6Quick3DSpatialAudio.so
%{_qt6_libdir}/libQt6Quick3DSpatialAudio.prl
%{_qt6_libdir}/cmake/Qt6/*.cmake
%{_qt6_libdir}/cmake/Qt6BuildInternals/StandaloneTests/*.cmake
%dir %{_qt6_libdir}/cmake/Qt6BundledResonanceAudio/
%{_qt6_libdir}/cmake/Qt6BundledResonanceAudio/*.cmake
#%%dir %%{_qt6_libdir}/cmake/Qt6QGstreamerMediaPluginPrivate/
#%%{_qt6_libdir}/cmake/Qt6QGstreamerMediaPluginPrivate/*.cmake
%dir  %{_qt6_libdir}/cmake/Qt6MultimediaQuickPrivate
%{_qt6_libdir}/cmake/Qt6MultimediaQuickPrivate/*.cmake
%dir %{_qt6_libdir}/cmake/Qt6Multimedia
%{_qt6_libdir}/cmake/Qt6Multimedia/*.cmake
%dir %{_qt6_libdir}/cmake/Qt6MultimediaWidgets
%{_qt6_libdir}/cmake/Qt6MultimediaWidgets/*.cmake
%dir %{_qt6_libdir}/cmake/Qt6SpatialAudio/
%{_qt6_libdir}/cmake/Qt6SpatialAudio/*cmake
%dir %{_qt6_libdir}/cmake/Qt6Quick3DSpatialAudioPrivate
%{_qt6_libdir}/cmake/Qt6Quick3DSpatialAudioPrivate/*cmake
%dir %{_qt6_libdir}/cmake/Qt6Qml/QmlPlugins
%{_qt6_libdir}/cmake/Qt6Qml/QmlPlugins/*.cmake
%dir %{_qt6_libdir}/cmake/Qt6FFmpegMediaPluginImplPrivate
%{_qt6_libdir}/cmake/Qt6FFmpegMediaPluginImplPrivate/*.cmake
%dir %{_qt6_libdir}/cmake/Qt6GstreamerMediaPluginImplPrivate
%{_qt6_libdir}/cmake/Qt6GstreamerMediaPluginImplPrivate/*.cmake
%dir %{_qt6_libdir}/cmake/Qt6MultimediaTestLibPrivate
%{_qt6_libdir}/cmake/Qt6MultimediaTestLibPrivate/*.cmake
%{_qt6_archdatadir}/mkspecs/modules/*.pri
%{_qt6_libdir}/qt6/metatypes/qt6*_metatypes.json
%{_qt6_libdir}/qt6/modules/*.json
%{_qt6_libdir}/pkgconfig/*.pc
