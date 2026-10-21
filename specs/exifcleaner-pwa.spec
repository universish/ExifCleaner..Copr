%global debug_package %{nil}

Name:           exifcleaner-pwa
Version:        4.5.0
Release:        1%{?dist}
Summary:        ExifCleaner PWA Launcher (Browser Wrapper)
License:        MIT
URL:            https://exifcleaner.com
BuildArch:      noarch

Requires:       pciutils
Requires:       xdg-utils
Requires:       hicolor-icon-theme

%description
Smart PWA wrapper for ExifCleaner. Launches the local Electron web assets
as a standalone borderless PWA window in the user's preferred browser without Electron dependencies.

%prep
%build
%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}%{_datadir}/applications

# PWA Başlatıcı Script
cat << 'EOF' > %{buildroot}%{_libexecdir}/exifcleaner-browser-wrapper
#!/usr/bin/env bash
# Electron app.asar içeriğini okuyabilen veya lokal asset'leri başlatan PWA sarmalayıcı
URL="file:///opt/ExifCleaner/resources/app.asar/index.html"

PWA_PROFILE_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/exifcleaner-pwa-profile"
mkdir -p "$PWA_PROFILE_DIR"

CHROMIUM_FLAGS="--ozone-platform-hint=auto --user-data-dir=$PWA_PROFILE_DIR --class=ExifCleanerPWA --no-first-run --allow-file-access-from-files"

if lspci -k 2>/dev/null | grep -iA 2 "VGA" | grep -i "nvidia" > /dev/null; then
    CHROMIUM_FLAGS="$CHROMIUM_FLAGS --disable-features=Vulkan"
else
    CHROMIUM_FLAGS="$CHROMIUM_FLAGS --enable-features=Vulkan"
fi

DEFAULT_BROWSER=$(xdg-settings get default-web-browser 2>/dev/null || xdg-mime query default x-scheme-handler/http 2>/dev/null)

if [[ "$DEFAULT_BROWSER" == *"chrome"* ]] || [[ "$DEFAULT_BROWSER" == *"chromium"* ]] || [[ "$DEFAULT_BROWSER" == *"brave"* ]] || [[ "$DEFAULT_BROWSER" == *"edge"* ]]; then
    BROWSER_BIN=$(echo "$DEFAULT_BROWSER" | sed 's/.desktop//')
    exec "$BROWSER_BIN" --app="$URL" $CHROMIUM_FLAGS
fi

exec xdg-open "$URL"
EOF
chmod +x %{buildroot}%{_libexecdir}/exifcleaner-browser-wrapper

# Ana Başlatıcı
cat << 'EOF' > %{buildroot}%{_bindir}/exifcleaner-pwa
#!/usr/bin/env bash
exec %{_libexecdir}/exifcleaner-browser-wrapper
EOF
chmod +x %{buildroot}%{_bindir}/exifcleaner-pwa

# Masaüstü Kısayolu
cat << 'EOF' > %{buildroot}%{_datadir}/applications/exifcleaner-pwa.desktop
[Desktop Entry]
Name=ExifCleaner (PWA Mode)
Comment=Clean metadata in Browser
Exec=/usr/bin/exifcleaner-pwa
Icon=exifcleaner
Type=Application
StartupWMClass=ExifCleanerPWA
Categories=Utility;Graphics;
EOF

%files
%{_bindir}/exifcleaner-pwa
%{_libexecdir}/exifcleaner-browser-wrapper
%{_datadir}/applications/exifcleaner-pwa.desktop

%changelog
* Wed Oct 21 2026 Saffet Yavuz <saffet.yavuz@tutamail.com> - 4.5.0-1
- Initial PWA wrapper creation for ExifCleaner.
