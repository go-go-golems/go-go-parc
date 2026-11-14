-- Shape of each build session.
SELECT session_id, model, duration_seconds, turn_count, tool_call_count,
       read_count, create_count, modify_count, execute_count
FROM sessions ORDER BY started_at;
