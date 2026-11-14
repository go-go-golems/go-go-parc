-- Every tool call in order: what the agent did, step by step.
SELECT emitting_turn_index AS turn, tool_name, operation_type AS op,
       COALESCE(NULLIF(file_path, ''), substr(replace(COALESCE(command, arguments_json), char(10), ' '), 1, 110)) AS target,
       success, exit_code
FROM tool_calls ORDER BY session_id, emitting_turn_index, tool_call_id;
