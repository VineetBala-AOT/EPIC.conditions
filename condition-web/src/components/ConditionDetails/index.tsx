import { useEffect, useRef, useState } from "react";
import { BCDesignTokens } from "epic.theme";
import { createDefaultCondition, ProjectDocumentConditionDetailModel } from "@/models/Condition";
import { Box, Stack } from "@mui/material";
import { ContentBoxSkeleton } from "../Shared/ContentBox/ContentBoxSkeleton";
import { styled } from "@mui/system";
import ConditionInfoTabs from "./ConditionInfoTabs";
import ConditionHeader from "./ConditionHeader";

export const CardInnerBox = styled(Box)({
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "center",
  flexDirection: "column",
  height: "100%",
  padding: "0 12px",
});

type ConditionsParam = {
  initialCondition?: ProjectDocumentConditionDetailModel;
  projectId: string;
  documentId: string;
  conditionId: number;
};

export const ConditionDetails = ({
  initialCondition,
  projectId,
  documentId,
  conditionId
}: ConditionsParam) => {

  const [condition, setCondition] = useState(() => initialCondition?.condition || createDefaultCondition());

  // On a DIFFERENT condition, replace local state wholesale. On a refetch of the
  // SAME condition (e.g. after adding/approving a management plan, IEM terms
  // package, or report), only merge in the server-authoritative approval/
  // requirement flags — these are never locally edited, so the server is always
  // right — while leaving condition_attributes/subconditions untouched so an
  // in-progress local edit never gets clobbered by a refetch.
  const loadedConditionIdRef = useRef(initialCondition?.condition?.condition_id);
  useEffect(() => {
    if (!initialCondition?.condition) {
      return;
    }
    const incoming = initialCondition.condition;
    if (loadedConditionIdRef.current !== incoming.condition_id) {
      setCondition(incoming);
    } else {
      setCondition((prev) => ({
        ...prev,
        is_approved: incoming.is_approved,
        is_condition_attributes_approved: incoming.is_condition_attributes_approved,
        is_topic_tags_approved: incoming.is_topic_tags_approved,
        // Server-authoritative rolled-up badge status. Without merging this, the
        // header keeps showing the stale status (e.g. "Data Entry Required") after a
        // management plan / IEM / report is filled in and approved, until a full
        // page refresh re-initialises state. See deriveConditionStatus.
        status: incoming.status,
        requires_management_plan: incoming.requires_management_plan,
        requires_iem_terms: incoming.requires_iem_terms,
        requires_report: incoming.requires_report,
      }));
    }
    loadedConditionIdRef.current = incoming.condition_id;
  }, [initialCondition]);

  return (
    <Stack spacing={2} direction={"column"} sx={{ width: '100%' }}>
      <Box
        sx={{
          borderRadius: "3px",
          border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
          boxShadow: "0px 1px 2px rgba(0, 0, 0, 0.1)",
        }}
      >
        <ConditionHeader
          conditionId={conditionId}
          projectName={initialCondition?.project_name || ""}
          documentLabel={initialCondition?.document_label || ""} 
          condition={condition}
          setCondition={setCondition}
        />
      </Box>

      <Box
        sx={{
          borderRadius: "3px",
          boxShadow: "0px 2px 2px rgba(0, 0, 0, 0.1)",
          paddingTop: "0.5em"
        }}
      >
        <ConditionInfoTabs
          projectId={projectId}
          documentId={documentId}
          conditionId={conditionId}
          condition={condition}
          setCondition={setCondition}
        />
      </Box>
    </Stack>
  );
};

export const ConditionDetailsSkeleton = () => {
  return (
    <Stack spacing={2} direction={"column"} sx={{ width: '100%' }}>
      <ContentBoxSkeleton />
      <ContentBoxSkeleton />
      <ContentBoxSkeleton />
    </Stack>
  );
};
