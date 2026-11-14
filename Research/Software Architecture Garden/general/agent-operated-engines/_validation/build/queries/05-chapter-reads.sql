-- When and how the agent consulted the chapter and the task.
SELECT emitting_turn_index AS turn, tool_name,
       substr(replace(COALESCE(NULLIF(file_path, ''), command, arguments_json), char(10), ' '), 1, 100) AS target
FROM tool_calls
WHERE COALESCE(file_path, '') LIKE '%CHAPTER.md%' OR COALESCE(command, arguments_json) LIKE '%CHAPTER.md%'
   OR COALESCE(file_path, '') LIKE '%TASK.md%' OR COALESCE(command, arguments_json) LIKE '%TASK.md%'
ORDER BY emitting_turn_index;
