%bcond_without	python3

%define		module		maturin
%define		crates_ver	1.8.2

Summary:	Build and publish rust crates as python packages
Name:		maturin
Version:	1.8.2
Release:	1
License:	MIT or Apache v2.0
Group:		Applications
Source0:	https://github.com/PyO3/maturin/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	762eaadba0e0a250a30892c8d17c32a2
# ./create-crates.sh
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	c15d367a752fc0c9997eb4c6a95f7df5
URL:		https://github.com/PyO3/maturin
BuildRequires:	cargo
BuildRequires:	rpmbuild(macros) >= 2.004
BuildRequires:	rust
%if %{with python3}
BuildRequires:	python3-modules >= 1:3.2
BuildRequires:	python3-setuptools_rust >= 1.0
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
%py3_build
%endif

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"

%cargo_install --frozen --root $RPM_BUILD_ROOT%{_prefix} --path $(pwd)
%{__rm} $RPM_BUILD_ROOT%{_prefix}/.crates*

%if %{with python3}
%py3_install
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
%{py3_sitedir}/%{module}-%{version}-py*.egg-info
%endif
