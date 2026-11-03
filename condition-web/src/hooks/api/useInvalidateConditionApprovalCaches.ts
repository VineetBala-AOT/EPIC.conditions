import { useQueryClient } from "@tanstack/react-query";
import { useParams } from "@tanstack/react-router";
import { useCallback } from "react";
import { invalidateConditionApprovalCaches } from "./constants";

// Route-aware wrapper around invalidateConditionApprovalCaches. Every mutation
// that can change a condition's approval status is fired from a page nested
// under the `$projectId` route, so the current route param is the project that
// owns the mutated condition. Reading it here (with strict: false, so it is
// simply undefined when no project is in scope) keeps the project id in one
// place instead of threading it through every mutation hook and component. When
// it is undefined the underlying helper falls back to a broad, all-projects
// invalidation, which is still correct.
export const useInvalidateConditionApprovalCaches = () => {
  const queryClient = useQueryClient();
  const { projectId } = useParams({ strict: false }) as { projectId?: string };
  return useCallback(
    () => invalidateConditionApprovalCaches(queryClient, projectId),
    [queryClient, projectId],
  );
};
