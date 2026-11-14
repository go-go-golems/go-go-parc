-- Test runs and their outcome (the last lines of the result).
SELECT emitting_turn_index AS turn,
       substr(replace(COALESCE(command, arguments_json), char(10), ' '), 1, 90) AS command,
       exit_code,
       substr(replace(substr(result, -220), char(10), ' | '), 1, 220) AS tail
FROM tool_calls
WHERE COALESCE(command, arguments_json) LIKE '%unittest%' OR COALESCE(command, arguments_json) LIKE '%pytest%'
   OR COALESCE(command, arguments_json) LIKE '%python3 -m hubreg%' OR COALESCE(command, arguments_json) LIKE '%python3 -c%'
ORDER BY emitting_turn_index;
