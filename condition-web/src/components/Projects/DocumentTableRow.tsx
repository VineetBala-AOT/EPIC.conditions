import { ArrowForwardIos } from "@mui/icons-material";
import { Link, TableCell, TableRow, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import DocumentStatusChip from "./DocumentStatusChip";
import { DocumentModel, DocumentStatus } from "@/models/Document";

interface ProjectRowProps {
  document: DocumentModel;
}
const border = `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`;

export default function ProjectTableRow({
    document,
}: ProjectRowProps) {
  return (
    <>
      <TableRow
        key={`row-${document.document_id}`}
        sx={{
          my: 1,
          "&:hover": {
            backgroundColor: BCDesignTokens.surfaceColorMenusHover,
          },
        }}
      >
        <TableCell
          colSpan={6}
          align="left"
          sx={{
            borderTop: border,
            borderBottom: border,
            py: BCDesignTokens.layoutPaddingXsmall,
          }}
        >
          <Link
            sx={{
              color: BCDesignTokens.themeBlue90,
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
            }}
            component={"button"}
            onClick={() => {}}
          >
            <Typography
              variant="h6"
              color={BCDesignTokens.themeBlue90}
              fontWeight={"500"}
              sx={{ mr: 0.5 }}
            >
              {document.document_type ?? "--"}
            </Typography>
            <ArrowForwardIos fontSize="small" />
          </Link>
        </TableCell>
        <TableCell
          colSpan={2}
          align="right"
          sx={{
            borderTop: border,
            borderBottom: border,
            py: BCDesignTokens.layoutPaddingXsmall,
          }}
        >
          {"--"}
        </TableCell>
        <TableCell
          colSpan={2}
          align="right"
          sx={{
            borderTop: border,
            borderBottom: border,
            py: BCDesignTokens.layoutPaddingXsmall,
          }}
        >
          {document.date_issued ? new Date(document.date_issued).getFullYear() : "--"}
        </TableCell>
        <TableCell
          colSpan={2}
          align="center"
          sx={{
            borderTop: border,
            borderBottom: border,
            py: BCDesignTokens.layoutPaddingXsmall,
          }}
        >
          <DocumentStatusChip status={document.status as DocumentStatus} />
        </TableCell>
      </TableRow>
      <TableRow key={`empty-row-${document.document_id}`} sx={{ py: 1 }}>
        <TableCell
          component="th"
          scope="row"
          colSpan={12}
          sx={{
            border: 0,
            py: BCDesignTokens.layoutPaddingXsmall,
          }}
        />
      </TableRow>
    </>
  );
}