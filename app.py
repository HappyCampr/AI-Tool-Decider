from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import dash
from dash import ALL, Dash, Input, Output, State, callback_context, dcc, html, no_update
import dash_bootstrap_components as dbc


# =========================================================
# Configuration
# =========================================================

APP_TITLE = "AI Automation Decision Framework"
HYBRID_THRESHOLD = 2

ARCH_PROCESS = "Process Clarification or Manual Improvement First"
ARCH_ANALYTICS = "Traditional Analytics / Decision Support"
ARCH_AUTOMATION = "Deterministic Automation"
ARCH_ML = "Machine Learning"
ARCH_LLM = "LLM-Assisted Workflow"
ARCH_HYBRID = "Hybrid"
ARCH_NOT_READY = "Prerequisites Needed Before Implementation"

FIT_ARCHITECTURES = [
    ARCH_ANALYTICS,
    ARCH_AUTOMATION,
    ARCH_ML,
    ARCH_LLM,
]

SECTION_ORDER = [
    "problem_value",
    "organizational_context",
    "problem_structure",
    "output_requirements",
    "human_use",
    "risk_governance",
]


# =========================================================
# Question model
# =========================================================

QUESTIONS: Dict[str, Dict[str, Any]] = {
    "q0_problem_definition": {
        "section": "problem_value",
        "title": "How clearly is the problem this project should solve defined?",
        "help": "A technology recommendation is only useful when the underlying business problem is clear.",
        "options": [
            ("clear", "Clear - the problem, affected users, and desired outcome are documented"),
            ("partial", "Partial - the general issue is known, but important details are still unclear"),
            ("unclear", "Unclear - the project is currently driven more by interest in technology than by a defined problem"),
        ],
    },
    "q0_success_metric": {
        "section": "problem_value",
        "title": "Is there a measurable success metric for this project?",
        "help": "Examples include reduced processing time, improved prediction accuracy, fewer manual errors, or higher completion rates.",
        "options": [
            ("defined", "Yes - a baseline and target measure are defined"),
            ("partial", "Partially - intended value is understood, but the baseline or target is not finalized"),
            ("none", "No - success has not yet been defined measurably"),
        ],
    },
    "q0_simpler_solution": {
        "section": "problem_value",
        "title": "Could a simpler solution reasonably address the problem before advanced AI is considered?",
        "help": "Examples include clearer procedures, dashboard reporting, deterministic business rules, form redesign, or workflow automation.",
        "options": [
            ("yes_process", "Yes - process clarification or manual improvement may be sufficient"),
            ("yes_analytics", "Yes - reporting, dashboards, or analytics may be sufficient"),
            ("possibly", "Possibly - simpler alternatives should be tested against more advanced options"),
            ("no", "No - the problem appears to require prediction, language understanding, or adaptive behavior"),
        ],
    },
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
    "q8a_decision_authority": {
        "section": "human_use",
        "title": "What role will the system have in the final decision or action?",
        "help": "Systems that advise or draft content create different risks than systems that independently approve, deny, route, or execute actions.",
        "options": [
            ("inform", "Inform - provide information or analysis for a human decision"),
            ("recommend", "Recommend - suggest an action that a human reviews"),
            ("draft", "Draft - generate content or classifications for human approval"),
            ("execute", "Execute - take action automatically within defined rules"),
            ("decide", "Decide - make consequential final decisions without routine human approval"),
        ],
    },
    "q8b_human_override": {
        "section": "human_use",
        "title": "Can an accountable human review, override, or correct the system output?",
        "help": "Meaningful human control is especially important for complex or high-impact systems.",
        "options": [
            ("always", "Yes - review and override are available when needed"),
            ("limited", "Partially - override exists only in limited cases"),
            ("no", "No - the system output will generally be final"),
        ],
    },
    "q8c_user_training": {
        "section": "human_use",
        "title": "Will users be trained on appropriate use, limitations, and error handling?",
        "help": "Training reduces misuse, overreliance, and incorrect interpretation of outputs.",
        "options": [
            ("planned", "Yes - training and usage guidance are planned"),
            ("informal", "Partially - informal guidance may be available"),
            ("none", "No - users are expected to adopt the tool without structured guidance"),
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
    "problem_value": {
        "title": "1. Problem Definition & Value",
        "intro": "Clarify the business problem, expected value, and whether a simpler solution should be tested first.",
    },
    "organizational_context": {
        "title": "2. Organizational Context",
        "intro": "Evaluate whether the organization and project context support advanced AI systems.",
    },
    "problem_structure": {
        "title": "3. Problem Structure",
        "intro": "Determine whether the problem requires probabilistic AI or could be solved with simpler automation.",
    },
    "output_requirements": {
        "title": "4. Output Requirements",
        "intro": "Output constraints strongly determine the appropriate automation approach.",
    },
    "human_use": {
        "title": "5. Human Use & Decision Authority",
        "intro": "Evaluate who will rely on the system and how much decision authority it should receive.",
    },
    "risk_governance": {
        "title": "6. Risk & Governance",
        "intro": "Evaluate operational risk, explainability, governance, and cost considerations.",
    },
}


QUESTION_ORDER = [
    "q0_problem_definition",
    "q0_success_metric",
    "q0_simpler_solution",
    "q1_ai_maturity",
    "q2_project_data_maturity",
    "q3_change_readiness",
    "q4_workflow_established",
    "q4b_workflow_mappable",
    "q5_input_type",
    "q6_output_boundaries",
    "q7_output_consistency",
    "q8a_decision_authority",
    "q8b_human_override",
    "q8c_user_training",
    "q8_risk_exposure",
    "q9_explainability",
    "q10_monitoring",
    "q11_cost_justification",
    "q12_build_model",
]


def section_questions(section_key: str, answers: Dict[str, Any]) -> List[str]:
    ordered = []
    for key in QUESTION_ORDER:
        if QUESTIONS[key]["section"] != section_key:
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


def delta(
    analytics: int = 0,
    automation: int = 0,
    ml: int = 0,
    llm: int = 0,
) -> ScoreDelta:
    return {
        ARCH_ANALYTICS: analytics,
        ARCH_AUTOMATION: automation,
        ARCH_ML: ml,
        ARCH_LLM: llm,
    }


SCORE_TABLES: Dict[str, Dict[str, ScoreDelta]] = {
    "q0_simpler_solution": {
        "yes_process": delta(),
        "yes_analytics": delta(analytics=4),
        "possibly": delta(analytics=1, automation=1),
        "no": delta(),
    },
    "q4_workflow_established": {
        "no": delta(),
        "undocumented": delta(analytics=1, automation=1),
        "mapped": delta(automation=3),
    },
    "q4b_workflow_mappable": {
        "yes": delta(automation=2),
        "partial": delta(automation=1, llm=1),
        "no": delta(llm=1),
    },
    "q5_input_type": {
        "structured": delta(analytics=2, automation=2, ml=1),
        "mixed": delta(analytics=1, automation=1, ml=1, llm=1),
        "unstructured": delta(llm=3),
    },
    "q6_output_boundaries": {
        "closed": delta(analytics=1, automation=3, ml=2),
        "bounded": delta(analytics=1, automation=1, ml=2, llm=1),
        "open": delta(llm=3),
    },
    "q7_output_consistency": {
        "identical": delta(analytics=1, automation=3, ml=1, llm=-4),
        "consistent": delta(analytics=1, automation=1, ml=2),
        "variation_ok": delta(llm=2),
    },
}


EXPLANATION_TEMPLATES: Dict[str, Dict[str, str]] = {
    "q0_problem_definition": {
        "clear": "The business problem and desired outcome are clearly documented, allowing architecture selection to proceed.",
        "partial": "The project goal is partly understood, but additional clarification may be needed before implementation.",
        "unclear": "The project is not yet grounded in a clearly defined business problem, so technology selection would be premature.",
    },
    "q0_success_metric": {
        "defined": "A measurable baseline and target outcome are defined, enabling meaningful pilot evaluation.",
        "partial": "Expected value is understood, but the measurement approach should be finalized before implementation.",
        "none": "No measurable success definition exists, so the organization cannot yet determine whether a technology improves outcomes.",
    },
    "q0_simpler_solution": {
        "yes_process": "A process or manual improvement may adequately address the problem before technology complexity is introduced.",
        "yes_analytics": "Traditional analytics or decision support may provide sufficient value without advanced AI.",
        "possibly": "Simpler alternatives should be tested as baselines before selecting a more complex architecture.",
        "no": "The use case appears to require capabilities beyond simple process or reporting improvements.",
    },
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
    "q8a_decision_authority": {
        "inform": "The system will inform human decisions rather than making them, limiting autonomy-related risk.",
        "recommend": "The system will recommend actions while preserving human decision authority.",
        "draft": "The system will generate draft outputs that require human approval.",
        "execute": "The system may execute actions automatically, increasing the need for controls and exception handling.",
        "decide": "The system may make final decisions, creating substantial accountability and governance requirements.",
    },
    "q8b_human_override": {
        "always": "Human review and override mechanisms are available, supporting meaningful control.",
        "limited": "Human override exists only in limited cases, requiring careful control design.",
        "no": "The absence of meaningful human override increases the risk of inappropriate automated decisions.",
    },
    "q8c_user_training": {
        "planned": "Structured user training supports appropriate reliance and error handling.",
        "informal": "Informal guidance may not adequately prevent misuse or overreliance.",
        "none": "Users may be unprepared to interpret limitations or identify erroneous outputs.",
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
    required_controls: List[str]
    prerequisite_actions: List[str]
    baseline_to_test: str
    tradeoffs: Dict[str, str]
    resources: List[str]
    phased_plan: List[str]
    why_not: Dict[str, List[str]]


TRADEOFFS = {
    ARCH_PROCESS: {
        "Build complexity": "Minimal",
        "Operational risk": "Low",
        "Maintenance burden": "Low",
        "Governance requirement": "Clarify ownership and measurement first",
    },
    ARCH_ANALYTICS: {
        "Build complexity": "Low",
        "Operational risk": "Low",
        "Maintenance burden": "Low-Medium",
        "Governance requirement": "Data quality and metric definitions",
    },
    ARCH_AUTOMATION: {
        "Build complexity": "Low-Medium",
        "Operational risk": "Low-Medium",
        "Maintenance burden": "Low-Medium",
        "Governance requirement": "Rules, exceptions, and audit logging",
    },
    ARCH_ML: {
        "Build complexity": "Medium",
        "Operational risk": "Medium",
        "Maintenance burden": "Medium",
        "Governance requirement": "Model evaluation, monitoring, and review",
    },
    ARCH_LLM: {
        "Build complexity": "Medium",
        "Operational risk": "Medium-High",
        "Maintenance burden": "Medium-High",
        "Governance requirement": "Prompt/output controls, monitoring, and human review",
    },
    ARCH_HYBRID: {
        "Build complexity": "Medium-High",
        "Operational risk": "Medium",
        "Maintenance burden": "Medium-High",
        "Governance requirement": "Layered validation, audit logs, and human oversight",
    },
    ARCH_NOT_READY: {
        "Build complexity": "Not advised yet",
        "Operational risk": "High if implemented prematurely",
        "Maintenance burden": "High relative to value",
        "Governance requirement": "Prerequisites must be completed first",
    },
}


def evaluate_answers(answers: Dict[str, Any]) -> EvaluationResult:
    scores = {arch: 0 for arch in FIT_ARCHITECTURES}
    key_drivers: List[str] = []
    exclusions: List[str] = []
    required_controls: List[str] = []
    prerequisite_actions: List[str] = []

    why_not = {
        ARCH_ANALYTICS: [],
        ARCH_AUTOMATION: [],
        ARCH_ML: [],
        ARCH_LLM: [],
    }

    for q_key, answer in answers.items():
        text = EXPLANATION_TEMPLATES.get(q_key, {}).get(answer)
        if text:
            key_drivers.append(text)

    problem_unclear = answers.get("q0_problem_definition") == "unclear"
    metric_missing = answers.get("q0_success_metric") == "none"
    process_first = answers.get("q0_simpler_solution") == "yes_process"

    if problem_unclear or metric_missing or process_first:
        if problem_unclear:
            prerequisite_actions.append(
                "Define the business problem, affected users, desired outcome, and decision owner before selecting technology."
            )
        if metric_missing:
            prerequisite_actions.append(
                "Establish a measurable baseline and target outcome before evaluating implementation options."
            )
        if process_first:
            prerequisite_actions.append(
                "Test process clarification or manual improvement before introducing automation or AI complexity."
            )

        return build_gated_result(
            recommendation_label=ARCH_PROCESS,
            scores=scores,
            answers=answers,
            key_drivers=key_drivers,
            exclusions=exclusions,
            required_controls=required_controls,
            prerequisite_actions=prerequisite_actions,
            baseline_to_test="Current manual process or clarified workflow baseline",
        )

    data_fragmented = answers.get("q2_project_data_maturity") == "fragmented"
    workflow_missing = answers.get("q4_workflow_established") == "no"
    readiness_low = answers.get("q3_change_readiness") == "low"

    if data_fragmented:
        prerequisite_actions.append(
            "Clean, consolidate, and document project data before relying on model-driven outputs."
        )

    if workflow_missing:
        prerequisite_actions.append(
            "Map the current process and clarify decision points before automating workflow execution."
        )

    if readiness_low:
        prerequisite_actions.append(
            "Assign ownership, training, governance, and monitoring responsibility before implementation."
        )

    if sum([data_fragmented, workflow_missing, readiness_low]) >= 2:
        return build_gated_result(
            recommendation_label=ARCH_NOT_READY,
            scores=scores,
            answers=answers,
            key_drivers=key_drivers,
            exclusions=exclusions,
            required_controls=required_controls,
            prerequisite_actions=prerequisite_actions,
            baseline_to_test="Reassess architecture after prerequisite work is completed",
        )

    for q_key, answer in answers.items():
        deltas = SCORE_TABLES.get(q_key, {}).get(answer)
        if deltas:
            for arch, value in deltas.items():
                scores[arch] += value

    risk_high = answers.get("q8_risk_exposure") == "high"
    deterministic_required = answers.get("q7_output_consistency") == "identical"
    decision_authority = answers.get("q8a_decision_authority")
    no_override = answers.get("q8b_human_override") == "no"
    explainability_required = answers.get("q9_explainability") == "required"
    unstructured_input = answers.get("q5_input_type") == "unstructured"
    mixed_input = answers.get("q5_input_type") == "mixed"

    if answers.get("q8b_human_override") in {"always", "limited"}:
        required_controls.append("Document human review and override procedures.")

    if answers.get("q8c_user_training") != "planned":
        required_controls.append("Create user training on appropriate use, limitations, and error handling.")

    if answers.get("q10_monitoring") in {"some", "continuous"}:
        required_controls.append("Define monitoring metrics, exception handling, and escalation ownership.")

    if explainability_required:
        required_controls.append("Maintain decision traces, audit logs, and documented explanation requirements.")

    if risk_high:
        required_controls.append("Require formal risk review before deployment.")

    llm_final_blocked = (
        risk_high
        and decision_authority in {"execute", "decide"}
    ) or (
        deterministic_required
        and decision_authority in {"execute", "decide"}
    ) or (
        no_override
        and decision_authority in {"execute", "decide"}
    )

    if llm_final_blocked:
        scores[ARCH_LLM] -= 6
        exclusions.append(
            "An LLM should not independently make or execute final consequential decisions under the selected control requirements."
        )
        why_not[ARCH_LLM].append(
            "The selected risk, determinism, or human-control conditions require a more controlled final decision path."
        )

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary_arch, primary_score = ranked[0]
    second_arch, second_score = ranked[1]

    hybrid_needed = False
    secondary = None

    if llm_final_blocked and (unstructured_input or mixed_input):
        primary_arch = (
            ARCH_AUTOMATION
            if scores[ARCH_AUTOMATION] >= scores[ARCH_ML]
            else ARCH_ML
        )
        secondary = ARCH_LLM
        hybrid_needed = True
        recommendation_label = f"{ARCH_HYBRID}: {ARCH_LLM} for interpretation + {primary_arch} for validated action"
        required_controls.append(
            "Limit generative output to extraction, drafting, or summarization before deterministic or human-approved action."
        )
    elif abs(primary_score - second_score) <= HYBRID_THRESHOLD:
        hybrid_needed = True
        secondary = second_arch
        recommendation_label = f"{ARCH_HYBRID}: {primary_arch} + {second_arch}"
    else:
        recommendation_label = primary_arch

    confidence = determine_confidence(primary_score, second_score, hybrid_needed)
    baseline_to_test = determine_baseline(primary_arch, secondary)

    for arch in FIT_ARCHITECTURES:
        if arch == primary_arch or arch == secondary:
            continue
        why_not[arch].append(
            f"{arch} was not the top fit based on the current balance of workflow structure, input type, and output requirements."
        )

    return EvaluationResult(
        scores=scores,
        primary=primary_arch,
        secondary=secondary,
        recommendation_label=recommendation_label,
        confidence=confidence,
        key_drivers=dedupe_preserve_order(key_drivers)[:8],
        exclusions=dedupe_preserve_order(exclusions),
        required_controls=dedupe_preserve_order(required_controls),
        prerequisite_actions=dedupe_preserve_order(prerequisite_actions),
        baseline_to_test=baseline_to_test,
        tradeoffs=TRADEOFFS[ARCH_HYBRID if hybrid_needed else primary_arch],
        resources=determine_resources(answers, recommendation_label),
        phased_plan=determine_phased_plan(answers, recommendation_label),
        why_not=why_not,
    )


def determine_confidence(primary_score: int, second_score: int, hybrid_needed: bool) -> str:
    gap = primary_score - second_score
    if hybrid_needed:
        return "Medium"
    if gap >= 4:
        return "High"
    if gap >= 2:
        return "Medium"
    return "Low"


def determine_baseline(primary: str, secondary: Optional[str]) -> str:
    if primary == ARCH_ANALYTICS:
        return "Compare against the current reporting or manual decision process."
    if primary == ARCH_AUTOMATION:
        return "Compare deterministic workflow performance against the current manual process."
    if primary == ARCH_ML:
        return "Compare model performance against rules-based or descriptive analytics baselines."
    if primary == ARCH_LLM:
        return "Compare the LLM-assisted workflow against a structured template or deterministic alternative."
    if secondary:
        return "Compare the hybrid design against its simpler single-component alternative."
    return "Define a measurable non-AI baseline before pilot testing."


def build_gated_result(
    recommendation_label: str,
    scores: Dict[str, int],
    answers: Dict[str, Any],
    key_drivers: List[str],
    exclusions: List[str],
    required_controls: List[str],
    prerequisite_actions: List[str],
    baseline_to_test: str,
) -> EvaluationResult:
    return EvaluationResult(
        scores=scores,
        primary=recommendation_label,
        secondary=None,
        recommendation_label=recommendation_label,
        confidence="High",
        key_drivers=dedupe_preserve_order(key_drivers)[:8],
        exclusions=dedupe_preserve_order(exclusions),
        required_controls=dedupe_preserve_order(required_controls),
        prerequisite_actions=dedupe_preserve_order(prerequisite_actions),
        baseline_to_test=baseline_to_test,
        tradeoffs=TRADEOFFS[recommendation_label],
        resources=determine_resources(answers, recommendation_label),
        phased_plan=determine_phased_plan(answers, recommendation_label),
        why_not={
            ARCH_ANALYTICS: [],
            ARCH_AUTOMATION: [],
            ARCH_ML: [],
            ARCH_LLM: [],
        },
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
    if recommendation_label == ARCH_PROCESS:
        return [
            "Phase 0 - Clarify the problem, decision owner, current workflow, and measurable baseline.",
            "Phase 1 - Test whether process or manual improvements resolve the primary issue.",
            "Phase 2 - Reassess whether analytics, automation, or AI is still needed.",
        ]

    if recommendation_label == ARCH_NOT_READY:
        return [
            "Phase 0 - Address workflow, data, ownership, training, and governance prerequisites.",
            "Phase 1 - Establish a measurable baseline and confirm implementation readiness.",
            "Phase 2 - Reassess the simplest viable architecture before piloting.",
        ]

    if recommendation_label == ARCH_ANALYTICS:
        return [
            "Phase 1 - Build a decision-support baseline using trusted metrics, reporting, or dashboards.",
            "Phase 2 - Measure whether analytics alone adequately improves decisions or workflow performance.",
            "Phase 3 - Consider automation or AI only if documented gaps remain.",
        ]

    phases = []

    if answers.get("q2_project_data_maturity") in {"fragmented", "transform"}:
        phases.append(
            "Phase 0 - Complete data preparation, documentation, and quality validation."
        )

    phases.extend([
        "Phase 1 - Build a constrained MVP with defined success metrics, audit logging, and exception handling.",
        "Phase 2 - Pilot against a simpler comparison baseline and evaluate quality, cost, user reliance, and operational burden.",
        "Phase 3 - Scale only after governance controls and measurable benefits are demonstrated.",
    ])

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
            html.Tr([
                html.Td(question["title"]),
                html.Td(label),
                html.Td(
                    dbc.Button(
                        "Edit",
                        id={"type": "edit-answer", "question": q_key},
                        color="primary",
                        outline=True,
                        size="sm",
                    ),
                    style={"textAlign": "right"},
                ),
            ])
        )

    return dbc.Container(
        [
            html.H2("Review Your Inputs", className="mt-4"),
            html.P("Confirm your answers before generating the recommendation."),
            dbc.Table(
                [
                    html.Thead(html.Tr([html.Th("Question"), html.Th("Selected Answer"), html.Th("")])),
                    html.Tbody(rows),
                ],
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
    for arch in FIT_ARCHITECTURES:
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
                                html.H4("Candidate Architecture Fit"),
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
                                html.H4("Required Controls"),
                                html.Ul([html.Li(x) for x in result.required_controls])
                                if result.required_controls
                                else html.P("No additional controls were triggered beyond standard project governance."),
                            ])
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Prerequisites & Baseline"),
                                html.Ul([html.Li(x) for x in result.prerequisite_actions])
                                if result.prerequisite_actions
                                else html.P("No blocking prerequisite actions were triggered."),
                                html.Hr(),
                                html.Div("Recommended comparison baseline", className="fw-bold"),
                                html.P(result.baseline_to_test),
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


def question_card(q_key: str, answers: Dict[str, Any], current_index: int, total_questions: int, edit_mode: bool = False) -> dbc.Container:
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
                    dbc.Col(dbc.Button("Save" if edit_mode else "Next", id="btn-next", color="primary"), style={"textAlign": "right"}),
                ],
                className="mt-4",
            ),
        ],
        style={"maxWidth": "920px"},
    )


# =========================================================
# Dash app
# =========================================================

app: Dash = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = APP_TITLE
server = app.server

app.layout = html.Div(
    [
        dcc.Store(id="store-answers", data={}),
        dcc.Store(id="store-current-answer", data=None),
        dcc.Store(id="store-page", data={"mode": "welcome", "question_idx": 0}),
        html.Div(id="page-content"),
    ]
)


@app.callback(
    Output("store-current-answer", "data"),
    Input("current-answer", "value", allow_optional=True),
    prevent_initial_call=True,
)
def store_current_answer(current_answer):
    return current_answer


@app.callback(
    Output("store-page", "data"),
    Output("store-answers", "data"),
    Input("btn-start", "n_clicks", allow_optional=True),
    Input("btn-next", "n_clicks", allow_optional=True),
    Input("btn-back", "n_clicks", allow_optional=True),
    Input("btn-submit", "n_clicks", allow_optional=True),
    Input("btn-restart", "n_clicks", allow_optional=True),
    Input({"type": "edit-answer", "question": ALL}, "n_clicks", allow_optional=True),
    State("store-page", "data"),
    State("store-answers", "data"),
    State("store-current-answer", "data"),
    prevent_initial_call=True,
)
def handle_navigation(start, next_clicks, back_clicks, submit_clicks, restart_clicks, edit_clicks, page_state, answers, current_answer):
    answers = answers or {}
    page_state = page_state or {"mode": "welcome", "question_idx": 0}

    triggered_raw = callback_context.triggered[0]["prop_id"].split(".")[0] if callback_context.triggered else None
    try:
        triggered = json.loads(triggered_raw) if triggered_raw and triggered_raw.startswith("{") else triggered_raw
    except json.JSONDecodeError:
        triggered = triggered_raw

    visible_qs = all_visible_questions(answers)
    mode = page_state.get("mode", "welcome")
    idx = page_state.get("question_idx", 0)

    if isinstance(triggered, dict) and triggered.get("type") == "edit-answer":
        question_key = triggered.get("question")
        if question_key in visible_qs:
            return {"mode": "question", "question_idx": visible_qs.index(question_key), "return_to_review": True}, answers
        return no_update, answers

    if triggered == "btn-restart":
        return {"mode": "welcome", "question_idx": 0}, {}

    if triggered == "btn-start":
        return {"mode": "question", "question_idx": 0, "return_to_review": False}, answers

    if mode == "question" and visible_qs and 0 <= idx < len(visible_qs):
        q_key = visible_qs[idx]
        answer_to_save = current_answer if current_answer is not None else answers.get(q_key)
        if answer_to_save is not None:
            answers = {**answers, q_key: answer_to_save}
            visible_qs = all_visible_questions(answers)

    if triggered == "btn-next":
        if mode == "question":
            if page_state.get("return_to_review"):
                return {"mode": "review", "question_idx": idx, "return_to_review": False}, answers
            if idx + 1 < len(visible_qs):
                return {"mode": "question", "question_idx": idx + 1, "return_to_review": False}, answers
            return {"mode": "review", "question_idx": idx, "return_to_review": False}, answers
        return no_update, answers

    if triggered == "btn-back":
        if mode == "results":
            return {"mode": "review", "question_idx": max(len(visible_qs) - 1, 0)}, answers
        if mode == "review":
            return {"mode": "question", "question_idx": max(len(visible_qs) - 1, 0), "return_to_review": False}, answers
        if mode == "question":
            if page_state.get("return_to_review"):
                return {"mode": "review", "question_idx": idx, "return_to_review": False}, answers
            if idx > 0:
                return {"mode": "question", "question_idx": idx - 1, "return_to_review": False}, answers
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
    return question_card(q_key, answers, idx + 1, len(visible_qs), bool(page_state.get("return_to_review")))


if __name__ == "__main__":
    app.run(debug=False)
