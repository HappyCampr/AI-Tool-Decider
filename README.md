## AI Automation Decision Framework

This tool evaluates architectural fit using organizational readiness,
problem structure, output requirements, and governance constraints.

flowchart TD

A[Start: Project Evaluation] --> B[Section 1: Organizational Context]

B --> C{AI Maturity}
C -->|None or Pilot| D[Check Change Readiness]
C -->|Production or Mature| E[Continue]

D --> E

E --> F{Project Data Maturity}

F -->|Low| G[Increase Automation Bias]
F -->|Moderate/High| H[Allow ML Consideration]

G --> I[Section 2: Problem Structure]
H --> I

I --> J{Workflow Defined?}

J -->|No| K[RPA Not Recommended]
J -->|Yes| L[Automation Candidate]

K --> M{Inputs Structured?}
L --> M

M -->|Structured| N[Automation or ML Candidate]
M -->|Mixed| O[ML or Hybrid Candidate]
M -->|Unstructured| P[LLM Candidate]

N --> Q[Section 3: Output Requirements]
O --> Q
P --> Q

Q --> R{Output Closed Set?}

R -->|Yes| S[Boost Automation + ML]
R -->|No| T[Boost LLM]

S --> U{Outputs Must Be Identical?}
T --> U

U -->|Yes| V[Reduce LLM Score]
U -->|Variation OK| W[LLM Allowed]

V --> X[Section 4: Risk & Governance]
W --> X

X --> Y{Risk Exposure}

Y -->|High| Z[Prefer Deterministic Systems]
Y -->|Medium| AA[Balanced ML + Automation]
Y -->|Low| AB[LLM Allowed]

Z --> AC{LLM Needed for Interpretation?}
AA --> AD[Score Architectures]
AB --> AD

AC -->|Yes| AE[Hybrid: LLM Agent + Deterministic Validation]
AC -->|No| AD

AE --> AD

AD --> AF[Calculate Scores]

AF --> AG{Scores Close?}

AG -->|Yes| AH[Hybrid Architecture Recommended]
AG -->|No| AI[Recommend Highest Scoring Architecture]

AI --> AJ[Generate Explanation Based on Answers]
AH --> AJ

AJ --> AK[Display Recommendation + Tradeoffs + Resources]

AK --> AL[End]
