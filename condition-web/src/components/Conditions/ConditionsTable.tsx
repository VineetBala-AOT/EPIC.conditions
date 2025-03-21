import {
    Box,
    Table,
    TableBody,
    TableContainer,
    TableHead,
    TableRow,
  } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { ConditionModel } from "@/models/Condition";
import { StyledTableHeadCell } from "../Shared/Table/common";
import ConditionTableRow from "./ConditionTableRow";
import { DocumentTypes } from "@/utils/enums"

export default function ConditionTable({
    conditions,
    projectId,
    documentId,
    headless,
    noConditions,
    documentTypeId,
    tableType
}: {
    conditions: Array<ConditionModel>;
    projectId: string;
    documentId: string;
    headless?: boolean;
    noConditions: boolean;
    documentTypeId: number;
    tableType: string;
}) {
    return (
        <TableContainer component={Box} sx={{ height: "100%", overflowY: 'auto', minWidth: 1000 }}>
            <Table sx={{ tableLayout: "fixed", border: 0 }} aria-label="simple table">
            {!headless && (
                <TableHead
                sx={{
                    border: 0,
                    ".MuiTableCell-root": {
                    p: BCDesignTokens.layoutPaddingXsmall,
                    },
                }}
                >
                    <TableRow>
                        <StyledTableHeadCell colSpan={2}>
                            Condition Number
                        </StyledTableHeadCell>
                        <StyledTableHeadCell colSpan={6}>
                            Condition Name
                        </StyledTableHeadCell>
                        {documentTypeId !== DocumentTypes.Amendment && (
                            <StyledTableHeadCell colSpan={2} align="right">
                                Amendment In
                            </StyledTableHeadCell>
                        )}
                        <StyledTableHeadCell colSpan={2} align="right">
                            Tags
                        </StyledTableHeadCell>
                        <StyledTableHeadCell colSpan={2} align="right">
                            Year Issued
                        </StyledTableHeadCell>
                        {tableType == "consolidated" && (
                            <StyledTableHeadCell colSpan={2} align="right">
                                Source Document
                            </StyledTableHeadCell>
                        )}
                        <StyledTableHeadCell colSpan={2} align="center">
                            Standard Condition
                        </StyledTableHeadCell>
                        <StyledTableHeadCell colSpan={2} align="center">
                            Status
                        </StyledTableHeadCell>
                    </TableRow>
                </TableHead>
            )}
            <TableBody>
            {!noConditions && conditions?.map((condition) => (
                <ConditionTableRow
                    key={condition.condition_id}
                    condition={condition}
                    projectId={projectId}
                    documentId={documentId}
                    documentTypeId={documentTypeId}
                    tableType={tableType}
                />
            ))}
            </TableBody>
            </Table>
        </TableContainer>
    );
}
