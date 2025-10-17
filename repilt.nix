{ pkgs }:
let
  python = pkgs.python310Full;
  prybar = pkgs.replitPackages.prybar-python310 or null;
  stderred = pkgs.replitPackages.stderred or null;
in {
  deps = [
    python
    prybar
    stderred
  ];

  env = {
    # makeLibraryPath expects a list of packages; use stdenv.cc (compiler runtime) rather than cc.cc.lib
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc
      pkgs.zlib
      pkgs.glib
      pkgs.xorg.libX11
    ];

    # Use the concrete python path and python binary explicitly
    PYTHONHOME = toString python;
    PYTHONBIN = "${toString python}/bin/python3.10";

    LANG = "en_US.UTF-8";

    # Only set these if the packages exist, otherwise set an empty string so the env var is defined
    STDERREDBIN = if stderred != null then "${toString stderred}/bin/stderred" else "";
    PRYBAR_PYTHON_BIN = if prybar != null then "${toString prybar}/bin/prybar-python310" else "";
  };
}
