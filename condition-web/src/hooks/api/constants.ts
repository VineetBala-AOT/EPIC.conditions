import { QueryClient } from "@tanstack/react-query";

export const defaultUseQueryOptions = {
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    staleTime: 1000 * 60 * 5,
    retry: false,
};

export const QUERY_KEY = Object.freeze({
    ATTRIBUTEKEYS: "attribute-keys",
    PROJECTS: "projects",
    AVAILABLE_PROJECTS: "available-projects",
    DOCUMENT: "documents",
    AVAILABLE_DOCUMENTS: "available-documents",
    DOCUMENTDETAIL: "document-details",
    PROJECTDOCUMENT: "project-documents",
    DOCUMENTTYPE: "document-type",
    SUBCONDITIONS: "subconditions",
    CONDITIONS: "conditions",
    CONDITION: "condition",
    CONDITIONSDETAIL: "condition-details",
    CONSOLIDATEDCONDITIONS: "consolidated-conditions",
    USERS: "users"
  });

// A management plan, IEM terms package, report, or report submission change
// can flip a condition's is_condition_attributes_approved flag, which in turn
// changes the combined approval status rolled up and shown on: the condition
// details page, the document-level condition listing, the project-level
// consolidated conditions page, the per-category documents listing, and the
// projects landing/detail page. Call this from every such mutation's
// onSuccess so all of them stay live without requiring a manual page
// refresh.
//
// When `projectId` is supplied, the project-scoped caches (condition details,
// condition listing, consolidated conditions, documents) are invalidated only
// for that project — a condition can only be mutated from within its own
// project's pages, so other projects' cached data is unaffected and must not be
// needlessly refetched. The projects landing is a single global list with no
// per-project key, so it is always invalidated in full. Omitting `projectId`
// falls back to invalidating every project (safe, but broader).
export const invalidateConditionApprovalCaches = (
  queryClient: QueryClient,
  projectId?: string,
) => {
  // All four of these query families key projectId as their first argument,
  // e.g. [CONDITIONS, projectId, documentId, ...], so [KEY, projectId] is a
  // partial-match prefix that scopes invalidation to the one project.
  const projectScopedKeys = [
    QUERY_KEY.CONDITIONSDETAIL,
    QUERY_KEY.CONDITIONS,
    QUERY_KEY.CONSOLIDATEDCONDITIONS,
    QUERY_KEY.DOCUMENT,
  ];
  for (const key of projectScopedKeys) {
    queryClient.invalidateQueries({
      queryKey: projectId ? [key, projectId] : [key],
    });
  }
  queryClient.invalidateQueries({ queryKey: [QUERY_KEY.PROJECTS] });
};

export const HTTP_STATUS_CODES = {
    NOT_FOUND: 404,
    FORBIDDEN: 403,
    BAD_REQUEST: 400,
    CONFLICT: 409,
    PRECONDITION_FAILED: 412,
};
