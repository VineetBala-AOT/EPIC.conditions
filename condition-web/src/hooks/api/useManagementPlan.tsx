import { submitRequest } from "@/utils/axiosUtils";
import { useMutation } from "@tanstack/react-query";
import { useInvalidateConditionApprovalCaches } from "./useInvalidateConditionApprovalCaches";
import { Options } from "./types";

export const usePatchManagementPlan = (
    planId?: string,
    conditionId?: number,
    options?: Options
  ) => {
    const invalidateApprovalCaches = useInvalidateConditionApprovalCaches();
    return useMutation({
      mutationFn: (payload: Partial<{ name: string; is_approved: boolean }>) => {
        if (!planId) {
          return Promise.reject(new Error("Management Plan ID is required"));
        }
        return submitRequest({
          url: `/managementplan/${planId}`,
          method: "patch",
          data: payload,
        });
      },
      ...options,
      onSuccess: (data) => {
        // The condition's approval flag may have been recomputed server-side
        // (e.g. approving/unapproving this plan) — refresh condition details,
        // the document listing, and the consolidated conditions page so they
        // all pick up the authoritative value without a manual refresh.
        if (conditionId) {
          invalidateApprovalCaches();
        }
        options?.onSuccess?.(data);
      },
    });
  };

const removeManagementPlan = (planId: string) => {
  return submitRequest({
    url: `/managementplan/${planId}`,
    method: "delete",
  });
};

export const useRemoveManagementPlan = (conditionId?: number, options?: Options) => {
  const invalidateApprovalCaches = useInvalidateConditionApprovalCaches();
  return useMutation({
    mutationFn: (planId: string) => {
      if (!planId) {
        return Promise.reject(new Error("Plan ID is required"));
      }
      return removeManagementPlan(planId);
    },
    ...options,
    onSuccess: (data) => {
      if (conditionId) {
        invalidateApprovalCaches();
      }
      options?.onSuccess?.(data);
    },
  });
};
