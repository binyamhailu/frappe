# Logistics ERP Architecture

This document converts the source architecture photo into a Mermaid diagram that can be versioned and refined as the system design evolves.

Source image: [architecture.jpeg](architecture.jpeg)

## Operational And Accounting Workflow

```mermaid
flowchart TB
  %% Logistics ERP - Operational and Accounting Workflow

  subgraph A["A. Operational Trip Lifecycle"]
    direction LR
    A1["1. Trip Planning<br/>Create trip<br/>Define route<br/>Assign vehicle<br/>Assign driver<br/>Set budget"]
    A2["2. Trip Start / Dispatch<br/>Driver departs<br/>Status: In Progress<br/>Trip code generated"]
    A3["3. Trip Execution<br/>Operations in progress<br/>Costs incurred from different sources"]
    A4["4. Trip Completion<br/>Trip ends<br/>Capture actual KM<br/>Delivery info<br/>Completion details"]
    A5["5. Invoicing & Revenue<br/>Create invoice for trip<br/>Post revenue<br/>Record receivable"]
    A6["6. Payment Collection<br/>Receive payment<br/>Allocate to invoice<br/>Close receivable"]

    A1 --> A2 --> A3 --> A4 --> A5 --> A6
  end

  subgraph B["B. Cost Sources - How Costs Are Captured"]
    direction LR

    subgraph B1["1. HO Cashier"]
      direction TB
      B1a["Cash payment / driver advance recorded in ERP"]
      B1b["Link to trip, driver, and expense type"]
      B1c["Accounting impact<br/>Dr: Expense / Driver Advance Asset<br/>Cr: Cash / Bank"]
      B1a --> B1b --> B1c
    end

    subgraph B2["2. Log Cashier / Site Cashier"]
      direction TB
      B2a["Expense recorded in ERP by logistics cashier"]
      B2b["Select trip, driver, and expense category"]
      B2c["Accounting impact<br/>Dr: Expense Account<br/>Cr: Cash"]
      B2a --> B2b --> B2c
    end

    subgraph B3["3. Prepaid Fuel System - External"]
      direction TB
      B3a["Fuel account funded / top-up"]
      B3b["Fuel consumed by vehicle / trip"]
      B3c["Import or sync fuel usage to ERP"]
      B3d["Funding impact<br/>Dr: Prepaid Fuel Asset<br/>Cr: Cash / Bank"]
      B3e["Usage impact<br/>Dr: Fuel Expense<br/>Cr: Prepaid Fuel Asset"]
      B3a --> B3d
      B3b --> B3c --> B3e
    end

    subgraph B4["4. Prepaid Toll System - External"]
      direction TB
      B4a["Toll account funded / top-up"]
      B4b["Toll used by vehicle / trip"]
      B4c["Import or sync toll transactions to ERP"]
      B4d["Funding impact<br/>Dr: Prepaid Toll Asset<br/>Cr: Cash / Bank"]
      B4e["Usage impact<br/>Dr: Toll Expense<br/>Cr: Prepaid Toll Asset"]
      B4a --> B4d
      B4b --> B4c --> B4e
    end
  end

  A3 -. "costs captured during execution" .-> B1a
  A3 -. "costs captured during execution" .-> B2a
  A3 -. "external fuel usage" .-> B3b
  A3 -. "external toll usage" .-> B4b

  subgraph C["C. Cost Consolidation And Matching"]
    direction LR
    C1["Matching rules<br/>By vehicle<br/>By trip dates<br/>By route<br/>By reference<br/>Manual override when needed"]
    C2["All costs consolidated to trip<br/>HO cash expenses<br/>Log cash expenses<br/>Fuel prepaid usage<br/>Toll prepaid usage<br/>Driver advances & settlements"]
    C3["Trip cost summary<br/>Total budget<br/>Total actual cost<br/>Variance: budget vs actual<br/>Profitability: revenue - cost"]
    C4["Unmatched / exceptions<br/>Unmatched fuel transactions<br/>Unmatched toll transactions<br/>Costs without trip<br/>Duplicate / invalid entries"]

    C1 --> C2 --> C3 --> C4
  end

  B1c -. "reference / matching" .-> C2
  B2c -. "reference / matching" .-> C2
  B3e -. "import / matching" .-> C2
  B4e -. "import / matching" .-> C2
  A5 --> C3

  subgraph D["D. Accounting Flow - Double Entry"]
    direction LR
    D1["1. Transaction recorded<br/>Any cost or revenue captured in ERP"]
    D2["2. System generates accounting entry<br/>Automatic double entry<br/>Debit and credit"]
    D3["3. Post to ledger<br/>Real-time posting to General Ledger"]
    D4["4. Update balances<br/>GL accounts<br/>Sub-ledgers<br/>Prepaid balances"]
    D5["5. Period close<br/>Lock period<br/>Accruals<br/>Adjustments<br/>Reconciliations"]

    D1 --> D2 --> D3 --> D4 --> D5
  end

  B1c --> D1
  B2c --> D1
  B3d --> D1
  B3e --> D1
  B4d --> D1
  B4e --> D1
  A5 --> D1
  A6 --> D1

  subgraph P["Key Accounting Principles"]
    direction LR
    P1["Double entry"]
    P2["Accrual basis"]
    P3["Audit trail"]
    P4["Period based"]
    P5["Configurable chart of accounts"]
    P6["Multi-currency"]
  end

  D2 -. "must follow" .-> P1

  subgraph E["E. Reporting Outputs"]
    direction LR
    E1["Reports available<br/>Trip-wise profitability<br/>Budget vs actual<br/>Cost per vehicle / driver<br/>Expense summary by category<br/>Fuel usage & fuel balance<br/>Toll usage & toll balance<br/>P&L, balance sheet, cash flow<br/>A/R aging and A/P aging<br/>Custom trip reports"]
    E2["Report currency<br/>Base currency<br/>Transaction currency<br/>Dual currency reports<br/>Exchange rate management"]
  end

  C3 --> E1
  C4 --> E1
  D5 --> E1
  D4 --> E2

  subgraph I["Integrations"]
    direction LR
    I1["Fuel system<br/>API / import"]
    I2["Toll system<br/>API / import"]
    I3["Bank / payment gateway"]
    I4["External accounting<br/>Optional"]
  end

  I1 -. "usage import" .-> B3c
  I2 -. "transaction import" .-> B4c
  I3 -. "payment confirmation" .-> A6
  D3 -. "optional export" .-> I4
```

## Architecture Notes

- Every transaction must have a clear source, an optional trip reference, and a defined accounting impact.
- Trip planning and budgeting do not normally post accounting entries; approved operational, prepaid, revenue, and payment transactions do.
- Fuel and toll usage should be matched to trips by vehicle, date range, route, reference, or controlled manual override.
- Unmatched imported transactions must remain visible as exceptions until resolved.
- Reports must reconcile operational trip costs with the General Ledger, sub-ledgers, prepaid balances, and multi-currency reporting.
