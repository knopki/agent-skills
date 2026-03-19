{ pkgs, ... }:
{
  knopki = {
    git = {
      enable = true;
      withGitHooks = true;
    };
    markdown = {
      enable = true;
      format.enable = true;
      lychee.enable = true;
      markdownlint.enable = true;
    };
    menu.enable = true;
    shell = {
      enable = true;
      lsp.enable = true;
      shellcheck.enable = true;
      shfmt.enable = true;
    };
    yaml = {
      enable = true;
      format.enable = true;
      yamllint.enable = true;
    };
  };

  git-hooks = {
    enable = true;
    hooks = {
      agentskills = {
        enable = true;
        name = "agentskills";
        description = "Validate skills";
        package = pkgs.uv;
        entry = "uvx --from skills-ref agentskills validate";
        files = "SKILL\\.md$";
      };
    };
  };
  treefmt = {
    enable = true;
    config.programs.ruff-check.enable = true;
    config.programs.ruff-format.enable = true;
  };

  languages = {
    javascript.enable = true;
    python = {
      enable = true;
      uv.enable = true;
    };
  };

  scripts = {
    agentskills.exec = ''
      exec uvx --from skills-ref agentskills $@
    '';
  };
}
