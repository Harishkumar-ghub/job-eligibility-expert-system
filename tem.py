import streamlit as st

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="Job Eligibility Expert System", 
    page_icon="💼",
    layout="centered"
)

# ---------- KNOWLEDGE BASE ----------

# 1. Qualification hierarchy defined on an integer scale (1 to 4).
# Candidates with higher levels automatically satisfy lower minimum rank requirements.
QUAL_LEVELS = {
    "10th": 1,
    "12th": 2,
    "B.Com": 3, "BA": 3, "B.Sc": 3, "BCA": 3, "B.Tech": 3, "B.Ed": 3,
    "M.Com": 4, "MA": 4, "M.Sc": 4, "MCA": 4, "M.Tech": 4, "MBA": 4
}

# Ordered list for UI selection dropdown
QUALS = list(QUAL_LEVELS.keys())

# 2. Job criteria updated with:
# - min_qual_level: Minimum rank required on integer scale
# - allowed_quals: Specific streams accepted (None means any qualification at or above min_qual_level is accepted)
JOBS = {
    "Software Developer": {
        "min_qual_level": 3,
        "allowed_quals": ["B.Tech", "BCA", "MCA", "M.Tech"],
        "min_marks": 60,
        "min_age": 20,
        "max_age": 35,
        "min_exp": 0
    },
    "Bank PO": {
        "min_qual_level": 3,  # Accepts any Bachelor's or Master's
        "allowed_quals": None,
        "min_marks": 50,
        "min_age": 20,
        "max_age": 30,
        "min_exp": 0
    },
    "Government Clerk": {
        "min_qual_level": 2,  # Accepts 12th standard or higher
        "allowed_quals": None,
        "min_marks": 50,
        "min_age": 18,
        "max_age": 27,
        "min_exp": 0
    },
    "Teacher": {
        "min_qual_level": 3,
        "allowed_quals": ["B.Ed", "BA", "B.Sc", "MA", "M.Sc", "MCA"],
        "min_marks": 55,
        "min_age": 21,
        "max_age": 40,
        "min_exp": 1
    },
    "Data Analyst": {
        "min_qual_level": 3,
        "allowed_quals": ["B.Tech", "BCA", "B.Sc", "MCA", "M.Sc", "MBA", "M.Tech"],
        "min_marks": 60,
        "min_age": 20,
        "max_age": 35,
        "min_exp": 1
    },
}


# ---------- INFERENCE ENGINE ----------

def check_qualification(cand_qual: str, rules: dict) -> bool:
    """
    Checks candidate's qualification against job criteria:
    1. Compares integer scale ranks (cand_level vs. min_qual_level).
    2. Checks stream requirement if specific degrees are enforced.
    """
    cand_level = QUAL_LEVELS.get(cand_qual, 0)
    min_level = rules["min_qual_level"]
    
    # Check 1: Must meet or exceed minimum education level
    if cand_level < min_level:
        return False
        
    # Check 2: If specific streams are required, candidate's degree must be in the list
    allowed = rules.get("allowed_quals")
    if allowed is not None and cand_qual not in allowed:
        return False
        
    return True


def check_job(rules: dict, qual: str, marks: float, age: int, exp: int) -> list:
    """Evaluates a candidate profile against job rules and returns failure reasons."""
    reasons = []

    # Qualification validation
    if not check_qualification(qual, rules):
        if rules["allowed_quals"]:
            req_str = ", ".join(rules["allowed_quals"])
            reasons.append(f"Qualification '{qual}' does not match required stream(s): {req_str}")
        else:
            reasons.append(f"Qualification level too low (requires level {rules['min_qual_level']}+)")

    # Marks validation
    if marks < rules["min_marks"]:
        reasons.append(f"Marks ({marks}%) below required threshold ({rules['min_marks']}%)")

    # Age boundary validation
    if age < rules["min_age"]:
        reasons.append(f"Age ({age} yrs) below minimum requirement ({rules['min_age']} yrs)")
    elif age > rules["max_age"]:
        reasons.append(f"Age ({age} yrs) exceeds maximum limit ({rules['max_age']} yrs)")

    # Experience validation
    if exp < rules["min_exp"]:
        reasons.append(f"Experience ({exp} yr) below required ({rules['min_exp']} yr)")

    return reasons


def infer(qual: str, marks: float, age: int, exp: int):
    """Iterates through knowledge base to determine eligibility."""
    eligible, not_eligible = [], []
    
    for job, rules in JOBS.items():
        reasons = check_job(rules, qual, marks, age, exp)
        if reasons:
            not_eligible.append((job, reasons))
        else:
            eligible.append(job)
            
    return eligible, not_eligible


# ---------- USER INTERFACE ----------

st.title("💼 Job Eligibility Expert System")
st.caption("Rule-Based Inference Engine (Hierarchical Qualification Matching)")

# Candidate Input Section
with st.container(): 
        
    qual = st.selectbox("Highest Qualification", QUALS, index=2)
    marks = st.slider("Marks / Percentage (%)", min_value=0, max_value=100, value=60)
    
    age = st.number_input("Age (Years)", min_value=15, max_value=70, value=22)
    exp = st.number_input("Experience (Years)", min_value=0, max_value=40, value=0)

st.divider()

# Evaluation & Output Section
if st.button("Evaluate Eligibility", type="primary", use_container_width=True):
    eligible, not_eligible = infer(qual, marks, age, exp)

    # Render Eligible Roles
    st.subheader("✅ Eligible Positions")
    if eligible:
        for job in eligible:
            st.success(f"**{job}** — Meets all qualification standards.")
    else:
        st.warning("No matching job profiles found based on your input criteria.")

    # Render Ineligible Roles with Reason Breakdown
    if not_eligible:
        st.subheader("❌ Ineligible Positions")
        for job, reasons in not_eligible:
            with st.expander(f"**{job}**", expanded=True):
                for r in reasons:
                    st.write(f"- {r}")

# Knowledge Base Reference Accordion
with st.expander("🔍 View Knowledge Base Criteria"):
    for job, r in JOBS.items():
        allowed = ", ".join(r["allowed_quals"]) if r["allowed_quals"] else "Any stream"
        st.markdown(
            f"**{job}**  \n"
            f"• Min Level: Rank {r['min_qual_level']} | Allowed: {allowed}  \n"
            f"• Marks: ≥ {r['min_marks']}% | Age: {r['min_age']}–{r['max_age']} yrs | Min Exp: {r['min_exp']} yr"
        )