# Original request — Remotion deck refactor

> Refactor the existing Remotion composition (don't start over). Use the remotion-best-practices and remotion-markup skills and `@remotion/transitions`. 1920x1080, 30fps, ~48s. Follow the FraudLens AI deck: Inter font (`@remotion/google-fonts/Inter`), palette from `src/theme.ts`. Near-black, warm white and lime dominate; coral only for risk, mint only for human review/validated, violet only for retrieved citations. Rounded panels (`#111214`, 1px subtle border, 24px radius), small uppercase lime section labels with letter-spacing, big bold headlines like the deck.
>
> **Transitions:** wrap scenes in `TransitionSeries`, with 18-frame overlaps using `springTiming`. Alternate `fade`, `slide({direction:"from-right"})` and `wipe`. No hard cuts. Add a persistent layer outside the series: a bottom pipeline rail `ALERT → SCORE → EVIDENCE → BRIEF` whose active pill fills lime as scenes advance, plus a faint grid and a slow lime glow that drifts across scenes.
>
> **Motion rules:** spring-in every element with a 4-6 frame stagger. Slow 1.00→1.04 push-in on each scene. Numbers count up with ease-out. Lines draw with `strokeDashoffset`. Text types out with a cursor. Nothing static for more than 1s.
>
> **Scenes:**
>
> 1. 0-4s Title: logo mark draws in, "Every suspicious transaction should come with an explanation." Chips ALERT → EVIDENCE → EXPLANATION light up in sequence, last one filled lime.
> 2. 4-9s Problem: "90%+" counts up, caption "of transaction-monitoring alerts are false positives." Three bullets (Transaction records, Account activity, Policies & case history) stagger in. Footer "Source: McKinsey".
> 3. 9-15s Incoming alert: transaction card slides in ($48.5K, new counterparty, 4.1× typical amount). Badge "ILLUSTRATIVE EXAMPLE — NOT LIVE CUSTOMER DATA".
> 4. 15-23s Detect: the card travels into a "LightGBM AML baseline" node, then a risk-score gauge animates and crosses a threshold line. The score and flag turn coral.
> 5. 23-33s Explain: four evidence cards (Transactions, Account history, Policies, Case notes) fly into a central RAG node labelled "retrieve • ground • draft", with lime dotted paths and pulses.
> 6. 33-42s Brief: "ALERT BRIEF / #0248 — Why this transfer merits review" types out. Citation chips (Transaction record, Account history, AML policy) pop in with violet highlights. Lime line: "Suggested next step: verify source of funds." Mint chip: "Human review required."
> 7. 42-48s Close: "From alert to accountable answer." with "Seeking AML design partners."
>
> Drive all text and numbers from `src/data/transactions.json`. Keep scene durations in one config. Render with `remotion-render`.
