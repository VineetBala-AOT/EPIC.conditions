import { useEffect } from "react";
import { Else, If, Then } from "react-if";
import { PageGrid } from "@/components/Shared/PageGrid";
import { Grid } from "@mui/material";
import { createFileRoute, Navigate, useParams } from "@tanstack/react-router";
import { useLoadConditionDetails } from "@/hooks/api/useConditions";
import { ConditionDetails, ConditionDetailsSkeleton } from "@/components/ConditionDetails";
import { notify } from "@/components/Shared/Snackbar/snackbarStore";
import { useBreadCrumb } from "@/components/Shared/layout/SideNav/breadCrumbStore";

export const Route = createFileRoute(
  "/_authenticated/_dashboard/conditions/project/$projectId/document/$documentId/condition/$conditionNumber/"
)({
  component: ConditionPage,
  notFoundComponent: () => {
    return <p>Condition not found!</p>;
  },
  meta: ({ params }) => [
    { title: "Home", path: "/projects/" },
    { title: `${params.projectId}`, path: `/projects/` }, // Fixed Projects path
    { title: `${params.documentId}`, path: `/_authenticated/_dashboard/conditions/project/${params.projectId}/document/${params.documentId}/condition/$conditionNumber/` } // Path to the specific document
  ],
});

function ConditionPage() {
  const { projectId: projectIdParam, documentId: documentIdParam, conditionNumber: conditionNumberParam } = useParams({ strict: false });
  const projectId = String(projectIdParam);
  const documentId = String(documentIdParam);
  const conditionNumber = Number(conditionNumberParam);

  const {
    data: conditionDetails,
    isPending: isConditionsLoading,
    isError: isConditionsError
  } = useLoadConditionDetails(projectId, documentId, conditionNumber);

  useEffect(() => {
    if (isConditionsError) {
      notify.error("Failed to load condition");
    }
  }, [isConditionsError]);

  if (isConditionsError) return <Navigate to="/error" />;

  const META_PROJECT_TITLE = `${projectId}`;
  const META_DOCUMENT_TITLE = `${documentId}`;
  const { replaceBreadcrumb } = useBreadCrumb();
  useEffect(() => {
    if (conditionDetails) {
      replaceBreadcrumb(META_PROJECT_TITLE, conditionDetails?.project_name || "");
      replaceBreadcrumb(META_DOCUMENT_TITLE, conditionDetails?.document_type || "");
    }
  }, [conditionDetails, replaceBreadcrumb, META_PROJECT_TITLE, META_DOCUMENT_TITLE]);

  return (
    <PageGrid>
      <Grid item xs={12}>
        <If condition={isConditionsLoading}>
          <Then>
            <ConditionDetailsSkeleton />
          </Then>
          <Else>
            <ConditionDetails
              projectName = {conditionDetails?.project_name || ""}
              documentName = {conditionDetails?.display_name || ""}
              condition={conditionDetails?.condition}
            />
          </Else>
        </If>
      </Grid>
    </PageGrid>
  );
}