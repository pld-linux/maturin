#
# Conditional build:
%bcond_without	python3		# Python (3.x) module

%define		module		maturin
%define		crates_ver	%{version}

Summary:	Build and publish Rust crates as Python packages
Summary(pl.UTF-8):	Budowanie i publikowanie pak Rusta jako pakietów Pythonowych
Name:		maturin
Version:	1.9.4
Release:	1
License:	MIT or Apache v2.0
Group:		Development/Tools
Source0:	https://github.com/PyO3/maturin/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	71042be87f337dad340976d78c1bcccf
# poldek -uvg cargo-vendor-filterer
# cargo vendor-filterer --platform='*-unknown-linux-*' --tier=2
# tar cJf maturin-crates-%{version}.tar.xz vendor Cargo.lock
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	73a4fb0a11a68fabce99a003c8d82280
Patch0:		x32.patch
URL:		https://github.com/PyO3/maturin
BuildRequires:	bzip2-devel
BuildRequires:	cargo
BuildRequires:	diffstat
BuildRequires:	pkgconfig
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.050
BuildRequires:	rust >= 1.74
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	xz-devel
%if %{with python3}
BuildRequires:	python3-build
BuildRequires:	python3-installer
BuildRequires:	python3-modules >= 1:3.7
BuildRequires:	python3-setuptools >= 1:77.0.0
BuildRequires:	python3-setuptools_rust >= 1.11.0
%if "%{_ver_lt %{py3_ver} 3.11}" == "1"
BuildRequires:	python3-tomli >= 1.1.0
%endif
%endif
%{?rust_req}
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Build and publish crates with pyo3, rust-cpython and cffi bindings as
well as rust binaries as Python packages.

%description -l pl.UTF-8
Budowanie i publikowanie pak przy użyciu wiązań pyo3, rust-cpython i
cffi, a także binariów Rusta jako pakietów Pythona.

%package -n python3-%{module}
Summary:	Maturin bindings for Python
Summary(pl.UTF-8):	Wiązania Maturina dla Pythona
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}
Requires:	python3-modules >= 1:3.7

%description -n python3-%{module}
Maturin bindings for Python.

%description -n python3-%{module} -l pl.UTF-8
Wiązania Maturina dla Pythona.

%prep
%setup -q -a1

%{__sed} -i -e 's/@@VERSION@@/%{version}/' Cargo.lock

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
export MATURIN_SETUP_ARGS="%__cargo_common_opts --target %rust_target --target-dir %cargo_targetdir"
%py3_build_pyproject
%endif

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"

%cargo_install --frozen --root $RPM_BUILD_ROOT%{_prefix} --path $(pwd)

%if %{with python3}
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
