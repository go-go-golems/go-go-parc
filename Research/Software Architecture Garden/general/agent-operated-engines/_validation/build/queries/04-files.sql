-- Files the agent created or modified, with how often.
SELECT file_path, operation_type AS op, COUNT(*) AS n, MIN(emitting_turn_index) AS first_turn
FROM tool_calls WHERE operation_type IN ('NEW', 'MODIFY') AND COALESCE(file_path, '') <> ''
GROUP BY file_path, operation_type ORDER BY first_turn;
