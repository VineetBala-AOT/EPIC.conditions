import { DocumentStatus } from "@/models/Document";

/**
 * Status roll-up helpers shared by the condition header, conditions list, and
 * consolidated views so every badge agrees on the same 3-state model:
 *
 *   "nodata" (Data Entry Required) < "false" (Awaiting Confirmation) < "true" (Confirmed)
 *
 * The overall status of a condition is the lowest status among its parts. The
 * "Data Entry Required" signal depends on per-package data that a list/consolidated
 * row does not hold, so it is computed on the server and delivered as `status`.
 * The confirmed/awaiting distinction is derived from whatever approval booleans the
 * client currently holds — on the detail page all three update optimistically, while
 * list/consolidated rows carry only the server-combined `is_approved` — so the badge
 * reacts immediately to a confirm/un-confirm without waiting for a refetch.
 */

type ConditionStatusInput = {
  status?: DocumentStatus | null;
  is_approved?: boolean | null;
  is_topic_tags_approved?: boolean | null;
  is_condition_attributes_approved?: boolean | null;
};

export const deriveConditionStatus = (
  condition: ConditionStatusInput
): DocumentStatus => {
  // "Data Entry Required" is the lowest status and can only be known from the
  // server roll-up, so let it win when present.
  if (condition.status === "nodata") return "nodata";

  const fullyApproved =
    condition.is_approved === true &&
    condition.is_topic_tags_approved !== false &&
    condition.is_condition_attributes_approved !== false;

  return fullyApproved ? "true" : "false";
};

/**
 * Roll a collection of conditions up to a single badge status (lowest wins):
 * any "nodata" -> "nodata", otherwise all "true" -> "true", otherwise "false".
 */
export const rollupConditionsStatus = (
  conditions?: ConditionStatusInput[] | null
): DocumentStatus => {
  if (!conditions || conditions.length === 0) return "nodata";

  const statuses = conditions.map(deriveConditionStatus);
  if (statuses.some((s) => s === "nodata")) return "nodata";
  if (statuses.every((s) => s === "true")) return "true";
  return "false";
};
