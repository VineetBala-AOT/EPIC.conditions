import { submitRequest } from "@/utils/axiosUtils";
import { useMutation } from "@tanstack/react-query";
import { useInvalidateConditionApprovalCaches } from "./useInvalidateConditionApprovalCaches";
import { Options } from "./types";

export const usePatchIEMTerms = (
  termsId?: string,
  conditionId?: number,
  options?: Options
) => {
  const invalidateApprovalCaches = useInvalidateConditionApprovalCaches();
  return useMutation({
    mutationFn: (payload: Partial<{ name: string; is_approved: boolean }>) => {
      if (!termsId) {
        return Promise.reject(new Error("IEM Terms ID is required"));
      }
      return submitRequest({
        url: `/iemterms/${termsId}`,
        method: "patch",
        data: payload,
      });
    },
    ...options,
    onSuccess: (data) => {
      // The condition's approval flag may have been recomputed server-side
      // (e.g. approving/unapproving this terms package) — refresh condition
      // details, the document listing, and the consolidated conditions page
      // so they all pick up the authoritative value without a manual refresh.
      if (conditionId) {
        invalidateApprovalCaches();
      }
      options?.onSuccess?.(data);
    },
  });
};

const removeIEMTerms = (termsId: string) => {
  return submitRequest({
    url: `/iemterms/${termsId}`,
    method: "delete",
  });
};

export const useRemoveIEMTerms = (conditionId?: number, options?: Options) => {
  const invalidateApprovalCaches = useInvalidateConditionApprovalCaches();
  return useMutation({
    mutationFn: (termsId: string) => {
      if (!termsId) {
        return Promise.reject(new Error("IEM Terms ID is required"));
      }
      return removeIEMTerms(termsId);
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
