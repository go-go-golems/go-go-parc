# agent-design-review: settings shared by the scripts. Copy to env.sh, edit, then `source env.sh`.
export REPO=/path/to/your/repo            # git repository the agents work in
export BASE=HEAD                          # revision every fresh agent starts from (pin it: a hash)
export OUT=/path/to/your/ticket/various/agent-review   # where rounds, logs and results go (commit this)
export WORKTREES=$REPO/.claude/worktrees  # one worktree per agent per round is created here
export MODEL=gpt-6.2-sol                  # codex model id
export EFFORT=medium                      # codex model_reasoning_effort
export CODEX_HOME=${CODEX_HOME:-$HOME/.codex}
export AGENT_TIMEOUT=3600                 # seconds per agent
