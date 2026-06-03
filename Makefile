# vim: ts=2 sw=2 sts=2 et :
SHELL := /bin/bash
OPEN  := $(shell command -v open 2>/dev/null || command -v xdg-open 2>/dev/null || echo true)
need   = @command -v $(1) >/dev/null || { printf "missing: %s (needed for %s)\n" $(1) $(2); exit 1; }

## defaults (override at CLI: make <target> VAR=val) ----------

Theme ?= https://github.com/catppuccin/nvim # for sh, vi
Site  ?= http://localhost:4000              # for serve (jekyll preview URL)
Port  ?= 4000                               # for serve (jekyll bind port)
BrewR ?= $(shell brew --prefix ruby 2>/dev/null)/bin # for serve (brew ruby override)
GemB  ?= $(HOME)/.gem/ruby/4.0.0/bin        # for serve (user gem bin)
F     ?= $(firstword $(wildcard docs/*.md)) # for vi
Live  ?= https://sci4seng.github.io/core    # for verify-live (live site URL)

## ---------------------------------------------------------------

help: ## show help
	@gawk 'BEGIN {FS = ":.*?##"; \
	         printf "\nUsage:\n  make \033[36m<target>\033[0m [VAR=val ...]\n\ntargets:\n"} \
	       /^[~a-zA-Z0-9_%\.\/ -]+:.*?##/ { \
	         printf("  \033[36m%-20s\033[0m %s\n", $$1, $$2) | "sort" }' $(MAKEFILE_LIST)
	@printf "\ndefaults:\n"
	@gawk 'match($$0, /^([A-Za-z][A-Za-z0-9]*)[ \t]*\?=[ \t]*([^#]*[^# \t])[ \t]*#[ \t]*(.+)/, a) { \
	         printf("  \033[36m%-8s\033[0m = %-30s %s\n", a[1], a[2], a[3]) | "sort" }' $(MAKEFILE_LIST)

## site -----------------------------------------------------------

regen: ## regenerate docs/ markdown from paper/outputs/*.csv
	$(call need,python3,regen)
	@python3 docs/scripts/gen_md.py

serve: regen ## bundle install + jekyll serve at $(Site) (URL printed)
	$(call need,bundle,serve)
	@cd docs && PATH="$(BrewR):$(GemB):$$PATH" bundle install --quiet
	@printf "\n\033[1;36m================================================\033[0m\n"
	@printf "\033[1;32m  SITE READY  →  $(Site)\033[0m\n"
	@printf "\033[1;36m================================================\033[0m\n"
	@printf "  Cmd-click the URL, or:  \033[33mopen $(Site)\033[0m\n"
	@printf "  Stop:  Ctrl-C\n\n"
	@cd docs && PATH="$(BrewR):$(GemB):$$PATH" bundle exec jekyll serve \
	  --port $(Port) --livereload

serve-open: regen ## serve + auto-open browser to $(Site)
	$(call need,bundle,serve-open)
	@cd docs && PATH="$(BrewR):$(GemB):$$PATH" bundle install --quiet
	@printf "\n\033[1;32m  SITE READY  →  $(Site)\033[0m  (opening browser)\n\n"
	@( sleep 2 && $(OPEN) $(Site) ) &
	@cd docs && PATH="$(BrewR):$(GemB):$$PATH" bundle exec jekyll serve \
	  --port $(Port) --livereload

build: regen ## build static site to docs/_site/
	$(call need,bundle,build)
	@cd docs && PATH="$(BrewR):$(GemB):$$PATH" bundle exec jekyll build

clean-site: ## wipe Jekyll build artifacts
	@rm -rf docs/_site docs/.jekyll-cache docs/.bundle docs/vendor; \
	 echo "wiped docs/_site + caches"

## inference (delegate to paper/Makefile) -------------------------

refresh: ## run paper pipeline + regen site
	@$(MAKE) -C paper refresh
	@$(MAKE) regen

## git -----------------------------------------------------------

push: ## prompt msg, commit -am, push
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status

publish: refresh ## refresh + git add -A + commit + push + wait + open live URL
	@read -p "Commit msg? " msg; git add -A && git commit -m "$$msg" && git push
	@printf "\n\033[1;33m  waiting 30s for GH Pages to rebuild...\033[0m\n"
	@sleep 30
	@printf "\033[1;32m  opening $(Live)\033[0m\n"
	@$(OPEN) $(Live)

verify-live: ## curl $(Live) and check K1–K3 (title, findings, typology)
	$(call need,curl,verify-live)
	@printf "Checking %s ...\n\n" "$(Live)"
	@U="$(Live)"; pass=0; fail=0; \
	probe() { local label="$$1" url="$$2" pat="$$3"; \
	  local body=$$(curl -sL --max-time 15 "$$url"); \
	  if [ -z "$$body" ]; then printf "  \033[31m✗\033[0m %-30s 0 bytes / unreachable\n" "$$label"; fail=$$((fail+1)); return; fi; \
	  if echo "$$body" | grep -qE "$$pat"; then \
	    printf "  \033[32m✓\033[0m %-30s matched: %s\n" "$$label" "$$pat"; pass=$$((pass+1)); \
	  else \
	    printf "  \033[31m✗\033[0m %-30s MISSING: %s   (at %s)\n" "$$label" "$$pat" "$$url"; fail=$$((fail+1)); \
	  fi; }; \
	probe "K1 title"          "$$U/"            "MYTHS"; \
	probe "K1 subtitle"       "$$U/"            "Models Yielding Testable Hypotheses"; \
	probe "K2 findings F0"    "$$U/findings/"   "F0"; \
	probe "K2 findings F3"    "$$U/findings/"   "F3"; \
	probe "K3 typology univ"  "$$U/typology/"   "universal"; \
	probe "K3 typology proc"  "$$U/typology/"   "process-conditional"; \
	probe "K3 typology frag"  "$$U/typology/"   "fragile"; \
	probe "K3 typology world" "$$U/typology/"   "world-conditional"; \
	probe "Models index"      "$$U/models/"     "brooks"; \
	probe "Model: brooks"     "$$U/models/brooks/" "fragile"; \
	printf "\nResult: \033[32m%d pass\033[0m / \033[31m%d fail\033[0m\n" "$$pass" "$$fail"; \
	[ "$$fail" -eq 0 ]

## doctor + shell ------------------------------------------------

doctor: ## check required tools (✓ found, ✗ missing)
	@for e in \
	   "python3|regen target, paper pipeline" \
	   "bundle|serve + build (jekyll)" \
	   "ruby|serve (>= 3.0 required by jekyll deps)" \
	   "gawk|help target (self-doc)" \
	   "git|push target" \
	   "nvim|vi target"; do \
	   c=$${e%%|*}; use=$${e##*|}; \
	   if command -v $$c >/dev/null; then \
	     printf "  \033[32m✓\033[0m %-10s used by: %s\n" "$$c" "$$use"; \
	   else \
	     printf "  \033[31m✗\033[0m %-10s missing — can't: %s\n" "$$c" "$$use"; fi; done
	@printf "\nruby version (must be ≥ 3.0):\n"
	@PATH="$(BrewR):$$PATH" ruby --version 2>/dev/null || echo "  no ruby on PATH"
	@printf "\nmacOS: brew install ruby gawk neovim && gem install bundler\n"

define BASHRC
set -o vi
# Force Homebrew Ruby + user-gem bin ahead of system Ruby (system = 2.6, too old for jekyll)
export PATH="$(BrewR):$(GemB):$$PATH"
__gp(){ local b=$$(git branch --show-current 2>/dev/null); [[ -z $$b ]] && return
  [[ -n $$(git status --porcelain 2>/dev/null) ]] && b="$$b*"; echo " $$b"; }
__pw(){ pwd | awk -F/ '{print $$(NF-1)"/"$$NF}'; }
PS1='\[\e[36m\]$$(__pw)\[\e[33m\]$$(__gp) \[\e[0m\][\!]\$$ '
export CLICOLOR=1
export LSCOLORS=ExGxBxDxCxEgEdxbxgxcxd
if command ls --color=auto / >/dev/null 2>&1; then alias ls='ls --color=auto'; else alias ls='ls -G'; fi
alias grep='grep --color=auto' less='less -R' ll='ls -la' gs='git status -s' gd='git diff' gl='git log --oneline -20'
alias serve='cd $$(git rev-parse --show-toplevel)/docs && bundle exec jekyll serve --port $(Port) --livereload'
alias regen='cd $$(git rev-parse --show-toplevel) && python3 docs/scripts/gen_md.py'
# catppuccin: clone once per shell, wipe on exit; vi reuses it
D=$$(mktemp -d); trap 'rm -rf "$$D"' EXIT
git clone -q --depth 1 $(Theme) "$$D/cat" 2>/dev/null
printf '%s\n' "$$VIMRC" > "$$D/vimrc"
alias vi='nvim --clean -u "$$D/vimrc" -c "set rtp^=$$D/cat" -c "colorscheme catppuccin-mocha"'
echo "[sci4seng/core shell] ruby: $$(ruby --version 2>/dev/null | head -1)"
echo "  aliases: serve, regen, gs, gd, gl, ll, vi"
endef
export BASHRC

sh: ## launch tuned bash w/ brew-ruby PATH + catppuccin (wiped on exit)
	$(call need,bash,sh)
	@bash --rcfile <(echo "$$BASHRC") -i

define VIMRC
set nu rnu cursorline mouse=a termguicolors et ts=2 sw=2 sts=2 ai si
set ignorecase smartcase hlsearch incsearch scrolloff=8 signcolumn=yes
set splitbelow splitright wrap linebreak wildmenu clipboard=unnamedplus
syntax on | filetype plugin indent on
endef
export VIMRC

vi: ## launch tuned nvim + catppuccin (wiped on exit)
	$(call need,nvim,vi)
	$(call need,git,vi)
	@D=$$(mktemp -d); trap "rm -rf $$D" EXIT; \
	 git clone -q --depth 1 $(Theme) $$D/cat; \
	 printf '%s\n' "$$VIMRC" > $$D/vimrc; \
	 nvim --clean -u $$D/vimrc -c "set rtp^=$$D/cat" \
	      -c "colorscheme catppuccin-mocha" $F
