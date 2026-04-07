{
  description = "LiteV environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python3
            pkgs.uv
          ];

          shellHook = ''
            echo "TinyEvo development environment"
            # Install the project in editable mode with dev dependencies
            uv pip install -e .[dev]
          '';
        };
      });
}