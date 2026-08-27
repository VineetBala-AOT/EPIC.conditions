import { mount } from "cypress/react18";
import { ThemeProvider } from "@mui/material/styles";
import { theme } from "../../../src/styles/theme";
import AddReportForm from "../../../src/components/ConditionDetails/ConditionAttribute/Reports/AddReportForm";

describe("AddReportForm", () => {
  const mountForm = (props: any = {}) => {
    const onSave = cy.stub().as("onSave");
    const onCancel = cy.stub().as("onCancel");
    mount(
      <ThemeProvider theme={theme}>
        <AddReportForm onSave={onSave} onCancel={onCancel} {...props} />
      </ThemeProvider>
    );
  };

  it("shows validation errors when saving with no fields filled", () => {
    mountForm();

    cy.contains("Report Information").should("exist");
    cy.contains("Save Report").click();

    cy.contains("Report type is required.").should("exist");
    cy.contains("Please indicate the phase(s) associated with this Report.").should("exist");
    cy.contains("Frequency is required.").should("exist");
    cy.get("@onSave").should("not.have.been.called");
  });

  it("reveals PSN-specific fields and submits a valid Project Status Notification report", () => {
    mountForm();

    // Open the Report Type select and choose Project Status Notification
    cy.contains("Select report type...").click();
    cy.get('li[role="option"]').contains("Project Status Notification").click();

    // PSN-specific fields appear per submission
    cy.get('input[placeholder="e.g. 4.1"]').should("exist");
    cy.contains("Select type...").should("exist");

    // Fill the PSN "Type" select
    cy.contains("Select type...").click();
    cy.get('li[role="option"]').contains("Primary Contact Notification").click();

    // Fill subcondition number
    cy.get('input[placeholder="e.g. 4.1"]').type("4.1");

    // Select a frequency (PSN frequencies include "As Needed")
    cy.contains("Select frequency...").click();
    cy.get('li[role="option"]').contains("As Needed").click();

    // Fill timing
    cy.get('input[placeholder="e.g. within 30 days after the issuance of this Certificate."]').type(
      "Within 30 days of a contact change"
    );

    // Select the "All Phases" phase checkbox
    cy.contains("All Phases").click();

    cy.contains("Save Report").click();

    cy.get("@onSave").should("have.been.calledOnce");
    cy.get("@onSave").should((stub: any) => {
      const submitted = stub.getCall(0).args[0];
      expect(submitted.report_type).to.eq("Project Status Notification");
      expect(submitted.submissions).to.have.length(1);
      expect(submitted.submissions[0].phases).to.include("All Phases");
      expect(submitted.submissions[0].frequency).to.eq("As Needed");
      expect(submitted.submissions[0].report_submission_type).to.eq("Primary Contact Notification");
    });
  });

  it("reveals Linked Management Plan and Report Title fields for a Management Plan Associated Report", () => {
    mountForm({ managementPlans: [{ id: "1", name: "Plan A" }] });

    cy.contains("Select report type...").click();
    cy.get('li[role="option"]').contains("Management Plan Associated Report").click();

    cy.contains("Linked Management Plan").should("exist");
    cy.contains("Report Title").should("exist");

    cy.get('input[placeholder="Enter report title..."]').type("Annual Monitoring Report");
  });

  it("adds an additional submission requirement block", () => {
    mountForm();

    cy.contains("Select report type...").click();
    cy.get('li[role="option"]').contains("Compliance Notification").click();

    cy.contains("Add Submission Requirement").click();

    // A second submission block renders its own Timing field
    cy.get('input[placeholder="e.g. within 30 days after the issuance of this Certificate."]').should(
      "have.length",
      2
    );
  });
});
