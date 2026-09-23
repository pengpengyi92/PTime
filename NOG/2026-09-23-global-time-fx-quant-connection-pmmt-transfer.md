# EPIC — Global Time Arbitrage × Connection × FX Quant DD × PMMT Transfer

**Date:** 2026-09-23  
**Status:** EPIC / cross-system  
**Systems:** PTime · P-Global · P-Connection · Pengyi OS · PJS · PMMT · PFICC

## 1. Why this is EPIC

This note captures a high-leverage global operating loop:

> **Time-zone arbitrage + trusted expert network + domain due diligence + immediate model transfer + job/interview execution**

Shenzhen night is Boston working daytime and overlaps with London afternoon. PTime therefore converts otherwise “dead” local evening hours into high-value global research, networking, consulting, recruiting, and interview preparation windows.

The current concrete case is especially strong:
- Tencent FX / cross-border payment opportunity is moving forward.
- Before the next Tencent conversation, use PTime to schedule a 30-minute paid consultation with Xian Ming / State Street FX Quant in Boston.
- Extract institutional FX knowledge directly from a practitioner.
- Transfer the result into PMMT / PFICC / Tencent interview preparation immediately.

This is not merely networking. It is a **global knowledge-compounding loop**.

## 2. FICC business map: two economic directions

A useful first-principles split for FICC is:

### A. Client business
Serve corporate / institutional clients.

Typical activities:
- client flow
- sales & trading
- RFQ / quote
- spot / forward / swap / options
- hedging solutions
- execution
- liquidity provision / market making
- client pricing

Economic loop:

```text
Client Need / Flow
→ Price / Quote
→ Trade
→ Inventory / Exposure
→ Internalize or Hedge
→ Spread / Fee / PnL
```

### B. Proprietary / risk-taking business
Use the institution’s risk budget to earn PnL from market views, relative value, carry, alpha, or systematic strategies.

Typical activities:
- directional trading
- relative value
- carry
- systematic alpha
- statistical / macro strategies
- risk allocation

These two directions interact. Market making often sits at the boundary: the dealer serves client flow but temporarily carries principal inventory risk and must decide how and when to hedge.

## 3. Pricing is common infrastructure across both directions

Both client business and proprietary trading require a pricing / valuation layer.

### Client business
Need to answer:
- What is fair value now?
- What spread should this client receive?
- How should inventory and hedge cost alter the quote?
- Which venue / liquidity provider should be used?
- Should the client flow be internalized or externally hedged?

### Proprietary trading
Need to answer:
- What is fair value?
- What is expected return / alpha?
- Where is the market mispriced?
- How large should the position be?
- What is the cost of entering, carrying, and hedging the position?

Hence a common abstraction:

```text
Data
→ Fair Value
→ Pricing / Forecast
→ Quote or Position
→ Execution
→ Hedge / Inventory
→ Risk / PnL / Attribution
```

## 4. State Street FX Quant DD: question architecture

The Boston consultation should not be a generic “what does FX Quant do?” conversation.

Use the existing Equity / Futures / PMMT mental model and ask the practitioner to map it into institutional FX.

### Module 1 — Business Map
Questions:
- Who does the FX desk serve?
- What proportion is institutional client flow, market making, execution, research, or proprietary/risk-taking?
- Where does FX Quant sit in the desk?
- Which desks / traders / sales / execution teams consume Quant output?

### Module 2 — What FX Quant actually builds
Validate the real model mix:
- pricing / valuation
- alpha / forecasting
- execution algorithms
- TCA
- liquidity models
- client-flow modelling
- market-impact models
- hedging optimization
- inventory / risk models
- venue / LP selection
- monitoring / attribution

Key question:

> In day-to-day institutional FX Quant work, which of these model families matter most and what does the output actually look like?

## 5. Equity/Futures → FX data mapping

Existing Equity/Futures mental model:

```text
Fundamental
+
Price / Volume
+
L0 Bars
L1 BBO
L2 Order Book
L3 Order / Event / Queue
```

Ask how this maps to FX.

### FX fundamental layer
FX “fundamental” is largely relative macro rather than company-specific fundamental analysis.

Important candidates:
- central-bank policy
- rate expectations
- yield curves
- interest-rate differential
- inflation
- employment
- growth
- balance of payments
- capital flows
- risk sentiment
- structural currency supply / demand
- cross-currency basis

Core idea:

> **Equity fundamental ≈ company economics; FX fundamental ≈ relative macro + relative rates + cross-country capital flows.**

### FX market-data layer
Do not mechanically copy exchange-based L0/L1/L2/L3 concepts.

Institutional FX is fragmented and dealer / venue / OTC driven. Validate:
- bars / trades
- BBO
- venue depth
- dealer quotes
- RFQ
- client flow
- LP quotes
- forward points
- swap points
- execution / TCA records
- internal inventory
- counterparty / venue liquidity

Key DD question:

> What is actually observable at each layer, and what data is proprietary to the institution?

## 6. PMMT validation question

Use PMMT directly as a hypothesis to test:

```text
Fair Value
+
Inventory
+
Volatility
+
Order / Client Flow
+
Liquidity
+
Funding / Hedge Cost
→
Bid / Ask + Size + Skew
→
Execution / Hedge
→
Inventory / Risk / PnL Feedback
```

Ask:

> In real institutional FX, which parts of this abstraction are correct, which variables dominate, and which must be replaced or extended by FX-specific factors?

Candidate FX-specific additions:
- rate differential
- forward points
- swap points
- cross-currency basis
- client-flow segmentation
- internalization probability
- counterparty
- venue / LP liquidity
- hedge cost
- funding
- settlement / tenor effects

## 7. Equity/Futures Quant → FX Quant transition

High-value question:

> If someone has primarily done Equity / Futures Quant and now moves into FX, what is the highest-ROI 20% of knowledge to learn first?

Separate:

### Transferable
- statistics / ML
- time-series modelling
- factor / alpha research
- market microstructure
- execution
- backtesting
- risk
- data engineering
- systematic experimentation

### FX-specific
Validate priorities around:
- macro / rates
- spot-forward-swap relationships
- forward points
- tenor structure
- dealer / OTC microstructure
- fragmented liquidity
- client flow
- hedging
- funding / basis
- institutional execution

## 8. Tencent cross-border payment bridge

Final consultation module:

> If the institution is not a bank dealer but a cross-border payment platform with large real payment/client flows, what are the central FX Quant / pricing / hedging problems?

Working hypothesis:

```text
Payment / Client Flow
→ Exposure Aggregation
→ Fair Pricing
→ Client Pricing
→ Inventory / Netting
→ LP / Venue Selection
→ Hedge Execution
→ TCA / Risk / PnL Monitoring
```

This is the direct bridge:

```text
State Street FX Quant
        ↓
Institutional FX mental model
        ↓
Tencent Cross-border Payment / FX
        ↓
PMMT / PFICC architecture
```

## 9. PTime × P-Global × P-Connection operating loop

The deeper insight is the workflow itself:

```text
Local Opportunity Appears
        ↓
Identify Missing Knowledge
        ↓
P-Connection finds practitioner
        ↓
PTime finds optimal global work window
        ↓
P-Global maps city / institution / market
        ↓
Paid Consultation / Informal Meeting
        ↓
Extract real institutional knowledge
        ↓
Update PMMT / PFICC / Pengyi OS
        ↓
Use immediately in interview / application / build
        ↓
Create stronger artifacts and new connections
        ↺
```

This turns global networking into an **active research infrastructure** rather than a static contact list.

## 10. Immediate execution

1. Send Tencent follow-up and request a short informal meeting.
2. Tonight Shenzhen time, reach out to Xian Ming in Boston.
3. Book ~30-minute paid consultation using the previous consulting format.
4. Prepare one-page question sheet using:
   - Business
   - Data
   - Model
   - Pricing
   - Execution / Hedging
   - Equity→FX Transfer
   - Cross-border Payment Mapping
5. After the call, immediately convert answers into:
   - PMMT model updates
   - PFICC market map
   - Tencent interview questions
   - P-Connection relationship record
   - PTime timezone playbook
   - P-Global Boston / FX node

## 11. Core thesis

> **PTime is not a clock utility. It is a global opportunity router.**

> **P-Connection is not a CRM. It is a human knowledge-access layer.**

> **P-Global is not a map. It is the geographic layer of the opportunity graph.**

> **PMMT is not only a crypto market maker. It can become a multi-asset institutional pricing / inventory / liquidity / execution engine.**

The combined system creates a repeatable loop:

**Global Time → Global People → Institutional Knowledge → Model Transfer → Artifact → Opportunity → New Global Connections.**
