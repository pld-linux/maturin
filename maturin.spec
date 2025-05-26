%bcond_without	python3

%define		module		maturin
%define		crates_ver	1.8.6

Summary:	Build and publish rust crates as python packages
Name:		maturin
Version:	1.8.6
Release:	2
License:	MIT or Apache v2.0
Group:		Applications
Source0:	https://github.com/PyO3/maturin/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	6580b7095788035ac526550c5e179d50
# ./create-crates.sh
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	760b984b0a30a1cd7b47c189255f639c
Patch0:		x32.patch
URL:		https://github.com/PyO3/maturin
BuildRequires:	cargo
BuildRequires:	diffstat
BuildRequires:	rpmbuild(macros) >= 2.004
BuildRequires:	rust
%if %{with python3}
BuildRequires:	python3-build
BuildRequires:	python3-installer
BuildRequires:	python3-modules >= 1:3.2
BuildRequires:	python3-setuptools_rust >= 1.11.0
%endif
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Build and publish crates with pyo3, rust-cpython and cffi bindings as
well as rust binaries as python packages.

%package -n python3-%{module}
Summary:	Maturin bindings for Python
Group:		Libraries/Python
Requires:	python3-modules >= 1:3.2
Requires:	%{name} = %{version}-%{release}

%description -n python3-%{module}
Maturin bindings for Python.

%prep
%setup -q -a1

%{__mv} maturin-%{crates_ver}/* .
sed -i -e 's/@@VERSION@@/%{version}/' Cargo.lock

diffstat -l -p1 %{PATCH0} | xargs sha256sum > x32.patch.sha256
%patch -P0 -p1
cat x32.patch.sha256 | while read old_sum f; do
  new_sum=$(sha256sum $f | cut -f1 -d' ')
  test "$old_sum" != "$new_sum"
  %{__sed} -i -e "s/$old_sum/$new_sum/" vendor/ring/.cargo-checksum.json
done

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"

%cargo_build --frozen

%if %{with python3}
export RUSTFLAGS="%{rpmrustflags}"
export MATURIN_SETUP_ARGS="%__cargo_common_opts --target %rust_target --target-dir %cargo_targetdir"
%py3_build_pyproject
%endif

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"

%cargo_install --frozen --root $RPM_BUILD_ROOT%{_prefix} --path $(pwd)

%if %{with python3}
export RUSTFLAGS="%{rpmrustflags}"
export MATURIN_SETUP_ARGS="%__cargo_common_opts --target %rust_target --target-dir %cargo_targetdir"
%{__rm} $RPM_BUILD_ROOT%{_bindir}/maturin
%py3_install_pyproject
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog.md README.md
%attr(755,root,root) %{_bindir}/maturin

%if %{with python3}
%files -n python3-%{module}
%defattr(644,root,root,755)
%{py3_sitedir}/%{module}
%{py3_sitedir}/%{module}-%{version}.dist-info
%endif
