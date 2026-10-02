import streamlit as st

st.set_page_config(page_title="Job Eligibility Expert System", page_icon="💼")

# ---------- KNOWLEDGE BASE (job criteria) ----------
JOBS = {
    "Software Developer": {"quals": ["B.Tech", "BCA", "MCA", "M.Tech"], "min_marks": 60, "min_age": 20, "max_age": 35, "min_exp": 0},
    "Bank PO":            {"quals": ["B.Tech", "BCA", "B.Com", "BA", "B.Sc", "MBA", "MCA"], "min_marks": 50, "min_age": 20, "max_age": 30, "min_exp": 0},
    "Government Clerk":   {"quals": ["12th", "B.Tech", "BCA", "B.Com", "BA", "B.Sc"], "min_marks": 50, "min_age": 18, "max_age": 27, "min_exp": 0},
    "Teacher":            {"quals": ["B.Ed", "MA", "M.Sc", "MBA", "MCA"], "min_marks": 55, "min_age": 21, "max_age": 40, "min_exp": 1},
    "Data Analyst":       {"quals": ["B.Tech", "BCA", "B.Sc", "MCA", "M.Sc", "MBA"], "min_marks": 60, "min_age": 20, "max_age": 35, "min_exp": 1},
}

QUALS = ["10th", "12th", "B.Tech", "BCA", "B.Com", "BA", "B.Sc", "B.Ed", "MA", "M.Sc", "MBA", "MCA", "M.Tech"]

# ---------- INFERENCE ENGINE ----------
def check_job(job, rules, qual, marks, age, exp):
    reasons = []
    # IF qualification not accepted THEN not eligible
    if qual not in rules["quals"]:
        reasons.append(f"Qualification {qual} not accepted (needs: {', '.join(rules['quals'])})")
    # IF marks < minimum THEN not eligible
    if marks < rules["min_marks"]:
        reasons.append(f"Marks {marks}% below required {rules['min_marks']}%")
    # IF age outside range THEN not eligible
    if age < rules["min_age"]:
        reasons.append(f"Age {age} below minimum {rules['min_age']}")
    elif age > rules["max_age"]:
        reasons.append(f"Age {age} above maximum {rules['max_age']}")
    # IF experience < minimum THEN not eligible
    if exp < rules["min_exp"]:
        reasons.append(f"Experience {exp} yr(s) below required {rules['min_exp']} yr(s)")
    return reasons

def infer(qual, marks, age, exp):
    eligible, not_eligible = [], []
    for job, rules in JOBS.items():
        reasons = check_job(job, rules, qual, marks, age, exp)
        if reasons:
            not_eligible.append((job, reasons))
        else:
            eligible.append(job)
    return eligible, not_eligible

# ---------- UI ----------
st.title("💼 Job Eligibility Expert System")
st.caption("User Input → IF-THEN Rules → Inference → Eligibility Result")

qual = st.selectbox("Highest Qualification", QUALS, index=2)
marks = st.slider("Marks / Percentage (%)", 0, 100, 60)
age = st.number_input("Age", min_value=15, max_value=70, value=22)
exp = st.number_input("Experience (years)", min_value=0, max_value=40, value=0)

if st.button("Check Eligibility"):
    eligible, not_eligible = infer(qual, marks, age, exp)

    st.subheader("✅ Eligible For")
    if eligible:
        for job in eligible:
            st.success(job)
    else:
        st.warning("Not eligible for any job in the knowledge base.")

    st.subheader("❌ Not Eligible For")
    for job, reasons in not_eligible:
        st.error(job)
        for r in reasons:
            st.caption(f"• {r}")

with st.expander("View Knowledge Base (rules)"):
    for job, r in JOBS.items():
        st.write(f"**{job}**: {', '.join(r['quals'])} | min {r['min_marks']}% | age {r['min_age']}-{r['max_age']} | min exp {r['min_exp']} yr")