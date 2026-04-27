# Enterprise System Requirements Specification

## Logistics ERP System

**Developer-ready specification for Trip Management, Driver Management, Multi-source Cost Capture, Prepaid Fuel and Toll Accounting, Dual Currency, Budget vs Actual and Financial Reporting**

**Prepared for:** Logistics, Finance, Operations and Software Development Teams  
**Version:** 1.0 Corrected Detailed Draft  
**Date:** April 2026

# Document Control

| **Item**                       | **Details**                                                                                                                                                                                                                            |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Document purpose               | Define functional, accounting, reporting, integration, control and data requirements for a Logistics ERP system.                                                                                                                       |
| Main business problem          | Costs are incurred and captured from multiple sources: Head Office cashier, Logistics cashier, prepaid diesel account and prepaid toll system. The ERP must consolidate these costs into trip-wise operational and accounting reports. |
| Critical developer instruction | Every operational activity must either create a defined accounting impact or clearly have no accounting impact. Developers must not build financial screens as free text forms. Accounting rules must be structured and traceable.     |
| Primary users                  | Operations users, HO cashier, Logistics cashier, accountant, finance manager, management, system administrator and developers.                                                                                                         |
| Base assumptions               | The company uses one base reporting currency and may transact in a second currency. Fuel and toll systems may be integrated by API or imported periodically using files.                                                               |

# Revision History

| **Version** | **Date**   | **Description**                                                                            | **Owner**                   |
|-------------|------------|--------------------------------------------------------------------------------------------|-----------------------------|
| 1.0         | April 2026 | Corrected enterprise-level SRS based on the actual operating routine and accounting needs. | Business Owner / Consultant |

# Table of Contents

1. Executive Summary

2. Business Background

3. Goals and Success Measures

4. Scope and Boundaries

5. User Roles and Responsibilities

6. End-to-End Business Workflow

7. Master Data Requirements

8. Trip Management Module

9. Driver Management Module

10. Cost Capture Module

11. Driver Advance and Settlement Module

12. Prepaid Fuel Module

13. Prepaid Toll Module

14. Matching and Exception Module

15. Accounting Engine

16. Budget vs Actual Module

17. Dual Currency Module

18. Revenue and Invoicing Module

19. Reporting and Dashboards

20. Database Design

21. Integration Requirements

22. Security and Controls

23. Audit Trail and Compliance

24. Non-Functional Requirements

25. Testing and Acceptance

26. Implementation Roadmap

27. Appendix A - Accounting Examples

28. Appendix B - Glossary

# 1. Executive Summary

This System Requirements Specification describes a Logistics ERP system
that connects daily logistics operations with formal accounting. The
system must manage trips, vehicles, drivers, cost capture, prepaid
diesel usage, toll usage, invoices, customer payments, budgets, dual
currency and financial reports. The most important design principle is
that the ERP must produce accurate trip-wise costs and accounting
entries from the same source data.

In the actual logistics routine, costs are not captured in one location.
Head Office cashier may issue cash or driver advances. Logistics cashier
may record operational payments at the site. Most diesel cost may be
consumed from a prepaid fuel account. Toll costs may also come from a
separate prepaid toll system. The ERP must bring all of these sources
into a single trip cost view and then into proper accounting reports.

The developer must understand that cash payment, prepaid consumption and
driver advance are different accounting events. A cash payment normally
credits cash or bank. A prepaid consumption credits a prepaid asset. A
driver advance creates an asset until the driver accounts for the money.
Trip creation and budgeting do not normally create accounting entries.
These differences must be reflected in database design, screens, posting
logic and reports.

- The ERP must support full trip lifecycle control from planning to
  closure.

- The ERP must support driver advances and settlements.

- The ERP must support HO cashier and Logistics cashier as separate cost
  sources.

- The ERP must support prepaid fuel top-up, fuel usage, toll top-up and
  toll usage.

- The ERP must support double-entry journals and a configurable chart of
  accounts.

- The ERP must support trip-wise profitability and budget vs actual
  reports.

- The ERP must support dual currency, with transaction currency and base
  currency values.

# 2. Business Background

The logistics business requires accurate tracking of costs and revenue
by trip. A trip may involve fuel, tolls, driver allowances, loading
expenses, repairs, permits, accommodation, emergency cash and other
operational costs. Some of these costs are paid in cash, some are paid
by bank, some are consumed from prepaid systems, and some may be accrued
or paid later. If all costs are not captured and linked to the correct
trip, management cannot measure profitability correctly.

The current operating routine creates a risk that financial reports and
operational reports do not agree. For example, diesel may be consumed
from a prepaid account but not immediately visible to the trip
accountant. Toll costs may be available in a separate toll platform but
not linked to the route or trip. Driver advances may be paid but not
settled on time. These issues lead to incomplete trip cost reports,
incorrect budget comparisons and weak financial control.

The proposed ERP must therefore be designed as a controlled operational
and accounting platform. It should not simply store expenses. It must
validate expense source, currency, trip, driver, vehicle, category,
approval status and accounting account. It must also allow finance users
to review, approve and post transactions into journals.

| **Business Issue**                                           | **ERP Requirement**                                                                                                     | **Result Expected**                                                |
|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| Multiple cost capture points                                 | Create one cost capture framework with source type for HO cashier, Log cashier, prepaid fuel, prepaid toll and imports. | All costs can be traced to source and consolidated by trip.        |
| Prepaid diesel and toll not visible in trip cost immediately | Import or capture prepaid usage and match it to trip.                                                                   | Trip cost includes fuel and toll consumption.                      |
| Driver advances may remain unsettled                         | Track advance issue, settlement, balance and trip link.                                                                 | Finance can see outstanding driver balances.                       |
| Manual budget comparison                                     | Automatically calculate actual cost and variance.                                                                       | Management can see over-budget trips.                              |
| Dual currency difficulty                                     | Store transaction amount, currency, exchange rate and base amount.                                                      | Reports can be prepared in base currency and transaction currency. |

# 3. Goals and Success Measures

The system will be successful when operations and finance use one source
of truth for logistics performance. The ERP must support reliable data
entry, correct accounting behavior, easy reporting and strong controls.

## 3.1 Goals

- Digitize trip planning, dispatch, execution and closure.

- Provide a complete cost record for every trip.

- Convert approved operational transactions into accounting journals
  automatically.

- Provide accurate trip-wise profit or loss.

- Track prepaid fuel and prepaid toll balances.

- Track driver advances and settlements.

- Enable budget vs actual analysis by trip, route, vehicle, driver and
  period.

- Generate financial reports that agree with operational data.

## 3.2 Success Measures

| **Measure**              | **Target**                                                                                         |
|--------------------------|----------------------------------------------------------------------------------------------------|
| Trip cost completeness   | All approved cash, prepaid fuel, prepaid toll and advance-settled costs appear in the trip report. |
| Accounting accuracy      | Every posted journal balances debit and credit.                                                    |
| Prepaid balance accuracy | Opening balance plus top-ups minus usage equals closing balance.                                   |
| Reporting timeliness     | Standard trip and financial reports should be available without manual spreadsheet consolidation.  |
| Exception visibility     | Unmatched fuel and toll transactions are visible in an exception queue.                            |
| Auditability             | Every posted transaction can be traced to user, source, trip, attachment and journal.              |

# 4. Scope and Boundaries

## 4.1 In Scope

- Trip management from planning to closure.

- Vehicle and driver assignment.

- Driver profile and driver advance management.

- HO cashier and Logistics cashier payment capture.

- Prepaid fuel account top-up and usage accounting.

- Prepaid toll account top-up and usage accounting.

- Fuel and toll transaction import or API integration.

- Automatic or manual matching of fuel and toll usage to trips.

- Chart of accounts and double-entry journal posting.

- Trip budgets, actual costs and variance reports.

- Dual currency transaction handling.

- Trip invoices, customer receivables and payment records.

- Operational, financial, control and exception reports.

## 4.2 Out of Scope Unless Later Approved

- Payroll processing beyond driver allowance and advance tracking.

- Full warehouse inventory management.

- Vehicle maintenance workshop planning beyond capturing maintenance
  costs.

- Bank integration for automatic bank statement reconciliation.

- Tax filing automation.

- Mobile driver application unless requested in a later phase.

# 5. User Roles and Responsibilities

| **Role**                  | **Responsibilities**                                                                            | **Restrictions or Controls**                                                 |
|---------------------------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| System Administrator      | Create users, roles, master data, currencies, routes, vehicles and configuration.               | Should not post financial entries unless also assigned finance role.         |
| Operations User           | Create trips, assign drivers and vehicles, update trip status and attach operational documents. | Cannot approve or post accounting journals.                                  |
| HO Cashier                | Record head office payments, driver advances and emergency trip payments.                       | Can create transactions but finance approval may be required before posting. |
| Logistics Cashier         | Record site or route level cash expenses and attach receipts.                                   | Cannot edit posted transactions.                                             |
| Accountant                | Review transactions, approve expenses, post journals, reverse errors and manage period locks.   | Posting rights controlled by role.                                           |
| Finance Manager           | Review financial statements, approve high value transactions and monitor prepaid balances.      | May have final approval authority.                                           |
| Management                | View dashboards, trip profitability and exception reports.                                      | Read-only access.                                                            |
| Developer or Support User | Maintain system configuration and troubleshoot technical issues.                                | Should not change posted financial data directly in the database.            |

# 6. End-to-End Business Workflow

The ERP must follow the real business flow below. The workflow is
important because it defines when accounting entries happen and when
they do not happen.

1.  Create trip with route, customer, driver, vehicle, planned dates and
    budget.

2.  Approve and dispatch trip. There is still no accounting entry unless
    money is issued or a cost is captured.

3.  Capture cash expenses from HO cashier or Logistics cashier.

4.  Issue driver advance if required and track it as an asset until
    settled.

5.  Import or capture diesel usage from prepaid fuel system.

6.  Import or capture toll usage from prepaid toll system.

7.  Match prepaid usage transactions to the correct trip using vehicle,
    date and route.

8.  Review trip costs and resolve unmatched transactions.

9.  Complete trip operationally.

10. Create customer invoice for trip revenue.

11. Receive customer payment and clear receivable.

12. Generate trip profitability, budget variance, prepaid balance and
    financial reports.

## 6.1 Workflow Diagram

Trip Created -\> Driver and Vehicle Assigned -\> Trip Budget Entered  
-\> Trip Dispatched  
-\> Costs Captured from HO Cashier / Log Cashier / Prepaid Fuel /
Prepaid Toll  
-\> Prepaid Fuel and Toll Transactions Matched to Trip  
-\> Accountant Reviews and Posts Journals  
-\> Trip Completed and Closed  
-\> Invoice Raised to Customer  
-\> Payment Received  
-\> Reports Generated

# 7. Master Data Requirements

| **Req ID** | **Requirement**                                                                                                                                                                       | **Priority** | **Acceptance Criteria**                                                   |
|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|---------------------------------------------------------------------------|
| MST-001    | System shall maintain master records for vehicles, drivers, routes, customers, currencies, exchange rates, expense categories, cash accounts, prepaid accounts and chart of accounts. | Must         | Users can create and maintain master data with active or inactive status. |
| MST-002    | System shall prevent use of inactive vehicles, drivers, routes, customers or accounts in new transactions unless overridden by authorized users.                                      | Must         | Inactive master data cannot be selected in normal transaction screens.    |
| MST-003    | Expense categories shall be mapped to general ledger accounts.                                                                                                                        | Must         | No expense can be posted if its category has no GL mapping.               |
| MST-004    | Currencies and exchange rates shall be date based.                                                                                                                                    | Must         | Transactions store the rate used and base amount calculated.              |
| MST-005    | Routes shall store origin, destination and estimated distance where available.                                                                                                        | Should       | Route data can support budget and matching logic.                         |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 8. Trip Management Module

| **Req ID** | **Requirement**                                                                                                                                                 | **Priority** | **Acceptance Criteria**                                                                  |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|------------------------------------------------------------------------------------------|
| TRIP-001   | System shall allow trip creation with trip number, customer, route, vehicle, driver, planned start date, planned end date, budget and currency.                 | Must         | Trip is saved with mandatory fields.                                                     |
| TRIP-002   | System shall support statuses Planned, Approved, Dispatched, In Progress, Completed, Closed and Cancelled.                                                      | Must         | Trip status transitions are controlled.                                                  |
| TRIP-003   | Trip creation shall not create accounting entries.                                                                                                              | Must         | No journal is created only because a trip is created.                                    |
| TRIP-004   | System shall display all costs linked to a trip from all sources.                                                                                               | Must         | Trip cost screen includes cashier, prepaid fuel, prepaid toll and settled advance costs. |
| TRIP-005   | System shall prevent closure when required unmatched prepaid transactions exist for the trip vehicle during trip dates, unless authorized override is recorded. | Should       | Closure control or warning exists.                                                       |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 9. Driver Management Module

| **Req ID** | **Requirement**                                                                                               | **Priority** | **Acceptance Criteria**                               |
|------------|---------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------------|
| DRV-001    | System shall store driver profile, license, contact information, status and optional employment details.      | Must         | Driver records are searchable and maintainable.       |
| DRV-002    | System shall link drivers to trips and driver advances.                                                       | Must         | Driver reports show trip assignments and balances.    |
| DRV-003    | System shall flag expired licenses if expiry date is maintained.                                              | Should       | User receives warning before assigning driver.        |
| DRV-004    | System shall support driver performance reports by trips completed, cost exceptions and outstanding advances. | Should       | Management can review driver performance.             |
| DRV-005    | System shall prevent assignment of inactive drivers to new trips.                                             | Must         | Inactive drivers cannot be selected in trip creation. |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 10. Cost Capture Module

| **Req ID** | **Requirement**                                                                                                           | **Priority** | **Acceptance Criteria**                              |
|------------|---------------------------------------------------------------------------------------------------------------------------|--------------|------------------------------------------------------|
| COST-001   | System shall capture expenses by source type: HO Cashier, Logistics Cashier, Prepaid Fuel, Prepaid Toll, Vendor or Other. | Must         | Every expense record has a source type.              |
| COST-002   | System shall require trip, expense category, amount, currency, date and source for trip-related expense records.          | Must         | Incomplete records cannot be submitted for approval. |
| COST-003   | System shall support receipt or voucher attachment.                                                                       | Should       | Attachment is visible from expense screen.           |
| COST-004   | System shall separate draft, submitted, approved, posted and rejected statuses.                                           | Must         | Approval workflow is auditable.                      |
| COST-005   | System shall produce a single trip cost summary from all approved cost sources.                                           | Must         | Trip report totals all sources.                      |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 11. Driver Advance and Settlement Module

| **Req ID** | **Requirement**                                                                                                   | **Priority** | **Acceptance Criteria**                               |
|------------|-------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------------|
| ADV-001    | System shall allow HO cashier or authorized cashier to issue driver advance linked to trip and driver.            | Must         | Advance balance is created for driver and trip.       |
| ADV-002    | Driver advance issue shall debit Driver Advance and credit Cash or Bank.                                          | Must         | Journal entry is generated correctly when posted.     |
| ADV-003    | System shall allow settlement of advances with expense categories, receipts and unused cash return if applicable. | Must         | Advance balance is reduced by settlements or returns. |
| ADV-004    | Advance settlement against expenses shall debit expense and credit Driver Advance.                                | Must         | Settlement journal is generated correctly.            |
| ADV-005    | System shall report outstanding advances by driver, trip and ageing.                                              | Must         | Finance can monitor balances.                         |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 12. Prepaid Fuel Module

| **Req ID** | **Requirement**                                                                                      | **Priority** | **Acceptance Criteria**                               |
|------------|------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------------|
| FUEL-001   | System shall maintain prepaid fuel accounts by provider, currency and GL prepaid asset account.      | Must         | Prepaid account master data exists.                   |
| FUEL-002   | Fuel account top-up shall debit Prepaid Fuel and credit Cash or Bank.                                | Must         | Top-up journal is correct.                            |
| FUEL-003   | Fuel usage shall debit Fuel Expense and credit Prepaid Fuel.                                         | Must         | Usage journal is correct.                             |
| FUEL-004   | System shall import or capture fuel usage with vehicle, date, liters, amount and external reference. | Must         | Fuel transaction list contains required fields.       |
| FUEL-005   | System shall match fuel usage to trip based on vehicle and usage date, with manual override.         | Must         | Usage can be matched and unmatched items are visible. |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 13. Prepaid Toll Module

| **Req ID** | **Requirement**                                                                                          | **Priority** | **Acceptance Criteria**                          |
|------------|----------------------------------------------------------------------------------------------------------|--------------|--------------------------------------------------|
| TOLL-001   | System shall maintain prepaid toll accounts by provider, currency and GL prepaid asset account.          | Must         | Prepaid toll account master data exists.         |
| TOLL-002   | Toll account top-up shall debit Prepaid Toll and credit Cash or Bank.                                    | Must         | Top-up journal is correct.                       |
| TOLL-003   | Toll usage shall debit Toll Expense and credit Prepaid Toll.                                             | Must         | Usage journal is correct.                        |
| TOLL-004   | System shall import or capture toll usage with vehicle, date, toll point, amount and external reference. | Must         | Toll transaction list contains required fields.  |
| TOLL-005   | System shall match toll usage to trip based on vehicle, date and route, with manual override.            | Must         | Usage can be matched and exceptions are visible. |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 14. Matching and Exception Module

| **Req ID** | **Requirement**                                                                                                                                          | **Priority** | **Acceptance Criteria**                       |
|------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|-----------------------------------------------|
| MATCH-001  | System shall attempt automatic matching of prepaid fuel and toll transactions to trips based on vehicle and transaction date falling within trip period. | Must         | System proposes or assigns trip match.        |
| MATCH-002  | System shall use route or toll point where available to improve toll matching.                                                                           | Should       | Route improves match confidence.              |
| MATCH-003  | System shall provide unmatched transaction queue.                                                                                                        | Must         | Unmatched transactions can be reviewed.       |
| MATCH-004  | System shall allow authorized manual matching, rematching and unmatched marking with reason.                                                             | Must         | Manual changes are audited.                   |
| MATCH-005  | System shall prevent duplicate posting of same external reference.                                                                                       | Must         | Duplicate references are rejected or flagged. |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 15. Accounting Engine

| **Req ID** | **Requirement**                                                                                  | **Priority** | **Acceptance Criteria**                           |
|------------|--------------------------------------------------------------------------------------------------|--------------|---------------------------------------------------|
| ACC-001    | System shall generate double-entry journals from approved transactions.                          | Must         | Every posted journal balances.                    |
| ACC-002    | System shall maintain chart of accounts with account code, name, type, parent and active status. | Must         | Accounts can be configured.                       |
| ACC-003    | System shall store journal source module and source ID.                                          | Must         | Every journal is traceable to source transaction. |
| ACC-004    | System shall prevent posting into locked periods.                                                | Must         | Closed periods cannot be changed.                 |
| ACC-005    | System shall reverse posted journals using reversal entries and shall not delete posted history. | Must         | Corrections are auditable.                        |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 16. Budget vs Actual Module

| **Req ID** | **Requirement**                                                           | **Priority** | **Acceptance Criteria**                                   |
|------------|---------------------------------------------------------------------------|--------------|-----------------------------------------------------------|
| BUD-001    | System shall allow budget entry at trip level.                            | Must         | Trip stores budget amount and currency.                   |
| BUD-002    | System should allow budget entry by expense category.                     | Should       | Fuel, toll, allowance and other budgets can be separated. |
| BUD-003    | System shall calculate actual cost from approved or posted trip expenses. | Must         | Actual cost agrees with cost ledger.                      |
| BUD-004    | System shall calculate variance as Budget minus Actual.                   | Must         | Report shows variance amount and percentage.              |
| BUD-005    | System shall highlight over-budget trips and categories.                  | Should       | Management can identify cost overruns.                    |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 17. Dual Currency Module

| **Req ID** | **Requirement**                                                                       | **Priority** | **Acceptance Criteria**                                   |
|------------|---------------------------------------------------------------------------------------|--------------|-----------------------------------------------------------|
| CUR-001    | System shall support transaction currency and base reporting currency.                | Must         | Every financial transaction stores both where applicable. |
| CUR-002    | System shall store exchange rate and rate date for each transaction.                  | Must         | Base amount is reproducible.                              |
| CUR-003    | System shall allow reports in base currency and transaction currency where practical. | Should       | Dual currency reports are available.                      |
| CUR-004    | System shall prevent posting when required exchange rate is missing.                  | Must         | Posting blocked until rate exists.                        |
| CUR-005    | System shall allow authorized exchange rate maintenance.                              | Must         | Rates can be controlled by finance.                       |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 18. Revenue and Invoicing Module

| **Req ID** | **Requirement**                                                                      | **Priority** | **Acceptance Criteria**             |
|------------|--------------------------------------------------------------------------------------|--------------|-------------------------------------|
| INV-001    | System shall allow invoice creation from completed or approved trips.                | Must         | Invoice links to trip and customer. |
| INV-002    | Invoice posting shall debit Accounts Receivable and credit Transport Revenue.        | Must         | Revenue journal is correct.         |
| INV-003    | Customer payment shall debit Cash or Bank and credit Accounts Receivable.            | Must         | Payment journal is correct.         |
| INV-004    | System shall track invoice status Draft, Posted, Partially Paid, Paid and Cancelled. | Must         | Receivables are trackable.          |
| INV-005    | System shall report revenue and receivables by customer, trip and period.            | Must         | Finance reports are available.      |

Developer note: Screens in this module must validate mandatory fields
before allowing submission or posting. Posted accounting records must be
protected from direct editing. Any correction after posting must follow
an approved reversal or adjustment workflow.

# 19. Reporting and Dashboards

Reports are a major deliverable. Reports must be generated from the same
transaction tables used for accounting so that operational reports and
financial reports agree. Users should be able to filter by period, trip,
customer, route, vehicle, driver, cost source, currency and status.

| **Report**             | **Audience**                    | **Content**                                                                                                       | **Purpose**                                 |
|------------------------|---------------------------------|-------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| Trip Profitability     | Operations, Finance, Management | Revenue, fuel, toll, driver allowance, repairs, other costs, total actual cost, budget, variance, profit or loss. | Shows whether each trip made or lost money. |
| Budget vs Actual       | Operations and Management       | Budget, actual, variance amount, variance percent by trip and cost category.                                      | Highlights cost overruns.                   |
| Prepaid Fuel Balance   | Finance                         | Opening balance, top-ups, fuel usage, adjustments and closing balance.                                            | Controls prepaid diesel account.            |
| Prepaid Toll Balance   | Finance                         | Opening balance, top-ups, toll usage, adjustments and closing balance.                                            | Controls prepaid toll account.              |
| Driver Advance Ageing  | Finance and Operations          | Driver, trip, advance amount, settled amount, balance, days outstanding.                                          | Controls driver accountability.             |
| Unmatched Transactions | Finance and Operations          | Fuel or toll usage without trip match.                                                                            | Ensures all costs are assigned.             |
| Cost by Vehicle        | Management                      | All trip costs grouped by vehicle.                                                                                | Supports fleet cost analysis.               |
| Cost by Driver         | Management                      | Costs and exceptions grouped by driver.                                                                           | Supports driver performance review.         |
| Profit and Loss        | Finance and Management          | Revenue, cost of services and expenses by period.                                                                 | Financial reporting.                        |

# 20. Database Design

The following database structure is recommended. Developers may adapt
names to the chosen technology stack, but the meaning, relationships and
accounting behavior must be preserved.

## vehicles

| **Field**    | **Type** | **Description**               |
|--------------|----------|-------------------------------|
| vehicle_id   | PK       | Unique vehicle ID             |
| plate_number | varchar  | Vehicle plate number          |
| vehicle_type | varchar  | Truck, trailer or tanker      |
| status       | varchar  | Active, inactive, maintenance |

## drivers

| **Field**      | **Type** | **Description**    |
|----------------|----------|--------------------|
| driver_id      | PK       | Driver ID          |
| full_name      | varchar  | Driver full name   |
| license_number | varchar  | License number     |
| license_expiry | date     | Expiry date        |
| status         | varchar  | Active or inactive |

## routes

| **Field**    | **Type** | **Description**    |
|--------------|----------|--------------------|
| route_id     | PK       | Route ID           |
| origin       | varchar  | Origin             |
| destination  | varchar  | Destination        |
| estimated_km | decimal  | Estimated distance |

## customers

| **Field**           | **Type** | **Description**          |
|---------------------|----------|--------------------------|
| customer_id         | PK       | Customer ID              |
| customer_name       | varchar  | Customer name            |
| default_currency_id | FK       | Default invoice currency |

## currencies

| **Field**     | **Type** | **Description** |
|---------------|----------|-----------------|
| currency_id   | PK       | Currency ID     |
| currency_code | varchar  | USD, ZMW etc.   |
| currency_name | varchar  | Currency name   |

## exchange_rates

| **Field**        | **Type** | **Description**  |
|------------------|----------|------------------|
| rate_id          | PK       | Rate ID          |
| currency_id      | FK       | Foreign currency |
| base_currency_id | FK       | Base currency    |
| rate             | decimal  | Exchange rate    |
| effective_date   | date     | Effective date   |

## trips

| **Field**          | **Type** | **Description** |
|--------------------|----------|-----------------|
| trip_id            | PK       | Trip ID         |
| trip_number        | varchar  | Trip number     |
| customer_id        | FK       | Customer        |
| route_id           | FK       | Route           |
| vehicle_id         | FK       | Vehicle         |
| driver_id          | FK       | Driver          |
| planned_start_date | datetime | Planned start   |
| actual_start_date  | datetime | Actual start    |
| actual_end_date    | datetime | Actual end      |
| status             | varchar  | Trip status     |
| budget_amount      | decimal  | Budget          |
| currency_id        | FK       | Budget currency |

## expense_categories

| **Field**     | **Type** | **Description**         |
|---------------|----------|-------------------------|
| category_id   | PK       | Category ID             |
| category_name | varchar  | Fuel, Toll, Repair etc. |
| gl_account_id | FK       | Expense GL account      |
| is_active     | boolean  | Status                  |

## trip_expenses

| **Field**     | **Type** | **Description**         |
|---------------|----------|-------------------------|
| expense_id    | PK       | Expense ID              |
| trip_id       | FK       | Trip                    |
| expense_date  | date     | Date                    |
| source_type   | varchar  | HO, Log, Fuel, Toll     |
| category_id   | FK       | Category                |
| amount        | decimal  | Amount                  |
| currency_id   | FK       | Currency                |
| exchange_rate | decimal  | Rate                    |
| base_amount   | decimal  | Base amount             |
| reference_no  | varchar  | Voucher or external ref |
| status        | varchar  | Draft, approved, posted |

## cash_accounts

| **Field**       | **Type** | **Description**         |
|-----------------|----------|-------------------------|
| cash_account_id | PK       | Cash account ID         |
| account_name    | varchar  | HO Cashier, Log Cashier |
| location        | varchar  | HO or site              |
| currency_id     | FK       | Currency                |
| gl_account_id   | FK       | Cash GL                 |

## cash_transactions

| **Field**           | **Type**    | **Description**          |
|---------------------|-------------|--------------------------|
| cash_transaction_id | PK          | Transaction ID           |
| cash_account_id     | FK          | Cash account             |
| trip_id             | FK nullable | Trip                     |
| driver_id           | FK nullable | Driver                   |
| transaction_type    | varchar     | Expense, advance, return |
| amount              | decimal     | Amount                   |
| currency_id         | FK          | Currency                 |
| base_amount         | decimal     | Base amount              |
| status              | varchar     | Draft, approved, posted  |

## driver_advances

| **Field**           | **Type** | **Description**         |
|---------------------|----------|-------------------------|
| advance_id          | PK       | Advance ID              |
| trip_id             | FK       | Trip                    |
| driver_id           | FK       | Driver                  |
| cash_transaction_id | FK       | Source cash transaction |
| amount              | decimal  | Amount                  |
| base_amount         | decimal  | Base amount             |
| status              | varchar  | Open, partial, closed   |

## driver_advance_settlements

| **Field**         | **Type**    | **Description**   |
|-------------------|-------------|-------------------|
| settlement_id     | PK          | Settlement ID     |
| advance_id        | FK          | Advance           |
| expense_id        | FK nullable | Expense created   |
| settled_amount    | decimal     | Settled amount    |
| settlement_date   | date        | Date              |
| balance_remaining | decimal     | Remaining balance |

## prepaid_accounts

| **Field**          | **Type** | **Description**      |
|--------------------|----------|----------------------|
| prepaid_account_id | PK       | Prepaid account      |
| account_name       | varchar  | Fuel or toll account |
| account_type       | varchar  | Fuel or Toll         |
| provider_name      | varchar  | Provider             |
| currency_id        | FK       | Currency             |
| gl_account_id      | FK       | Prepaid asset GL     |

## prepaid_topups

| **Field**          | **Type** | **Description**         |
|--------------------|----------|-------------------------|
| topup_id           | PK       | Top-up ID               |
| prepaid_account_id | FK       | Prepaid account         |
| topup_date         | date     | Top-up date             |
| amount             | decimal  | Amount                  |
| currency_id        | FK       | Currency                |
| exchange_rate      | decimal  | Rate                    |
| base_amount        | decimal  | Base amount             |
| payment_account_id | FK       | Cash or bank            |
| status             | varchar  | Draft, approved, posted |

## prepaid_usage_transactions

| **Field**          | **Type**         | **Description**               |
|--------------------|------------------|-------------------------------|
| usage_id           | PK               | Usage ID                      |
| prepaid_account_id | FK               | Prepaid account               |
| trip_id            | FK nullable      | Matched trip                  |
| vehicle_id         | FK               | Vehicle                       |
| usage_date         | date             | Usage date                    |
| usage_type         | varchar          | Fuel or Toll                  |
| quantity           | decimal nullable | Liters for fuel               |
| amount             | decimal          | Amount                        |
| currency_id        | FK               | Currency                      |
| base_amount        | decimal          | Base amount                   |
| external_reference | varchar          | External reference            |
| match_status       | varchar          | Matched, unmatched, exception |

## chart_of_accounts

| **Field**         | **Type**    | **Description**                    |
|-------------------|-------------|------------------------------------|
| gl_account_id     | PK          | GL ID                              |
| account_code      | varchar     | Account code                       |
| account_name      | varchar     | Account name                       |
| account_type      | varchar     | Asset, liability, revenue, expense |
| parent_account_id | FK nullable | Parent account                     |
| is_active         | boolean     | Active                             |

## journal_entries

| **Field**     | **Type** | **Description**         |
|---------------|----------|-------------------------|
| journal_id    | PK       | Journal ID              |
| journal_date  | date     | Journal date            |
| source_module | varchar  | Module                  |
| source_id     | varchar  | Source ID               |
| description   | text     | Description             |
| status        | varchar  | Draft, posted, reversed |
| posted_at     | datetime | Posting time            |

## journal_entry_lines

| **Field**          | **Type**    | **Description** |
|--------------------|-------------|-----------------|
| journal_line_id    | PK          | Line ID         |
| journal_id         | FK          | Journal         |
| gl_account_id      | FK          | Account         |
| debit_amount       | decimal     | Debit           |
| credit_amount      | decimal     | Credit          |
| currency_id        | FK          | Currency        |
| exchange_rate      | decimal     | Rate            |
| base_debit_amount  | decimal     | Base debit      |
| base_credit_amount | decimal     | Base credit     |
| trip_id            | FK nullable | Trip dimension  |

## trip_invoices

| **Field**      | **Type** | **Description**     |
|----------------|----------|---------------------|
| invoice_id     | PK       | Invoice ID          |
| invoice_number | varchar  | Invoice number      |
| trip_id        | FK       | Trip                |
| customer_id    | FK       | Customer            |
| invoice_date   | date     | Date                |
| amount         | decimal  | Amount              |
| currency_id    | FK       | Currency            |
| base_amount    | decimal  | Base amount         |
| status         | varchar  | Draft, posted, paid |

## customer_payments

| **Field**       | **Type** | **Description**      |
|-----------------|----------|----------------------|
| payment_id      | PK       | Payment ID           |
| customer_id     | FK       | Customer             |
| invoice_id      | FK       | Invoice              |
| payment_date    | date     | Date                 |
| amount          | decimal  | Amount               |
| currency_id     | FK       | Currency             |
| base_amount     | decimal  | Base amount          |
| bank_account_id | FK       | Bank or cash account |
| reference_no    | varchar  | Receipt reference    |

# 21. Integration Requirements

The ERP must integrate with fuel and toll systems either by API or
controlled import. If API integration is not available at first, the
system must allow CSV or Excel upload with validation and duplicate
checking.

- Fuel import must include vehicle, date, liters if available, amount,
  currency, provider and external reference.

- Toll import must include vehicle, date, toll point if available,
  amount, currency, provider and external reference.

- Imports must not create posted journals automatically until validation
  and approval rules are satisfied.

- The system must keep the original imported reference and file batch ID
  for audit.

- Rejected import rows must show error reasons.

# 22. Security and Controls

Security must protect financial integrity. Users should only perform
actions that match their role. Accounting posting and reversal must be
restricted to finance users.

- Use role-based access control.

- Separate data entry from approval where required.

- Restrict period locking and unlocking to authorized finance roles.

- Restrict exchange rate changes to finance or admin roles.

- Require reason for reversal, manual matching override and high value
  expense approval.

- Maintain audit trail for sensitive actions.

# 23. Audit Trail and Compliance

The ERP must be auditable. A finance user should be able to trace every
report number back to the original transaction and supporting document.

- Record created by, created date, modified by and modified date for
  major records.

- Record approval user and approval date.

- Record posting user and posting date.

- Store old value and new value for sensitive changes where practical.

- Do not allow deletion of posted journals.

- Use reversal entries or adjustment entries for corrections.

# 24. Non-Functional Requirements

The ERP must be reliable, secure and usable by operational and finance
teams. It should be designed for growth in trips, vehicles, transactions
and users.

- Standard reports should load in acceptable time for normal business
  volumes.

- The system should support backup and recovery procedures.

- The user interface should clearly show mandatory fields and validation
  errors.

- The system should support attachment storage for receipts and
  vouchers.

- The database should enforce referential integrity for key
  relationships.

- Configuration should be used for accounts and categories where
  possible, instead of hard-coding values.

# 25. Testing and Acceptance

Testing must prove that the system performs the complete logistics and
accounting workflow accurately. The system should not be accepted only
because screens are working. Reports and journals must also be correct.

- Test trip creation and confirm no journal is created.

- Test HO cashier expense and confirm debit expense, credit cash or
  bank.

- Test driver advance and confirm debit driver advance, credit cash or
  bank.

- Test driver settlement and confirm debit expense, credit driver
  advance.

- Test prepaid fuel top-up and confirm debit prepaid fuel, credit bank
  or cash.

- Test fuel usage and confirm debit fuel expense, credit prepaid fuel.

- Test prepaid toll top-up and usage.

- Test invoice and payment accounting.

- Test unmatched fuel and toll exceptions.

- Test dual currency conversion and base currency reports.

# 26. Implementation Roadmap

Implementation should be phased so that foundation data and controls are
correct before complex accounting and reporting are activated.

- Phase 1: Master data, users, roles, chart of accounts and currencies.

- Phase 2: Trip management and driver management.

- Phase 3: Cashier cost capture and driver advances.

- Phase 4: Prepaid fuel and prepaid toll accounts.

- Phase 5: Accounting posting engine and approval workflow.

- Phase 6: Invoicing, payments and reports.

- Phase 7: User acceptance testing, training, data migration and
  go-live.

# 27. Appendix A - Accounting Examples

| **Event**                                   | **Debit**           | **Credit**          | **Explanation**                                    |
|---------------------------------------------|---------------------|---------------------|----------------------------------------------------|
| Trip created                                | No debit            | No credit           | No accounting entry. The trip is only operational. |
| Trip budget entered                         | No debit            | No credit           | Budget is planning data, not a financial posting.  |
| HO cashier pays trip repair                 | Repair Expense      | Cash or Bank        | Direct cash cost linked to trip.                   |
| HO cashier gives driver advance             | Driver Advance      | Cash or Bank        | Driver owes accountability until settlement.       |
| Driver submits fuel receipt against advance | Fuel Expense        | Driver Advance      | Advance is converted into actual expense.          |
| Prepaid diesel account funded               | Prepaid Fuel        | Cash or Bank        | Asset created. No fuel expense yet.                |
| Diesel consumed by trip                     | Fuel Expense        | Prepaid Fuel        | Fuel asset reduced and trip cost recognized.       |
| Prepaid toll account funded                 | Prepaid Toll        | Cash or Bank        | Asset created. No toll expense yet.                |
| Toll consumed by trip                       | Toll Expense        | Prepaid Toll        | Toll asset reduced and trip cost recognized.       |
| Customer invoice posted                     | Accounts Receivable | Transport Revenue   | Revenue recognized.                                |
| Customer payment received                   | Cash or Bank        | Accounts Receivable | Receivable cleared.                                |

Example trip: A trip has budget of ZMW 10,000. Fuel consumed from
prepaid account is ZMW 4,000. Toll consumed from prepaid account is ZMW
800. Logistics cashier pays ZMW 600 for loading. Customer invoice is ZMW
8,500. The system should show actual cost of ZMW 5,400 before any
additional settled driver advance costs. Profit before other costs is
ZMW 3,100. If a ZMW 1,500 driver advance is later settled with receipts,
actual cost increases according to the approved expense categories and
the driver advance balance decreases.

# 28. Appendix B - Glossary

| **Term**             | **Meaning**                                                                           |
|----------------------|---------------------------------------------------------------------------------------|
| ERP                  | Enterprise Resource Planning system integrating operations and finance.               |
| Trip                 | A logistics movement from origin to destination using assigned driver and vehicle.    |
| HO Cashier           | Head Office cashier who records head office payments and advances.                    |
| Log Cashier          | Logistics cashier who records site or route-level expenses.                           |
| Prepaid Fuel         | Asset account representing money loaded into fuel system before diesel consumption.   |
| Prepaid Toll         | Asset account representing money loaded into toll system before toll usage.           |
| Driver Advance       | Money issued to driver that remains an asset until settled with receipts or returned. |
| Journal Entry        | Accounting record made of debit and credit lines.                                     |
| Chart of Accounts    | List of all general ledger accounts used for accounting.                              |
| Base Currency        | Main reporting currency of the company.                                               |
| Transaction Currency | Currency in which a transaction occurred.                                             |
| Matching             | Process of linking external fuel or toll usage to a trip.                             |
| Variance             | Difference between budget and actual amount.                                          |

# Final Sign-off Criteria

The system should be signed off only when the business can create a
trip, capture costs from HO cashier, Logistics cashier, prepaid fuel and
prepaid toll, post the correct accounting entries, create an invoice,
receive payment and produce accurate trip profitability, budget vs
actual, prepaid balance and financial reports.
