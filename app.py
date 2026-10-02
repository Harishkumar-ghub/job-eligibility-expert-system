import streamlit as st

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="Job Eligibility Expert System",
    page_icon="💼",
    layout="centered"
)

# ---------- KNOWLEDGE BASE ----------

# Qualification hierarchy on an integer scale (1 to 4).
# Higher levels automatically satisfy lower minimum level requirements.
QUAL_LEVELS = {
    "10th": 1,
    "12th": 2,
    "B.Com": 3, "BA": 3, "B.Sc": 3, "BCA": 3, "B.Tech": 3, "B.Ed": 3,
    "M.Com": 4, "MA": 4, "M.Sc": 4, "MCA": 4, "M.Tech": 4, "MBA": 4
}
QUALS = list(QUAL_LEVELS.keys())

# Skills relevant to each qualification (shown after the user picks one)
GENERAL_SKILLS = ["Communication", "Typing", "Maths"]
TECH_SKILLS = ["Python", "SQL", "Excel", "Networking", "Design"]
COMMERCE_SKILLS = ["Accounting", "Excel"]

QUAL_SKILLS = {
    "10th": GENERAL_SKILLS,
    "12th": GENERAL_SKILLS,
    "BA": GENERAL_SKILLS, "MA": GENERAL_SKILLS, "B.Ed": GENERAL_SKILLS,
    "B.Com": GENERAL_SKILLS + COMMERCE_SKILLS,
    "M.Com": GENERAL_SKILLS + COMMERCE_SKILLS,
    "B.Sc": GENERAL_SKILLS + TECH_SKILLS,
    "M.Sc": GENERAL_SKILLS + TECH_SKILLS,
    "BCA": GENERAL_SKILLS + TECH_SKILLS,
    "MCA": GENERAL_SKILLS + TECH_SKILLS,
    "B.Tech": GENERAL_SKILLS + TECH_SKILLS,
    "M.Tech": GENERAL_SKILLS + TECH_SKILLS,
    "MBA": GENERAL_SKILLS + ["Excel", "Accounting", "SQL", "Python"],
}

# Number of rule checks per job: qualification, marks, age, experience, skills
TOTAL_CHECKS = 5

# Job criteria
# allowed_quals = None means any degree at or above min_qual_level is accepted
JOBS = {
    "Software Developer": {
        "min_qual_level": 3, "allowed_quals": ["B.Tech", "BCA", "MCA", "M.Tech"],
        "min_marks": 60, "min_age": 20, "max_age": 35, "min_exp": 0,
        "skills": ["Python"]
    },
    "Bank PO": {
        "min_qual_level": 3, "allowed_quals": None,
        "min_marks": 50, "min_age": 20, "max_age": 30, "min_exp": 0,
        "skills": ["Maths", "Communication"]
    },
    "Government Clerk": {
        "min_qual_level": 2, "allowed_quals": None,
        "min_marks": 50, "min_age": 18, "max_age": 27, "min_exp": 0,
        "skills": ["Typing", "Communication"]
    },
    "Teacher": {
        "min_qual_level": 3, "allowed_quals": ["B.Ed", "BA", "B.Sc", "MA", "M.Sc", "MCA"],
        "min_marks": 55, "min_age": 21, "max_age": 40, "min_exp": 1,
        "skills": ["Communication"]
    },
    "Data Analyst": {
        "min_qual_level": 3, "allowed_quals": ["B.Tech", "BCA", "B.Sc", "MCA", "M.Sc", "MBA", "M.Tech"],
        "min_marks": 60, "min_age": 20, "max_age": 35, "min_exp": 1,
        "skills": ["Python", "SQL", "Excel"]
    },
    "Web Designer": {
        "min_qual_level": 3, "allowed_quals": ["BCA", "B.Tech", "B.Sc", "MCA"],
        "min_marks": 50, "min_age": 18, "max_age": 35, "min_exp": 0,
        "skills": ["Design"]
    },
    "Network Engineer": {
        "min_qual_level": 3, "allowed_quals": ["B.Tech", "BCA", "B.Sc", "MCA", "M.Tech"],
        "min_marks": 55, "min_age": 20, "max_age": 35, "min_exp": 1,
        "skills": ["Networking"]
    },
    "Accountant": {
        "min_qual_level": 3, "allowed_quals": ["B.Com", "M.Com", "MBA"],
        "min_marks": 50, "min_age": 20, "max_age": 40, "min_exp": 0,
        "skills": ["Accounting", "Excel"]
    },
    "Data Entry Operator": {
        "min_qual_level": 2, "allowed_quals": None,
        "min_marks": 40, "min_age": 18, "max_age": 35, "min_exp": 0,
        "skills": ["Typing"]
    },
    "Sales Executive": {
        "min_qual_level": 2, "allowed_quals": None,
        "min_marks": 40, "min_age": 18, "max_age": 35, "min_exp": 0,
        "skills": ["Communication"]
    },
}


# ---------- INFERENCE ENGINE ----------

def check_qualification(cand_qual, rules):
    """Checks education level (rank) and, if required, the specific degree."""
    cand_level = QUAL_LEVELS.get(cand_qual, 0)

    # IF candidate level < minimum level THEN fail
    if cand_level < rules["min_qual_level"]:
        return False

    # IF specific degrees are required AND candidate's degree is not listed THEN fail
    allowed = rules.get("allowed_quals")
    if allowed is not None and cand_qual not in allowed:
        return False

    return True


def check_job(rules, qual, marks, age, exp, user_skills):
    """Applies all rules to one job. Returns (failure reasons, checks passed)."""
    reasons = []

    # Rule 1: Qualification
    if not check_qualification(qual, rules):
        if rules["allowed_quals"]:
            reasons.append(f"Qualification '{qual}' does not match required stream(s): {', '.join(rules['allowed_quals'])}")
        else:
            reasons.append(f"Qualification level too low (requires level {rules['min_qual_level']}+)")

    # Rule 2: Marks
    if marks < rules["min_marks"]:
        reasons.append(f"Marks ({marks}%) below required ({rules['min_marks']}%)")

    # Rule 3: Age range
    if age < rules["min_age"]:
        reasons.append(f"Age ({age}) below minimum ({rules['min_age']})")
    elif age > rules["max_age"]:
        reasons.append(f"Age ({age}) above maximum ({rules['max_age']})")

    # Rule 4: Experience
    if exp < rules["min_exp"]:
        reasons.append(f"Experience ({exp} yr) below required ({rules['min_exp']} yr)")

    # Rule 5: Skills. IF a required skill is missing THEN fail
    missing = [s for s in rules["skills"] if s not in user_skills]
    if missing:
        reasons.append(f"Missing skill(s): {', '.join(missing)}")

    passed = TOTAL_CHECKS - len(reasons)
    return reasons, passed


def infer(qual, marks, age, exp, user_skills):
    """Runs every job through the rules. Returns eligible and not-eligible lists."""
    eligible, not_eligible = [], []

    for job, rules in JOBS.items():
        reasons, passed = check_job(rules, qual, marks, age, exp, user_skills)
        if reasons:
            not_eligible.append((job, reasons, passed))
        else:
            eligible.append(job)

    # Show the closest matches first
    not_eligible.sort(key=lambda x: x[2], reverse=True)
    return eligible, not_eligible


# ---------- USER INTERFACE ----------

st.title("💼 Job Eligibility Expert System")
st.caption("Rule-Based Inference Engine: Qualification, Marks, Age, Experience, Skills")

# Starts empty so the user must choose a qualification first
qual = st.selectbox(
    "Highest Qualification", QUALS,
    index=None, placeholder="Select your qualification"
)
marks = st.slider("Marks / Percentage (%)", min_value=0, max_value=100, value=60)
age = st.number_input("Age (Years)", min_value=15, max_value=70, value=22)
exp = st.number_input("Experience (Years)", min_value=0, max_value=40, value=0)

# Skills appear only after a qualification is selected, and only relevant ones
user_skills = []
if qual is None:
    st.info("Select your highest qualification to unlock the skills section.")
else:
    user_skills = st.pills(
        f"Skills relevant to {qual}", QUAL_SKILLS[qual], selection_mode="multi"
    ) or []

st.divider()

# Button stays disabled until a qualification is chosen
if st.button("Evaluate Eligibility", type="primary", use_container_width=True, disabled=(qual is None)):
    eligible, not_eligible = infer(qual, marks, age, exp, user_skills)

    st.subheader("✅ Eligible Positions")
    if eligible:
        for job in eligible:
            st.success(f"**{job}**: meets all {TOTAL_CHECKS} criteria.")
    else:
        st.warning("No job matches all criteria. See the closest matches below.")

    if not_eligible:
        st.subheader("❌ Ineligible Positions")
        for job, reasons, passed in not_eligible:
            with st.expander(f"{job}: met {passed} of {TOTAL_CHECKS} criteria"):
                st.progress(passed / TOTAL_CHECKS)
                for r in reasons:
                    st.write(f"- {r}")

with st.expander("🔍 View Knowledge Base Criteria"):
    for job, r in JOBS.items():
        allowed = ", ".join(r["allowed_quals"]) if r["allowed_quals"] else "Any stream"
        st.markdown(
            f"**{job}**  \n"
            f"• Level: {r['min_qual_level']}+ | Allowed: {allowed}  \n"
            f"• Marks: ≥ {r['min_marks']}% | Age: {r['min_age']}–{r['max_age']} | Min Exp: {r['min_exp']} yr  \n"
            f"• Skills: {', '.join(r['skills'])}"
        )