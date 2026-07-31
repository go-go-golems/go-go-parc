-- Session details with turns/tools and activity windows for all converted sessions.
-- Used by the daily-log batch to build per-day report bundles.
SELECT
  s.session_id,
  s.agent_framework AS framework,
  s.model,
  s.title,
  s.working_directory AS cwd,
  s.started_at,
  s.ended_at,
  s.turn_count,
  s.tool_call_count,
  (SELECT MAX(t.timestamp) FROM turns t WHERE t.session_id = s.session_id) AS last_turn_at,
  (SELECT MAX(tc.timestamp) FROM tool_calls tc WHERE tc.session_id = s.session_id) AS last_tool_at
FROM sessions s
ORDER BY s.started_at;
