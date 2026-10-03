# ExifCleaner..Copr CI for Fedora 44+ (x86_64 RPM)

[ExifCleaner](https://github.com/szTheory/exifcleaner) is an open source desktop GUI app to clean image, video, and PDF metadata.

This repo packages ExifCleaner for Fedora by rewrapping the upstream prebuilt Linux RPM (`exifcleaner-X.Y.Z.x86_64.rpm`) with a Fedora spec. Currently x86_64 only. A GitHub Actions workflow runs daily at 12AM UTC to check the latest release from https://github.com/szTheory/exifcleaner and rebuilds COPR only when a new version is published. The downloaded RPM is verified against a recorded SHA256 checksum before submission.

The COPR project repository is available from: https://copr.fedorainfracloud.org/coprs/universish/ExifCleaner../

## Packaging compliance

This package is distributed via COPR only. It rewraps the upstream prebuilt
binary RPM, so it is **not eligible for the official Fedora repositories**:
the Fedora Packaging Guidelines require all binaries to be built from source
in the Fedora build system, and this repo intentionally ships the upstream
blob as-is (see `specs/exifcleaner.spec`).

Everything else follows the guidelines:

- `ExclusiveArch: x86_64` — matches the tested upstream prebuilt artifact.
- `%build` present (empty — nothing to compile) so rpm's build hooks run.
- `%check` runs `desktop-file-validate` and `appstreamcli validate` on the
  packaged files inside the build.
- `rpmlint` runs in CI on the built RPM with **0 errors, 0 warnings**:
  every flagged pattern is inherent to rewrapping the Electron blob
  (the `/opt` layout, required `$ORIGIN` runpaths, bare SONAMEs on the
  private libs, unstripped prebuilt binaries, GUI app without man page)
  and is documented in the spec.
- `%{_bindir}`, `%{_datadir}`, `%{_metainfodir}` macros used in `%files`.
- License provenance: the MIT license text is fetched from the upstream
  release tag by `spectool` (the prebuilt RPM ships none); a fetch failure
  fails the build, so the packaged license always matches the packaged
  version. `License: MIT` (SPDX) matches the upstream `LICENSE`.
- `%global debug_package %{nil}` with an explicit rationale: the prebuilt
  foreign binary cannot produce debuginfo, so the debug package is meaningless
  for a rewrap. Fedora's `%__os_install_post` gates `brp-strip` and
  `brp-strip-comment-note` on `%__debug_package` being undefined; with
  them active, every ELF in the payload loses its `.comment` section.
  `brp-strip-lto` and `brp-strip-static-archive` are not gated at all. All
  four hooks plus `add-det` are emptied in the spec, keeping the binary
  payload byte-identical to upstream.
- The bundled Electron libraries under `/opt/ExifCleaner` carry bare SONAMEs
  (e.g. `libffmpeg.so`). To prevent private libraries from leaking into the
  system package dependency graph, `%__provides_exclude_from` isolates `/opt/ExifCleaner`.
- One minimal, documented transformation: upstream's electron-builder binary
  can bake in temporary runner paths (`/home/runner/...`), tripping Fedora's
  `check-rpaths`. `%prep` removes invalid `RUNPATH` entries with `chrpath` if
  present, leaving valid `$ORIGIN` paths intact.
- The symlink `/usr/bin/exifcleaner` -> `/opt/ExifCleaner/exifcleaner` is declared
  in `%install`, so RPM owns it directly and no scriptlet is needed.
- Upstream ships no AppStream metadata, so this repo ships a curated
  `com.exifcleaner.exifcleaner.metainfo.xml` (RDNS id following Flathub); the
  upstream desktop file and icons are preserved as-is.
- Dependencies: core Electron dependencies (`gtk3`, `libnotify`, `nss`, `libsecret`,
  `libXScrnSaver`) along with `hicolor-icon-theme` and `xdg-utils` are declared.
- The downloaded RPM is verified against a recorded SHA256 checksum before
  submission to COPR. Note this is trust-on-first-use (guards corruption/mismatch,
  not a signing boundary): upstream publishes no signatures for the RPM.

# Instructions

Enable the COPR repository then install the package:

```bash
sudo dnf copr enable universish/ExifCleaner..
sudo dnf install exifcleaner
```

# Credits

Pattern and workflow structure adapted from [anudeepd/localsend-fedora-copr-ci](https://github.com/anudeepd/localsend-fedora-copr-ci)

— thanks for the clean reference implementation.