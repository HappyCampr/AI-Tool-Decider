from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import dash
from dash import Dash, Input, Output, State, callback_context, dcc, html, no_update
import dash_bootstrap_components as dbc


# =========================================================
# Configuration
# =========================================================

APP_TITLE = "AI Automation Decision Framework"
HYBRID_THRESHOLD = 2

ARCH_AUTOMATION = "Automation"
ARCH_ML = "Machine Learning"
ARCH_LLM = "LLM"
ARCH_HYBRID = "Hybrid"
ARCH_NOT_READY = "Prerequisites Needed Before Automation"

SECTION_ORDER = [
    "organizational_context",
    "problem_structure",
    "output_requirements",
    "risk_governance",
]


# =========================================================
# Question model
# =========================================================

QUESTIONS: Dict[str, Dict[str, Any]] = {
    "q1_ai_maturity": {
        "section": "organizational_context",
        "title": "How mature is your organization’s current use of AI?",
        "help": "This helps assess whether advanced AI is realistic for the current environment.",
        "options": [
            ("none", "None — AI is not currently used in production"),
            ("pilot", "Pilot projects — small experiments or proofs of concept"),
            ("limited", "Limited production — a few operational AI systems"),
            ("mature", "Mature AI environment — multiple systems with monitoring and governance"),
        ],
    },
    "q2_project_data_maturity": {
        "section": "organizational_context",
        "title": "For this specific project, how reliable and prepared is the available data?",
        "help": "Focus on the project under consideration, not the enterprise overall.",
        "options": [
            ("fragmented", "Data is fragmented or inconsistent and would require significant cleanup"),
            ("transform", "Data exists but requires transformation or consolidation"),
            ("clean", "Data is clean and structured but not continuously maintained"),
            ("governed", "Data is well-governed with reliable pipelines and monitoring"),
        ],
    },
    "q3_change_readiness": {
        "section": "organizational_context",
        "title": "How prepared is the organization to support AI adoption for this project?",
        "help": "Examples include training staff, assigning owners, and establishing monitoring or governance processes.",
        "options": [
            ("low", "Low readiness — no clear ownership or training plan"),
            ("moderate", "Moderate readiness — some planning and sponsorship exist"),
            ("high", "High readiness — clear ownership, monitoring, and training plans"),
        ],
    },
    "q4_workflow_established": {
        "section": "problem_structure",
        "title": "Is there an established workflow for the process this project would replace or support?",
        "help": "Stable, documented workflows generally favor automation and RPA-style solutions.",
        "options": [
            ("no", "No — the process is inconsistent or informal"),
            ("undocumented", "Yes — but the steps are not clearly documented"),
            ("mapped", "Yes — and the workflow can be clearly mapped"),
        ],
    },
    "q4b_workflow_mappable": {
        "section": "problem_structure",
        "title": "Can the workflow be represented as a flowchart or decision tree?",
        "help": "If the process can be mapped, deterministic automation is usually more viable.",
        "options": [
            ("yes", "Yes — clear step-by-step logic exists"),
            ("partial", "Partially — some steps require judgment"),
            ("no", "No — the process relies heavily on interpretation"),
        ],
    },
    "q5_input_type": {
        "section": "problem_structure",
        "title": "What type of input data will the system process most often?",
        "help": "Structured = numbers, IDs, dropdowns, database fields. Mixed = forms plus notes. Unstructured = emails, documents, chats, PDFs.",
        "options": [
            ("structured", "Structured data"),
            ("mixed", "Mixed structured and text data"),
            ("unstructured", "Unstructured data"),
        ],
    },
    "q6_output_boundaries": {
        "section": "output_requirements",
        "title": "Are valid outputs limited to a predefined set of answers or numeric values?",
        "help": "Examples include selecting one category from a list, returning a specific calculation, or assigning a code from a predefined list.",
        "options": [
            ("closed", "Yes — outputs must come from a defined list or numeric range"),
            ("bounded", "Mostly — outputs are bounded but allow some variation"),
            ("open", "No — outputs may be open-ended text or explanations"),
        ],
    },
    "q7_output_consistency": {
        "section": "output_requirements",
        "title": "Do the tool’s outputs need to always be identical for the same input?",
        "help": "Generative AI systems may produce slightly different responses each time. If exact reproducibility is required, deterministic automation or ML may be a better fit.",
        "options": [
            ("identical", "Yes — results must always be exactly the same"),
            ("consistent", "Preferably — consistency is important but small variation is acceptable"),
            ("variation_ok", "No — variation in wording or explanation is acceptable"),
        ],
    },
    "q8_risk_exposure": {
        "section": "risk_governance",
        "title": "What would be the impact if the system produced an incorrect result?",
        "help": "Consider operational impact, customer harm, revenue impact, legal exposure, or safety consequences.",
        "options": [
            ("low", "Low — minor inconvenience or internal correction needed"),
            ("medium", "Medium — customer impact or revenue implications"),
            ("high", "High — legal, regulatory, financial, or safety consequences"),
        ],
    },
    "q9_explainability": {
        "section": "risk_governance",
        "title": "How important is the ability to explain how the system reached a decision?",
        "help": "Examples include regulatory requirements, internal audit processes, and maintaining user trust.",
        "options": [
            ("required", "Required — explanations must be auditable or documented"),
            ("important", "Important — users expect clear reasoning"),
            ("not_required", "Not required — outcome accuracy is the primary concern"),
        ],
    },
    "q10_monitoring": {
        "section": "risk_governance",
        "title": "Will this system require ongoing monitoring or human oversight?",
        "help": "Examples include reviewing flagged outputs, monitoring accuracy or drift, or approving high-risk decisions.",
        "options": [
            ("minimal", "Minimal oversight expected"),
            ("some", "Some monitoring and review required"),
            ("continuous", "Continuous monitoring and human oversight required"),
        ],
    },
    "q11_cost_justification": {
        "section": "risk_governance",
        "title": "Is the expected value of this project high enough to justify more complex and costly systems?",
        "help": "Examples of higher costs include model training and tuning, infrastructure and API usage, monitoring, and maintenance.",
        "options": [
            ("no", "No — lower-cost automation would be preferable"),
            ("possibly", "Possibly — benefits may justify moderate investment"),
            ("yes", "Yes — high value justifies complex systems"),
        ],
    },
    "q12_build_model": {
        "section": "risk_governance",
        "title": "Who needs to build and maintain this solution over time?",
        "help": "This helps distinguish UI-configurable automation, specialized ML teams, and code-based engineering-led approaches.",
        "options": [
            ("ops_ui", "Business or operations teams need UI-based configuration"),
            ("specialized_ml", "A highly specialized data science / MLOps team is available"),
            ("software_eng", "Software engineers can build and maintain code-based systems"),
        ],
    },
}

SECTION_META = {
    "organizational_context": {
        "title": "1. Organizational Context",
        "intro": "Evaluate whether the organization and project context support advanced AI systems.",
    },
    "problem_structure": {
        "title": "2. Problem Structure",
        "intro": "Determine whether the problem requires probabilistic AI or could be solved with simpler automation.",
    },
    "output_requirements": {
        "title": "3. Output Requirements",
        "intro": "Output constraints strongly determine the appropriate automation approach.",
    },
    "risk_governance": {
        "title": "4. Risk & Governance",
        "intro": "Evaluate operational risk, explainability, governance, and cost considerations.",
    },
}


def section_questions(section_key: str, answers: Dict[str, Any]) -> List[str]:
    base = [qk for qk, qv in QUESTIONS.items() if qv["section"] == section_key]
    ordered = []
    for key in [
        "q1_ai_maturity",
        "q2_project_data_maturity",
        "q3_change_readiness",
        "q4_workflow_established",
        "q4b_workflow_mappable",
        "q5_input_type",
        "q6_output_boundaries",
        "q7_output_consistency",
        "q8_risk_exposure",
        "q9_explainability",
        "q10_monitoring",
        "q11_cost_justification",
        "q12_build_model",
    ]:
        if key not in base:
            continue
        if key == "q3_change_readiness" and answers.get("q1_ai_maturity") not in {"none", "pilot"}:
            continue
        if key == "q4b_workflow_mappable" and answers.get("q4_workflow_established") == "no":
            continue
        ordered.append(key)
    return ordered


def all_visible_questions(answers: Dict[str, Any]) -> List[str]:
    visible: List[str] = []
    for section in SECTION_ORDER:
        visible.extend(section_questions(section, answers))
    return visible


# =========================================================
# Scoring + explanations
# =========================================================

ScoreDelta = Dict[str, int]


def delta(automation: int = 0, ml: int = 0, llm: int = 0, not_ready: int = 0) -> ScoreDelta:
    return {
        ARCH_AUTOMATION: automation,
        ARCH_ML: ml,
        ARCH_LLM: llm,
        ARCH_NOT_READY: not_ready,
    }


SCORE_TABLES: Dict[str, Dict[str, ScoreDelta]] = {
    "q2_project_data_maturity": {
        "fragmented": delta(automation=1, ml=-2, not_ready=2),
        "transform": delta(automation=1, ml=-1, not_ready=1),
        "clean": delta(ml=1),
        "governed": delta(ml=2),
    },
    "q3_change_readiness": {
        "low": delta(ml=-2, llm=-2),
        "moderate": delta(),
        "high": delta(ml=1, llm=1),
    },
    "q4_workflow_established": {
        "no": delta(automation=-1, not_ready=2),
        "undocumented": delta(automation=1, not_ready=1),
        "mapped": delta(automation=3),
    },
    "q4b_workflow_mappable": {
        "yes": delta(automation=2),
        "partial": delta(automation=1),
        "no": delta(automation=-1, not_ready=1),
    },
    "q5_input_type": {
        "structured": delta(automation=1, ml=1),
        "mixed": delta(automation=1, ml=1, llm=1),
        "unstructured": delta(llm=2),
    },
    "q6_output_boundaries": {
        "closed": delta(automation=2, ml=2),
        "bounded": delta(automation=1, ml=1),
        "open": delta(llm=2),
    },
    "q7_output_consistency": {
        "identical": delta(automation=2, ml=2, llm=-3),
        "consistent": delta(automation=1, ml=1),
        "variation_ok": delta(llm=2),
    },
    "q8_risk_exposure": {
        "low": delta(),
        "medium": delta(automation=1, ml=2, llm=-1),
        "high": delta(automation=3, ml=1, llm=-2),
    },
    "q9_explainability": {
        "required": delta(automation=2, ml=1, llm=-1),
        "important": delta(automation=1, ml=1),
        "not_required": delta(llm=1),
    },
    "q10_monitoring": {
        "minimal": delta(automation=1),
        "some": delta(ml=1),
        "continuous": delta(llm=1),
    },
    "q11_cost_justification": {
        "no": delta(automation=1, llm=-2, not_ready=1),
        "possibly": delta(automation=1, ml=2),
        "yes": delta(ml=1, llm=2),
    },
    "q12_build_model": {
        "ops_ui": delta(automation=3),
        "specialized_ml": delta(ml=2),
        "software_eng": delta(automation=2, llm=2),
    },
}


EXPLANATION_TEMPLATES: Dict[str, Dict[str, str]] = {
    "q2_project_data_maturity": {
        "fragmented": "Project data is fragmented or inconsistent, which raises implementation risk for ML-heavy approaches and suggests prerequisite cleanup work.",
        "transform": "The project data exists but still requires transformation or consolidation, which may slow more advanced modeling efforts.",
        "clean": "The project data is clean and structured, which improves the viability of bounded ML use cases.",
        "governed": "The project has well-governed data pipelines and monitoring, which supports more advanced model-based approaches.",
    },
    "q3_change_readiness": {
        "low": "The organization has limited readiness to support AI change, reducing fit for ML or LLM approaches that require monitoring, ownership, and enablement.",
        "moderate": "The organization has some readiness to support AI adoption, but not enough to strongly favor advanced AI on that basis alone.",
        "high": "The organization has strong readiness to support AI adoption, which improves the feasibility of advanced AI approaches where appropriate.",
    },
    "q4_workflow_established": {
        "no": "The target process is not yet stable or well-defined, which weakens the case for RPA-style automation and may indicate that workflow design should come first.",
        "undocumented": "A workflow exists, but documentation and mapping work may be needed before reliable automation can be implemented.",
        "mapped": "The workflow is already clear and mappable, which strongly favors deterministic automation approaches.",
    },
    "q4b_workflow_mappable": {
        "yes": "Because the workflow can be expressed as a flowchart or decision tree, deterministic automation is more viable.",
        "partial": "Some workflow steps can be mapped, but judgment-based branches may require a hybrid design or human review.",
        "no": "The workflow relies heavily on interpretation, which weakens the fit for pure RPA-style automation.",
    },
    "q5_input_type": {
        "structured": "The system mainly processes structured inputs such as IDs, numbers, or database fields, which supports deterministic automation and bounded ML.",
        "mixed": "The system processes mixed inputs, which may support either bounded ML or an AI-assisted hybrid design depending on output constraints.",
        "unstructured": "The system processes unstructured content such as emails, documents, or chat, which increases the need for language understanding.",
    },
    "q6_output_boundaries": {
        "closed": "Outputs are constrained to a defined list or numeric range, which is typically a strong fit for deterministic automation or bounded ML.",
        "bounded": "Outputs are somewhat constrained, which may support deterministic logic with moderate model assistance.",
        "open": "Outputs are open-ended or generative, which increases the suitability of LLM-based approaches.",
    },
    "q7_output_consistency": {
        "identical": "You indicated outputs must be identical for the same inputs, which favors deterministic automation or bounded ML over generative systems.",
        "consistent": "You prefer consistency in outputs, which supports bounded automation or ML more than fully generative systems.",
        "variation_ok": "Variation in wording or explanation is acceptable, which increases the suitability of LLM-based approaches.",
    },
    "q8_risk_exposure": {
        "low": "The downside of an incorrect output is relatively low, which leaves more flexibility in architecture choice.",
        "medium": "The workflow has meaningful customer or revenue impact, which increases the value of predictable, governed solutions.",
        "high": "The workflow has high legal, regulatory, financial, or safety impact, which strongly favors predictable and auditable architectures.",
    },
    "q9_explainability": {
        "required": "Explainability is required, which favors auditable logic and makes black-box generative behavior less appropriate as a final decision path.",
        "important": "Explainability is important, increasing the value of interpretable models or workflow logic.",
        "not_required": "Explainability is less important for this use case, which leaves more room for generative techniques where other constraints allow them.",
    },
    "q10_monitoring": {
        "minimal": "Minimal oversight is expected, which favors lower-maintenance deterministic approaches.",
        "some": "Some monitoring is acceptable, which supports bounded ML or controlled automation with review points.",
        "continuous": "Continuous monitoring and human oversight are acceptable, which can support more advanced AI patterns when needed.",
    },
    "q11_cost_justification": {
        "no": "Higher-cost AI architectures are difficult to justify here, which increases the appeal of simpler automation.",
        "possibly": "Moderate investment may be justified, which can support bounded ML where value is measurable.",
        "yes": "The expected value can justify more complex systems, leaving room for ML or LLM-based designs where they are a strong fit.",
    },
    "q12_build_model": {
        "ops_ui": "Business or operations teams need UI-based configuration, which strongly favors configurable automation platforms.",
        "specialized_ml": "A specialized data science or MLOps team is available, which improves the feasibility of ML solutions.",
        "software_eng": "Software engineers are available to maintain code-based systems, which supports either engineered automation or LLM-based workflows with guardrails.",
    },
}


@dataclass
class EvaluationResult:
    scores: Dict[str, int]
    primary: str
    secondary: Optional[str]
    recommendation_label: str
    confidence: str
    key_drivers: List[str]
    exclusions: List[str]
    tradeoffs: Dict[str, str]
    resources: List[str]
    phased_plan: List[str]
    why_not: Dict[str, List[str]]


TRADEOFFS = {
    ARCH_AUTOMATION: {
        "Build complexity": "Low–Medium",
        "Operational risk": "Low",
        "Maintenance burden": "Low–Medium",
        "Governance requirement": "Low–Medium",
    },
    ARCH_ML: {
        "Build complexity": "Medium",
        "Operational risk": "Medium",
        "Maintenance burden": "Medium",
        "Governance requirement": "Medium",
    },
    ARCH_LLM: {
        "Build complexity": "Medium",
        "Operational risk": "Medium–High",
        "Maintenance burden": "Medium–High",
        "Governance requirement": "High",
    },
    ARCH_HYBRID: {
        "Build complexity": "Medium–High",
        "Operational risk": "Medium",
        "Maintenance burden": "Medium–High",
        "Governance requirement": "High",
    },
    ARCH_NOT_READY: {
        "Build complexity": "Not advised yet",
        "Operational risk": "High if forced early",
        "Maintenance burden": "High relative to value",
        "Governance requirement": "Prerequisites needed first",
    },
}


def evaluate_answers(answers: Dict[str, Any]) -> EvaluationResult:
    scores = {
        ARCH_AUTOMATION: 0,
        ARCH_ML: 0,
        ARCH_LLM: 0,
        ARCH_NOT_READY: 0,
    }
    key_drivers: List[str] = []
    exclusions: List[str] = []
    why_not = {
        ARCH_AUTOMATION: [],
        ARCH_ML: [],
        ARCH_LLM: [],
    }

    # Apply score tables
    for q_key, answer in answers.items():
        deltas = SCORE_TABLES.get(q_key, {}).get(answer)
        if deltas:
            for arch, value in deltas.items():
                scores[arch] += value
        text = EXPLANATION_TEMPLATES.get(q_key, {}).get(answer)
        if text:
            key_drivers.append(text)

    # Gates / exclusions
    risk_high = answers.get("q8_risk_exposure") == "high"
    deterministic_required = answers.get("q7_output_consistency") == "identical"
    input_unstructured = answers.get("q5_input_type") == "unstructured"
    input_mixed = answers.get("q5_input_type") == "mixed"
    workflow_no = answers.get("q4_workflow_established") == "no"
    workflow_not_mappable = answers.get("q4b_workflow_mappable") == "no"

    llm_final_blocked = False
    if risk_high and deterministic_required:
        llm_final_blocked = True
        exclusions.append(
            "LLM should not be used as the final decision-maker because the use case is both high risk and requires deterministic outputs."
        )
        scores[ARCH_LLM] -= 2
        why_not[ARCH_LLM].append(
            "The use case combines high risk with a requirement for identical outputs, which makes a standalone generative final-output approach a poor fit."
        )

    rpa_blocked = False
    if workflow_no or workflow_not_mappable:
        rpa_blocked = True
        exclusions.append(
            "RPA-style automation is not recommended until the workflow can be clearly defined and mapped."
        )
        why_not[ARCH_AUTOMATION].append(
            "Pure UI-driven automation depends on a stable, mappable workflow, which is not yet present here."
        )

    # Determine primary scores
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_arch, primary_score = ranked[0]
    second_arch, second_score = ranked[1]

    # Hybrid rules: close scores or LLM used only for interpretation
    hybrid_needed = False
    hybrid_primary = None
    hybrid_secondary = None

    if llm_final_blocked and (input_unstructured or input_mixed):
        hybrid_needed = True
        hybrid_primary = ARCH_AUTOMATION if scores[ARCH_AUTOMATION] >= scores[ARCH_ML] else ARCH_ML
        hybrid_secondary = ARCH_LLM
        exclusions.append(
            "If LLM is used here, it should be limited to interpretation, extraction, or summarization before deterministic validation."
        )

    elif abs(primary_score - second_score) <= HYBRID_THRESHOLD and primary_arch != ARCH_NOT_READY and second_arch != ARCH_NOT_READY:
        hybrid_needed = True
        hybrid_primary = primary_arch
        hybrid_secondary = second_arch

    # Not-ready rule
    data_fragmented = answers.get("q2_project_data_maturity") == "fragmented"
    change_low = answers.get("q3_change_readiness") == "low"
    if scores[ARCH_NOT_READY] >= max(scores[ARCH_AUTOMATION], scores[ARCH_ML], scores[ARCH_LLM]) or (
        workflow_no and data_fragmented and change_low
    ):
        recommendation_label = ARCH_NOT_READY
        primary = ARCH_NOT_READY
        secondary = None
        confidence = "High" if scores[ARCH_NOT_READY] >= primary_score else "Medium"
        tradeoffs = TRADEOFFS[ARCH_NOT_READY]
    elif hybrid_needed and hybrid_primary and hybrid_secondary:
        recommendation_label = f"Hybrid: {hybrid_primary} + {hybrid_secondary}"
        primary = hybrid_primary
        secondary = hybrid_secondary
        gap = abs(primary_score - second_score)
        confidence = "High" if gap <= 1 else "Medium"
        tradeoffs = TRADEOFFS[ARCH_HYBRID]
    else:
        recommendation_label = primary_arch
        primary = primary_arch
        secondary = None
        gap = primary_score - second_score
        confidence = "High" if gap >= 4 else "Medium" if gap >= 2 else "Low"
        tradeoffs = TRADEOFFS[primary_arch]

    if recommendation_label != ARCH_NOT_READY:
        if ARCH_AUTOMATION != primary:
            why_not[ARCH_AUTOMATION].append("Automation was not the top fit based on the current balance of workflow structure, input type, and output requirements.")
        if ARCH_ML != primary:
            why_not[ARCH_ML].append("Machine learning was not the top fit based on current data maturity, output constraints, or operating model requirements.")
        if ARCH_LLM != primary and secondary != ARCH_LLM:
            why_not[ARCH_LLM].append("A standalone LLM approach was not the top fit based on current determinism, risk, or explainability constraints.")

    resources = determine_resources(answers, recommendation_label)
    phased_plan = determine_phased_plan(answers, recommendation_label)

    return EvaluationResult(
        scores=scores,
        primary=primary,
        secondary=secondary,
        recommendation_label=recommendation_label,
        confidence=confidence,
        key_drivers=dedupe_preserve_order(key_drivers)[:8],
        exclusions=dedupe_preserve_order(exclusions),
        tradeoffs=tradeoffs,
        resources=resources,
        phased_plan=phased_plan,
        why_not=why_not,
    )


def determine_resources(answers: Dict[str, Any], recommendation_label: str) -> List[str]:
    resources: List[str] = []
    if answers.get("q1_ai_maturity") in {"none", "pilot"}:
        resources.append("Minimum viable AI governance checklist")
    if answers.get("q8_risk_exposure") == "high":
        resources.append("Human-in-the-loop control patterns")
        resources.append("Audit logging and exception handling checklist")
    if answers.get("q9_explainability") == "required":
        resources.append("Decision trace and explainability template")
    if answers.get("q4_workflow_established") in {"no", "undocumented"}:
        resources.append("Workflow discovery and process mapping worksheet")
    if "Hybrid" in recommendation_label:
        resources.append("Hybrid architecture pattern: interpretation plus deterministic validation")
    if not resources:
        resources.append("Implementation KPI starter template")
    return dedupe_preserve_order(resources)


def determine_phased_plan(answers: Dict[str, Any], recommendation_label: str) -> List[str]:
    phases: List[str] = []
    if recommendation_label == ARCH_NOT_READY:
        phases.extend([
            "Phase 0 — Standardize the workflow, clarify ownership, and address obvious data gaps.",
            "Phase 1 — Re-evaluate the use case once process structure, data readiness, and governance improve.",
            "Phase 2 — Pilot the simplest viable automation approach before considering more advanced AI.",
        ])
        return phases

    needs_prereqs = answers.get("q4_workflow_established") in {"no", "undocumented"} or answers.get("q2_project_data_maturity") in {"fragmented", "transform"}
    if needs_prereqs:
        phases.append("Phase 0 — Complete prerequisite work: process mapping, data cleanup, ownership, and monitoring definitions.")

    phases.append("Phase 1 — Build a constrained MVP with clear success metrics, audit logging, and exception handling.")
    phases.append("Phase 2 — Pilot with a limited user group and monitor quality, cost, and operational burden.")
    phases.append("Phase 3 — Scale only after the architecture performs reliably under governance controls.")
    return phases


def dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    output = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


# =========================================================
# UI helpers
# =========================================================


def welcome_layout() -> dbc.Container:
    return dbc.Container(
        [
            html.H1(APP_TITLE, className="mt-4"),
            html.P(
                "Evaluate the right level of intelligence for a workflow by balancing organizational readiness, problem structure, output requirements, and governance constraints.",
                className="lead",
            ),
            dbc.Alert(
                "This framework is designed to discourage unnecessary AI complexity and make tradeoffs transparent.",
                color="light",
            ),
            dbc.Button("Start Review", id="btn-start", color="primary", size="lg"),
        ],
        style={"maxWidth": "920px"},
    )


def review_layout(answers: Dict[str, Any]) -> dbc.Container:
    rows = []
    for q_key in all_visible_questions(answers):
        question = QUESTIONS[q_key]
        selected = answers.get(q_key)
        label = next((lbl for val, lbl in question["options"] if val == selected), "Not answered")
        rows.append(
            html.Tr([html.Td(question["title"]), html.Td(label)])
        )

    return dbc.Container(
        [
            html.H2("Review Your Inputs", className="mt-4"),
            html.P("Confirm your answers before generating the recommendation."),
            dbc.Table(
                [html.Thead(html.Tr([html.Th("Question"), html.Th("Selected Answer")])), html.Tbody(rows)],
                bordered=True,
                hover=True,
                responsive=True,
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Button("Back", id="btn-back", color="secondary", outline=True)),
                    dbc.Col(dbc.Button("Generate Recommendation", id="btn-submit", color="primary"), style={"textAlign": "right"}),
                ],
                className="mt-3",
            ),
        ],
        style={"maxWidth": "980px"},
    )


def score_bars(scores: Dict[str, int]) -> html.Div:
    min_score = min(scores.values())
    adjusted = {k: v - min_score + 1 for k, v in scores.items()}
    max_adjusted = max(adjusted.values()) if adjusted else 1

    cards = []
    for arch in [ARCH_AUTOMATION, ARCH_ML, ARCH_LLM, ARCH_NOT_READY]:
        value = scores[arch]
        pct = int((adjusted[arch] / max_adjusted) * 100)
        cards.append(
            dbc.Card(
                dbc.CardBody([
                    html.Div(arch, className="fw-bold"),
                    dbc.Progress(value=pct, className="my-2"),
                    html.Div(f"Score: {value}"),
                ]),
                className="mb-2",
            )
        )
    return html.Div(cards)


def results_layout(result: EvaluationResult, answers: Dict[str, Any]) -> dbc.Container:
    why_not_items = []
    for arch, reasons in result.why_not.items():
        if reasons:
            why_not_items.append(
                dbc.AccordionItem(
                    html.Ul([html.Li(reason) for reason in dedupe_preserve_order(reasons)[:3]]),
                    title=f"Why not {arch}",
                )
            )

    return dbc.Container(
        [
            html.H2("Recommendation", className="mt-4"),
            dbc.Badge(result.recommendation_label, color="success", className="mb-2", style={"fontSize": "1rem"}),
            html.Div(f"Confidence: {result.confidence}", className="mb-3 text-muted"),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Executive Summary"),
                                html.Ul([html.Li(x) for x in result.key_drivers[:5]]),
                            ])
                        ),
                        md=7,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Architecture Fit Scores"),
                                score_bars(result.scores),
                            ])
                        ),
                        md=5,
                    ),
                ],
                className="g-3",
            ),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Architectural Tradeoffs"),
                                html.Ul([html.Li(f"{k}: {v}") for k, v in result.tradeoffs.items()]),
                            ])
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Exclusions and Constraints"),
                                html.Ul([html.Li(x) for x in result.exclusions]) if result.exclusions else html.P("No hard exclusions were triggered."),
                            ])
                        ),
                        md=6,
                    ),
                ],
                className="g-3 mt-1",
            ),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Implementation Path"),
                                html.Ol([html.Li(x) for x in result.phased_plan]),
                            ])
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Recommended Resources"),
                                html.Ul([html.Li(x) for x in result.resources]),
                            ])
                        ),
                        md=6,
                    ),
                ],
                className="g-3 mt-1",
            ),

            dbc.Card(
                dbc.CardBody([
                    html.H4("Alternative Analysis"),
                    dbc.Accordion(why_not_items or [dbc.AccordionItem("No alternative analysis available.", title="Why not other options")], start_collapsed=True),
                ]),
                className="mt-3",
            ),

            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        html.Ul([html.Li(f"{QUESTIONS[q]['title']} — {next(lbl for val, lbl in QUESTIONS[q]['options'] if val == answers[q])}") for q in all_visible_questions(answers)]),
                        title="Your submitted answers",
                    )
                ],
                start_collapsed=True,
                className="mt-3",
            ),

            dbc.Row(
                [
                    dbc.Col(dbc.Button("Start Over", id="btn-restart", color="secondary", outline=True)),
                    dbc.Col(dbc.Button("Back to Review", id="btn-back", color="primary", outline=True), style={"textAlign": "right"}),
                ],
                className="mt-4 mb-5",
            ),
        ],
        style={"maxWidth": "1100px"},
    )


def question_card(q_key: str, answers: Dict[str, Any], current_index: int, total_questions: int) -> dbc.Container:
    q = QUESTIONS[q_key]
    progress_overall = int((current_index / total_questions) * 100)
    current_section = q["section"]
    section_qs = section_questions(current_section, answers)
    section_index = section_qs.index(q_key) + 1
    section_total = len(section_qs)
    progress_section = int((section_index / section_total) * 100)

    return dbc.Container(
        [
            html.H2(SECTION_META[current_section]["title"], className="mt-4"),
            html.P(SECTION_META[current_section]["intro"], className="text-muted"),
            html.Div("Overall progress", className="small text-muted"),
            dbc.Progress(value=progress_overall, className="mb-3"),
            html.Div(f"Section progress: {section_index} of {section_total}", className="small text-muted"),
            dbc.Progress(value=progress_section, className="mb-4"),
            dbc.Card(
                dbc.CardBody([
                    html.H4(q["title"]),
                    dbc.Alert(q["help"], color="light", className="mt-2"),
                    dbc.RadioItems(
                        id="current-answer",
                        options=[{"label": label, "value": value} for value, label in q["options"]],
                        value=answers.get(q_key),
                        className="mt-3",
                    ),
                ]),
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Button("Back", id="btn-back", color="secondary", outline=True)),
                    dbc.Col(dbc.Button("Next", id="btn-next", color="primary"), style={"textAlign": "right"}),
                ],
                className="mt-4",
            ),
        ],
        style={"maxWidth": "920px"},
    )


# =========================================================
# Dash app
# =========================================================

app: Dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = APP_TITLE
server = app.server

app.layout = html.Div(
    [
        dcc.Store(id="store-answers", data={}),
        dcc.Store(id="store-page", data={"mode": "welcome", "question_idx": 0}),
        html.Div(id="page-content"),
    ]
)


@app.callback(
    Output("store-page", "data"),
    Output("store-answers", "data"),
    Input("btn-start", "n_clicks"),
    Input("btn-next", "n_clicks"),
    Input("btn-back", "n_clicks"),
    Input("btn-submit", "n_clicks"),
    Input("btn-restart", "n_clicks"),
    State("store-page", "data"),
    State("store-answers", "data"),
    State("current-answer", "value"),
    prevent_initial_call=True,
)
def handle_navigation(start, next_clicks, back_clicks, submit_clicks, restart_clicks, page_state, answers, current_answer):
    answers = answers or {}
    page_state = page_state or {"mode": "welcome", "question_idx": 0}

    triggered = callback_context.triggered[0]["prop_id"].split(".")[0] if callback_context.triggered else None
    visible_qs = all_visible_questions(answers)
    mode = page_state.get("mode", "welcome")
    idx = page_state.get("question_idx", 0)

    if triggered == "btn-restart":
        return {"mode": "welcome", "question_idx": 0}, {}

    if triggered == "btn-start":
        return {"mode": "question", "question_idx": 0}, answers

    if mode == "question" and visible_qs and 0 <= idx < len(visible_qs) and current_answer is not None:
        q_key = visible_qs[idx]
        answers = {**answers, q_key: current_answer}
        visible_qs = all_visible_questions(answers)

    if triggered == "btn-next":
        if mode == "question":
            if idx + 1 < len(visible_qs):
                return {"mode": "question", "question_idx": idx + 1}, answers
            return {"mode": "review", "question_idx": idx}, answers
        return no_update, answers

    if triggered == "btn-back":
        if mode == "results":
            return {"mode": "review", "question_idx": max(len(visible_qs) - 1, 0)}, answers
        if mode == "review":
            return {"mode": "question", "question_idx": max(len(visible_qs) - 1, 0)}, answers
        if mode == "question":
            if idx > 0:
                return {"mode": "question", "question_idx": idx - 1}, answers
            return {"mode": "welcome", "question_idx": 0}, answers

    if triggered == "btn-submit":
        return {"mode": "results", "question_idx": idx}, answers

    return no_update, answers


@app.callback(
    Output("page-content", "children"),
    Input("store-page", "data"),
    Input("store-answers", "data"),
)
def render_page(page_state, answers):
    answers = answers or {}
    page_state = page_state or {"mode": "welcome", "question_idx": 0}
    mode = page_state.get("mode", "welcome")
    idx = page_state.get("question_idx", 0)

    if mode == "welcome":
        return welcome_layout()

    if mode == "review":
        return review_layout(answers)

    if mode == "results":
        result = evaluate_answers(answers)
        return results_layout(result, answers)

    visible_qs = all_visible_questions(answers)
    if not visible_qs:
        return welcome_layout()

    idx = max(0, min(idx, len(visible_qs) - 1))
    q_key = visible_qs[idx]
    return question_card(q_key, answers, idx + 1, len(visible_qs))


if __name__ == "__main__":
    app.run(debug=True)
