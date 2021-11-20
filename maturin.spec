%define		crates_ver	0.10.3

Summary:	Build and publish rust crates as python packages
Name:		maturin
Version:	0.10.3
Release:	2
License:	MIT or Apache v2.0
Group:		Applications
Source0:	https://github.com/PyO3/maturin/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	b1d821f86a97dc10648f38aa2c6a8540
# ./create-crates.sh
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	1b5a724601e35752b98b5ad8afc2a2b1
URL:		https://github.com/PyO3/maturin
BuildRequires:	cargo
BuildRequires:	rpmbuild(macros) >= 2.004
BuildRequires:	rust
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Build and publish crates with pyo3, rust-cpython and cffi bindings as
well as rust binaries as python packages.

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

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"

%cargo_install --frozen --root $RPM_BUILD_ROOT%{_prefix} --path $(pwd)
%{__rm} $RPM_BUILD_ROOT%{_prefix}/.crates*

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog.md Readme.md
%attr(755,root,root) %{_bindir}/maturin
