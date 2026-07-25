#!/usr/bin/env bash
# Apply a repository refquota and daily 14-day ZFS snapshot task on TrueNAS.
# Run from an authorized operator workstation with admin TrueNAS SSH access.
#
# Usage:
#   MACHINE=mimimi-2 ./02-configure-truenas-protection.sh
#   REFQUOTA_BYTES=2199023255552 MACHINE=f ./02-configure-truenas-protection.sh  # 2 TiB
set -euo pipefail
source "$(dirname "$0")/00-restic-crib-env.sh"

echo "Configuring TrueNAS protection for: $DATASET"
echo "  refquota:        $REFQUOTA_BYTES bytes"
echo "  snapshot schema: $SNAPSHOT_SCHEMA"
echo "  snapshot task:   daily 10:00, 14-day lifetime"
echo ""

ssh -o BatchMode=yes -o ConnectTimeout=10 "${TRUENAS_ADMIN}@${TRUENAS_HOST}" \
  "DATASET='$DATASET' REFQUOTA='$REFQUOTA_BYTES' SNAPSHOT_SCHEMA='$SNAPSHOT_SCHEMA' bash -s" <<'REMOTE'
set -euo pipefail

midclt call pool.dataset.update "$DATASET" "{\"refquota\":\"$REFQUOTA\"}" >/dev/null
echo "applied refquota to $DATASET"

tasks="$(midclt call pool.snapshottask.query "[[\"dataset\",\"=\",\"$DATASET\"]]")"
if [[ "$tasks" == "[]" ]]; then
  midclt call pool.snapshottask.create "{\"dataset\":\"$DATASET\",\"recursive\":false,\"lifetime_value\":14,\"lifetime_unit\":\"DAY\",\"naming_schema\":\"$SNAPSHOT_SCHEMA\",\"schedule\":{\"minute\":\"0\",\"hour\":\"10\",\"dom\":\"*\",\"month\":\"*\",\"dow\":\"*\"},\"enabled\":true}" >/dev/null
  echo "created daily 10:00 TrueNAS snapshot task with 14-day retention"
else
  echo "snapshot task already exists for $DATASET"
fi

echo ""
echo "--- dataset ---"
midclt call pool.dataset.query "[[\"id\",\"=\",\"$DATASET\"]]" |
  jq -c '.[] | {id,refquota,used,available}'
echo "--- snapshot task ---"
midclt call pool.snapshottask.query "[[\"dataset\",\"=\",\"$DATASET\"]]" |
  jq -c '.[] | {id,dataset,recursive,lifetime_value,lifetime_unit,naming_schema,schedule,enabled}'
REMOTE
