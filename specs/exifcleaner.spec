# Prebuilt foreign binary: no build-id or debuginfo can be produced, so the
# debug package is disabled. The payload ships as-is from the release RPM.
%global debug_package %{nil}

# NOTE: %%global debug_package %%{nil} makes the default ELF-rewriting brp hooks run.
# Empty all four hooks to keep the prebuilt payload byte-identical to upstream.
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_lto %{nil}
%global __brp_strip_static_archive %{nil}

# add-determinism would regenerate build-id links and mutate the foreign binary.
%undefine __brp_add_determinism

# Filter internal Electron shared libraries from leaking into RPM provides.
%global __provides_exclude_from ^/opt/ExifCleaner/.*$

Name:           exifcleaner
Version:        4.5.0
Release:        %autorelease
Summary:        Cross-platform desktop GUI app to clean image, video, and PDF metadata
License:        MIT
URL:            https://github.com/szTheory/exifcleaner
ExclusiveArch:  x86_64

# Upstream prebuilt x86_64 RPM is fetched directly by spectool.
Source0:        https://github.com/szTheory/exifcleaner/releases/download/v%{version}/exifcleaner-%{version}.x86_64.rpm
# Upstream prebuilt RPM does not bundle the root LICENSE file. Fetch it from the release tag:
Source1:        https://raw.githubusercontent.com/szTheory/exifcleaner/v%{version}/LICENSE
# Curated AppStream metadata
Source2:        com.exifcleaner.exifcleaner.metainfo.xml

BuildRequires:  cpio
BuildRequires:  desktop-file-utils
BuildRequires:  appstream
BuildRequires:  binutils
BuildRequires:  chrpath

# Runtime dependencies required by the Electron framework and desktop environment:
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
# Extract the upstream RPM payload
rpm2cpio %{SOURCE0} | cpio -idmv

# Clean invalid build workspace RUNPATH entries if left by electron-builder
for bin in opt/ExifCleaner/exifcleaner opt/ExifCleaner/*.so; do
  if [ -f "$bin" ]; then
    if readelf -d "$bin" 2>/dev/null | grep -Eq 'RUNPATH.*(/home/runner|/tmp)'; then
      chrpath -d "$bin" || true
    fi
  fi
done

cp %{SOURCE1} LICENSE

%build
# Nothing to compile: upstream prebuilt payload was extracted in %%prep.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# Copy extracted filesystem trees
cp -a opt %{buildroot}/
cp -a usr %{buildroot}/

# Install curated AppStream metadata
install -Dm0644 %{SOURCE2} %{buildroot}%{_metainfodir}/com.exifcleaner.exifcleaner.metainfo.xml

# Ensure /usr/bin symlink is owned by the package
install -d %{buildroot}%{_bindir}
ln -sf /opt/ExifCleaner/exifcleaner %{buildroot}%{_bindir}/exifcleaner

# Ensure executable permissions on main binary and sandbox
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
* Sat Oct 03 2026 Saffet Yavuz <saffet@example.com> - 4.5.0-1
- Initial repackaging of upstream ExifCleaner prebuilt RPM for Fedora COPR
- Unset ELF-rewriting brp hooks to preserve foreign binary integrity
- Exclude internal Electron libraries from RPM provides
