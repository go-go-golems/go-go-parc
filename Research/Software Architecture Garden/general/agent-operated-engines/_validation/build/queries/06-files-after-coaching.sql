-- Files created or modified after the second user message (the coaching prompt), with counts.
WITH coach AS (
  SELECT session_id, MIN(turn_index) AS t FROM turns
  WHERE role = 'user' AND turn_index > (SELECT MIN(turn_index) FROM turns t2 WHERE t2.role = 'user' AND t2.session_id = turns.session_id)
  GROUP BY session_id)
SELECT tc.file_path, tc.operation_type AS op, COUNT(*) AS n
FROM tool_calls tc JOIN coach c ON c.session_id = tc.session_id
WHERE tc.emitting_turn_index > c.t AND tc.operation_type IN ('NEW', 'MODIFY') AND COALESCE(tc.file_path, '') <> ''
GROUP BY tc.file_path, tc.operation_type ORDER BY tc.file_path;
