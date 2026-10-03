# Prebuilt foreign binary: no build-id or debuginfo can be produced, so the
# debug package is disabled.
%global debug_package %{nil}

# Disable generation of build-id symlinks
%global _build_id_links none
%undefine _missing_build_ids_terminate_build

# Empty all four hooks to keep the prebuilt payload byte-identical to upstream
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_lto %{nil}
%global __brp_strip_static_archive %{nil}

# add-determinism would mutate the foreign binary
%undefine __brp_add_determinism

# Filter internal Electron shared libraries
%global __provides_exclude_from ^/opt/ExifCleaner/.*$
%global __requires_exclude ^(libffmpeg\\.so.*)$

Name:           exifcleaner
Version:        4.5.0
Release:        %autorelease
Summary:        Cross-platform desktop GUI app to clean image, video, and PDF metadata
License:        MIT
URL:            https://github.com/szTheory/exifcleaner
ExclusiveArch:  x86_64

Source0:        https://github.com/szTheory/exifcleaner/releases/download/v%{version}/exifcleaner-%{version}.x86_64.rpm
Source1:        https://raw.githubusercontent.com/szTheory/exifcleaner/v%{version}/LICENSE
Source2:        com.exifcleaner.exifcleaner.metainfo.xml

BuildRequires:  cpio
BuildRequires:  desktop-file-utils
BuildRequires:  appstream
BuildRequires:  binutils
BuildRequires:  chrpath

Requires:       hicolor-icon-theme
Requires:       xdg-utils
Requires:       gtk3
Requires:       libnotify
Requires:       nss
Requires:       libsecret
Requires:       libXScrnSaver

%description
ExifCleaner is an open-source cross-platform desktop GUI app to clean metadata
from images, videos, PDFs, and other files with drag-and-drop support.
This package rewraps the upstream prebuilt x86_64 Linux RPM for Fedora (COPR only).

%prep
%setup -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

for bin in opt/ExifCleaner/exifcleaner opt/ExifCleaner/*.so; do
  if [ -f "$bin" ]; then
    if readelf -d "$bin" 2>/dev/null | grep -Eq 'RUNPATH.*(/home/runner|/tmp)'; then
      chrpath -d "$bin" || true
    fi
  fi
done

cp %{SOURCE1} LICENSE

%build
# Nothing to compile

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

cp -a opt %{buildroot}/
cp -a usr %{buildroot}/

# Yabancı build-id dizinini temizle
rm -rf %{buildroot}/usr/lib

install -Dm0644 %{SOURCE2} %{buildroot}%{_metainfodir}/com.exifcleaner.exifcleaner.metainfo.xml

# Çalıştırma bayraklarını ve dinamik tema kontrolünü sağlayan wrapper betik
install -d %{buildroot}%{_bindir}
cat << 'EOF' > %{buildroot}%{_bindir}/exifcleaner
#!/bin/bash
FLAGS="--ozone-platform=wayland --disable-vulkan --disable-features=Vulkan"

# GNOME / GTK sistem temasını kontrol et
COLOR_SCHEME=$(gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null | tr -d "'\"")
GTK_THEME=$(gsettings get org.gnome.desktop.interface gtk-theme 2>/dev/null | tr -d "'\"")

# Sistem koyu moddaysa Electron'a koyu temayı bildir
if [ "$COLOR_SCHEME" = "prefer-dark" ] || [[ "$GTK_THEME" =~ [Dd]ark ]]; then
    FLAGS="$FLAGS --force-dark-mode"
fi

exec /opt/ExifCleaner/exifcleaner $FLAGS "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/exifcleaner

# Menü kısayolunun wrapper betiği çalıştırmasını garantiye al
sed -i 's|^Exec=.*|Exec=/usr/bin/exifcleaner %U|' %{buildroot}%{_datadir}/applications/exifcleaner.desktop

chmod 0755 %{buildroot}/opt/ExifCleaner/exifcleaner
if [ -f %{buildroot}/opt/ExifCleaner/chrome-sandbox ]; then
  chmod 4755 %{buildroot}/opt/ExifCleaner/chrome-sandbox || chmod 0755 %{buildroot}/opt/ExifCleaner/chrome-sandbox
fi

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/exifcleaner.desktop
appstreamcli validate --no-net %{buildroot}%{_metainfodir}/com.exifcleaner.exifcleaner.metainfo.xml

%files
%license LICENSE
%{_bindir}/exifcleaner
/opt/ExifCleaner/
%{_datadir}/applications/exifcleaner.desktop
%{_datadir}/icons/hicolor/*/apps/*
%{_metainfodir}/com.exifcleaner.exifcleaner.metainfo.xml

%changelog
* Sat Oct 03 2026 Saffet Yavuz <saffet.yavuz@tutamail.com> - 4.5.0-3
- Add dynamic dark mode detection to wayland wrapper
- Clean invalid build-id symlinks from upstream payload
- Filter bundled libffmpeg.so from DT_NEEDED dependencies
