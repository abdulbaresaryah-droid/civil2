import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - ACI / ECP",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        margin-top: -2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.3rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 5px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.1rem; }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    div[data-testid="column"] { padding: 2px 5px !important; }
    .element-container { margin-bottom: 0px !important; }
    .katex { font-size: 0.95em; }
    </style>
""", unsafe_allow_html=True)

# Rebar data table (areas in mm^2)
rebar_data = {
    6: [28.3, 57, 85, 113, 142, 170, 198, 226, 255],
    8: [50.3, 101, 151, 201, 252, 302, 352, 402, 453],
    10: [78.5, 157, 236, 314, 393, 471, 550, 628, 707],
    12: [113.1, 226, 339, 452, 565, 678, 791, 904, 1017],
    14: [153.9, 308, 461, 615, 769, 923, 1077, 1231, 1385],
    16: [201.1, 402, 603, 804, 1005, 1206, 1407, 1608, 1809],
    18: [254.5, 509, 763, 1017, 1272, 1527, 1781, 2036, 2290],
    20: [314.2, 628, 942, 1256, 1570, 1884, 2199, 2513, 2827],
    22: [380.1, 760, 1140, 1520, 1900, 2281, 2661, 3041, 3421],
    25: [490.9, 982, 1473, 1964, 2454, 2945, 3436, 3927, 4418],
    28: [615.8, 1232, 1847, 2463, 3079, 3695, 4310, 4926, 5542],
    32: [804.2, 1609, 2413, 3217, 4021, 4826, 5630, 6434, 7238],
    36: [1017.9, 2036, 3054, 4072, 5089, 6107, 7125, 8143, 9161],
    40: [1256.6, 2513, 3770, 5027, 6283, 7540, 8796, 10053, 11310],
    50: [1963.5, 3928, 5892, 7856, 9820, 11784, 13748, 15712, 17676]
}


# -----------------------------
# Synced input (number + slider)
# -----------------------------
def _init_synced(key: str, default: float):
    if key not in st.session_state:
        st.session_state[key] = default
    num_key = f"{key}__num"
    sld_key = f"{key}__sld"
    if num_key not in st.session_state:
        st.session_state[num_key] = st.session_state[key]
    if sld_key not in st.session_state:
        st.session_state[sld_key] = st.session_state[key]


def _sync_from_num(key: str):
    num_key = f"{key}__num"
    sld_key = f"{key}__sld"
    v = st.session_state.get(num_key, 0.0)
    st.session_state[key] = v
    st.session_state[sld_key] = v  # force slider to match


def _sync_from_sld(key: str):
    num_key = f"{key}__num"
    sld_key = f"{key}__sld"
    v = st.session_state.get(sld_key, 0.0)
    st.session_state[key] = v
    st.session_state[num_key] = v  # force number to match


def synced_control(
    label: str,
    key: str,
    min_value: float,
    max_value: float,
    step: float,
    default: float,
    unit: str = "",
    help_text: str | None = None,
):
    _init_synced(key, default)

    st.sidebar.markdown(f"**{label}** {unit}".rstrip())

    c1, c2 = st.sidebar.columns([1, 1])
    with c1:
        st.number_input(
            "number",
            min_value=min_value,
            max_value=max_value,
            step=step,
            key=f"{key}__num",
            label_visibility="collapsed",
            help=help_text,
            on_change=_sync_from_num,
            args=(key,),
        )
    with c2:
        st.slider(
            "slider",
            min_value=min_value,
            max_value=max_value,
            step=step,
            key=f"{key}__sld",
            label_visibility="collapsed",
            help=help_text,
            on_change=_sync_from_sld,
            args=(key,),
        )

    return st.session_state[key]


# Initialize session state once
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    # defaults (can be 0.0 if you prefer forcing user input)
    st.session_state.fy = 420.0
    st.session_state.fcu = 25.0
    st.session_state.Mu = 100.0
    st.session_state.b = 250.0
    st.session_state.h = 500.0
    st.session_state.cover = 40.0
    st.session_state.phi = 0.90
    st.session_state.jd = 0.90
    st.session_state.beta1 = 0.85


def _set_synced_value(key: str, value: float):
    st.session_state[key] = value
    st.session_state[f"{key}__num"] = value
    st.session_state[f"{key}__sld"] = value


def clear_all_inputs():
    for k in ["fy", "fcu", "Mu", "b", "h", "cover", "phi", "jd", "beta1"]:
        _set_synced_value(k, 0.0)
    st.rerun()


# Title
st.markdown('<h1 class="main-header">🏗️ RC Section Design (ACI / ECP)</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Input Parameters")

design_code = st.sidebar.radio("Design Code", ["ACI 318", "Egyptian Code (C1/J method)"])
st.sidebar.markdown("---")

if st.sidebar.button("🗑️ Clear All Inputs", type="secondary", use_container_width=True):
    clear_all_inputs()

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")

fy = synced_control("Steel Yield Strength, fy", "fy", 0.0, 600.0, 10.0, st.session_state.fy, "(MPa)")
fcu = synced_control("Concrete Strength, f'c / fcu", "fcu", 0.0, 60.0, 2.5, st.session_state.fcu, "(MPa)")

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")
Mu = synced_control("Ultimate Moment, Mu", "Mu", 0.0, 500.0, 0.5, st.session_state.Mu, "(kN.m)")

st.sidebar.markdown("---")
st.sidebar.subheader("Section Dimensions")
b = synced_control("Width, b", "b", 0.0, 2000.0, 50.0, st.session_state.b, "(mm)")
h = synced_control("Height, h", "h", 0.0, 1500.0, 10.0, st.session_state.h, "(mm)")
cover = synced_control("Cover", "cover", 0.0, 100.0, 5.0, st.session_state.cover, "(mm)")

st.sidebar.markdown("---")
st.sidebar.subheader("Design Parameters")

if design_code == "ACI 318":
    phi = synced_control("Strength Reduction Factor, φ", "phi", 0.0, 0.9, 0.05, st.session_state.phi)
    jd = synced_control("Moment Arm Factor, jd", "jd", 0.0, 0.95, 0.01, st.session_state.jd)
    beta1 = synced_control("β₁ Factor", "beta1", 0.0, 0.85, 0.05, st.session_state.beta1)
else:
    st.sidebar.info("ECP constants (editable)")
    with st.sidebar.expander("ECP Constants", expanded=False):
        C1_min = st.number_input("C1 min", min_value=0.0, value=2.76, step=0.01)
        J_max = st.number_input("J max", min_value=0.0, max_value=1.0, value=0.95, step=0.01)
        k1 = st.number_input("k1 (in 1/k1)", min_value=0.01, value=1.15, step=0.01)
        k2 = st.number_input("k2 (in 1/(k2*C1^2))", min_value=0.01, value=0.9, step=0.01)
else_C1_min = 2.76
else_J_max = 0.95
else_k1 = 1.15
else_k2 = 0.9

# Validation
if not (fy > 0 and fcu > 0 and Mu > 0 and b > 0 and h > 0 and cover >= 0 and h > cover):
    st.warning("⚠️ Please enter all input values to proceed with calculations")
    st.info("💡 Make sure: h > cover")
    st.stop()

if design_code == "ACI 318":
    if not (phi > 0 and jd > 0 and beta1 > 0):
        st.warning("⚠️ Please enter all design parameters (φ, jd, β₁)")
        st.stop()

# Calculations
try:
    d = h - cover
    if d <= 0:
        st.error("❌ Error: Effective depth d = h - cover must be > 0")
        st.stop()

    Mu_Nmm = Mu * 1e6  # kN.m -> N.mm

    calculations = []

    # Step 1
    calculations.append({
        "step": "1",
        "description": "Effective Depth",
        "formula": r"d = h - \text{cover}",
        "substitution": rf"{h:.0f} - {cover:.0f}",
        "result": f"{d:.1f} mm",
        "variable": "d"
    })

    if design_code == "ACI 318":
        # ACI: same logic as v17
        denominator_initial = phi * fy * jd * d
        if denominator_initial == 0:
            st.error("❌ Error: φ * fy * jd * d cannot be zero")
            st.stop()

        As_initial = Mu_Nmm / denominator_initial

        calculations.append({
            "step": "2",
            "description": "Initial As",
            "formula": r"A_s = \frac{M_u}{\phi f_y jd \cdot d}",
            "substitution": rf"\frac{{{Mu_Nmm:.2e}}}{{{phi:.2f} \times {fy:.0f} \times {jd:.2f} \times {d:.1f}}}",
            "result": f"{As_initial:.1f} mm²",
            "variable": "As,init"
        })

        denominator_a = 0.85 * fcu * b
        if denominator_a == 0:
            st.error("❌ Error: 0.85 * f'c * b cannot be zero")
            st.stop()

        a_initial = (As_initial * fy) / denominator_a

        calculations.append({
            "step": "3",
            "description": "Depth of Block",
            "formula": r"a = \frac{A_s f_y}{0.85 f'_c b}",
            "substitution": rf"\frac{{{As_initial:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}",
            "result": f"{a_initial:.2f} mm",
            "variable": "a"
        })

        lever_arm = d - a_initial / 2.0
        if lever_arm <= 0:
            st.error("❌ Error: Lever arm (d - a/2) must be > 0")
            st.stop()

        As_calculated = Mu_Nmm / (phi * fy * lever_arm)

        calculations.append({
            "step": "4",
            "description": "Refined As",
            "formula": r"A_s = \frac{M_u}{\phi f_y (d - a/2)}",
            "substitution": rf"\frac{{{Mu_Nmm:.2e}}}{{{phi:.2f} \times {fy:.0f} \times ({d:.1f} - {a_initial/2.0:.2f})}}",
            "result": f"{As_calculated:.1f} mm²",
            "variable": "As,calc"
        })

        As_min_1 = (0.25 * math.sqrt(fcu) / fy) * b * d
        As_min_2 = (1.4 / fy) * b * d
        As_min = max(As_min_1, As_min_2)

        calculations.append({
            "step": "5",
            "description": "Minimum As",
            "formula": r"A_{s,min} = \max\left(\frac{0.25\sqrt{f_c^\prime}}{f_y}b_w d, \frac{1.4}{f_y}b_w d\right)",
            "substitution": rf"\max\left(\frac{{0.25 \times {math.sqrt(fcu):.2f}}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}, \frac{{1.4}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}\right)",
            "result": f"{As_min:.1f} mm²",
            "variable": "As,min"
        })

        As_required = max(As_calculated, As_min)
        governing = "minimum" if abs(As_required - As_min) < 1e-9 else "calculated"

        calculations.append({
            "step": "6",
            "description": "Required As",
            "formula": r"A_{s,req} = \max(A_s, A_{s,min})",
            "substitution": rf"\max({As_calculated:.1f}, {As_min:.1f})",
            "result": f"{As_required:.1f} mm² ({governing})",
            "variable": "As,req"
        })

        a_final = (As_required * fy) / denominator_a
        c = a_final / beta1
        if c <= 0:
            st.error("❌ Error: Neutral axis depth c must be > 0")
            st.stop()

        es = ((d - c) / c) * 0.003

        strain_safe = es >= 0.002
        if es >= 0.005:
            strain_status = "Tension ✓"
        elif es >= 0.002:
            strain_status = "Transition ⚠"
        else:
            strain_status = "Compression ✗"

        phi_Mn_Nmm = phi * As_required * fy * (d - a_final / 2.0)
        phi_Mn = phi_Mn_Nmm / 1e6  # -> kN.m

        capacity_safe = phi_Mn >= Mu
        utilization = (Mu / phi_Mn) * 100.0 if phi_Mn > 0 else 0.0

        calculations.append({
            "step": "7",
            "description": "Design Capacity",
            "formula": r"\phi M_n = \phi A_{s,req} f_y (d - a/2)",
            "substitution": rf"{phi:.2f} \times {As_required:.1f} \times {fy:.0f} \times ({d:.1f} - {a_final/2.0:.2f})",
            "result": f"{phi_Mn:.2f} kN.m",
            "variable": "φMn"
        })

        calculations.append({
            "step": "8",
            "description": "Capacity Check",
            "formula": r"\phi M_n \geq M_u",
            "substitution": f"{phi_Mn:.2f} ≥ {Mu:.2f}",
            "result": f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)',
            "variable": "Check"
        })

    else:
        # ECP: C1/J method per your screenshot
        C1_min = st.session_state.get("C1_min_runtime", None)
        # read constants from expander values if present; otherwise defaults
        # (Streamlit keeps those widget values directly as local variables in this run)
        C1_min = locals().get("C1_min", else_C1_min)
        J_max = locals().get("J_max", else_J_max)
        k1 = locals().get("k1", else_k1)
        k2 = locals().get("k2", else_k2)

        # C1 = d / sqrt(Mu/(fcu*b))
        denom = fcu * b
        if denom <= 0:
            st.error("❌ Error: fcu * b must be > 0")
            st.stop()

        inside = Mu_Nmm / denom  # mm^2
        if inside <= 0:
            st.error("❌ Error: Mu/(fcu*b) must be > 0")
            st.stop()

        C1 = d / math.sqrt(inside)

        calculations.append({
            "step": "2",
            "description": "C1 (ECP)",
            "formula": r"C_1 = \frac{d}{\sqrt{\frac{M_u}{f_{cu}\,b}}}",
            "substitution": rf"\frac{{{d:.1f}}}{{\sqrt{{\frac{{{Mu_Nmm:.2e}}}{{{fcu:.1f}\times {b:.0f}}}}}}}",
            "result": f"{C1:.3f}",
            "variable": "C1"
        })

        C1_ok = C1 >= C1_min
        calculations.append({
            "step": "3",
            "description": "C1 Check",
            "formula": r"C_1 \geq C_{1,\min}",
            "substitution": f"{C1:.3f} ≥ {C1_min:.2f}",
            "result": "PASS ✓" if C1_ok else "FAIL ✗",
            "variable": "Check"
        })

        if not C1_ok:
            st.error(
                f"❌ Error: C1 = {C1:.3f} < C1min = {C1_min:.2f}. "
                "Section is over-reinforced by this method. Reduce Mu or increase b/h (increase d)."
            )
            st.stop()

        # J = (1/k1) * (0.5 + sqrt(0.25 - 1/(k2*C1^2)))
        disc = 0.25 - 1.0 / (k2 * (C1 ** 2))
        if disc < 0:
            st.error(
                f"❌ Error: sqrt term negative (disc={disc:.4f}). "
                "Increase section or reduce Mu."
            )
            st.stop()

        J_raw = (1.0 / k1) * (0.5 + math.sqrt(disc))
        J = min(J_raw, J_max)

        calculations.append({
            "step": "4",
            "description": "J (ECP)",
            "formula": r"J=\frac{1}{k_1}\left(0.5+\sqrt{0.25-\frac{1}{k_2\,C_1^2}}\right)",
            "substitution": rf"\frac{{1}}{{{k1:.2f}}}\left(0.5+\sqrt{{0.25-\frac{{1}}{{{k2:.2f}\times {C1:.3f}^2}}}}\right)",
            "result": f"{J_raw:.4f}",
            "variable": "J"
        })

        calculations.append({
            "step": "5",
            "description": "J used",
            "formula": r"J=\min(J, J_{max})",
            "substitution": f"min({J_raw:.4f}, {J_max:.2f})",
            "result": f"{J:.4f}",
            "variable": "J_used"
        })

        # As = Mu / (fy * J * d)
        denom_As = fy * J * d
        if denom_As <= 0:
            st.error("❌ Error: fy * J * d must be > 0")
            st.stop()

        As_calculated = Mu_Nmm / denom_As

        calculations.append({
            "step": "6",
            "description": "As (ECP)",
            "formula": r"A_s=\frac{M_u}{f_y\,J\,d}",
            "substitution": rf"\frac{{{Mu_Nmm:.2e}}}{{{fy:.0f}\times {J:.4f}\times {d:.1f}}}",
            "result": f"{As_calculated:.1f} mm²",
            "variable": "As,calc"
        })

        # Minimum steel (kept from prior version; adjust if you have exact clause)
        As_min_1 = (0.6 / fy) * b * d
        As_min_2 = (0.225 * math.sqrt(fcu) / fy) * b * d
        As_min = max(As_min_1, As_min_2)

        calculations.append({
            "step": "7",
            "description": "Minimum As (ECP)",
            "formula": r"A_{s,\min}=\max\left(\frac{0.6}{f_y}bd,\frac{0.225\sqrt{f_{cu}}}{f_y}bd\right)",
            "substitution": rf"\max\left(\frac{{0.6}}{{{fy:.0f}}}\times {b:.0f}\times {d:.1f}, \frac{{0.225\times {math.sqrt(fcu):.2f}}}{{{fy:.0f}}}\times {b:.0f}\times {d:.1f}\right)",
            "result": f"{As_min:.1f} mm²",
            "variable": "As,min"
        })

        As_required = max(As_calculated, As_min)
        governing = "minimum" if abs(As_required - As_min) < 1e-9 else "calculated"

        calculations.append({
            "step": "8",
            "description": "Required As",
            "formula": r"A_{s,req}=\max(A_s,A_{s,\min})",
            "substitution": rf"\max({As_calculated:.1f}, {As_min:.1f})",
            "result": f"{As_required:.1f} mm² ({governing})",
            "variable": "As,req"
        })

        # Capacity by same method: Mn = As * fy * J * d
        Mn = (As_required * fy * J * d) / 1e6  # kN.m
        capacity_safe = Mn >= Mu
        utilization = (Mu / Mn) * 100.0 if Mn > 0 else 0.0

        calculations.append({
            "step": "9",
            "description": "Moment Capacity (ECP)",
            "formula": r"M_n=A_s f_y J d",
            "substitution": rf"{As_required:.1f}\times {fy:.0f}\times {J:.4f}\times {d:.1f}",
            "result": f"{Mn:.2f} kN.m",
            "variable": "Mn"
        })

        calculations.append({
            "step": "10",
            "description": "Capacity Check",
            "formula": r"M_n \geq M_u",
            "substitution": f"{Mn:.2f} ≥ {Mu:.2f}",
            "result": f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)',
            "variable": "Check"
        })

        # For unified summary display
        es = None
        c = None
        strain_safe = C1_ok
        strain_status = "OK" if C1_ok else "FAIL"
        phi_Mn = Mn  # reuse display variable name

except Exception as e:
    st.error(f"❌ Calculation Error: {str(e)}")
    st.stop()

# Input Summary
st.markdown('<h2 class="section-header">📋 Input Summary</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Code", "ACI" if design_code == "ACI 318" else "ECP")
    st.metric("Mu", f"{Mu:.2f} kN.m")
with col2:
    st.metric("b", f"{b:.0f} mm")
    st.metric("h", f"{h:.0f} mm")
with col3:
    st.metric("cover", f"{cover:.0f} mm")
    st.metric("d", f"{d:.1f} mm")
with col4:
    st.metric("fy", f"{fy:.0f} MPa")
    st.metric("fcu", f"{fcu:.1f} MPa")

# Calculations
st.markdown('<h2 class="section-header">🔢 Calculations</h2>', unsafe_allow_html=True)
for calc in calculations:
    c1, c2, c3, c4 = st.columns([0.4, 2.5, 2.5, 1.6])
    with c1:
        st.markdown(f"**{calc['step']}**")
    with c2:
        st.markdown(f"**{calc['description']}:** ${calc['formula']}$")
    with c3:
        st.latex(calc["substitution"])
    with c4:
        if "PASS" in calc["result"] or "SAFE" in calc["result"]:
            st.success(calc["result"])
        elif "FAIL" in calc["result"] or "UNSAFE" in calc["result"]:
            st.error(calc["result"])
        else:
            st.info(f"**{calc['result']}**")

# Summary
st.markdown("---")
st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Required Steel Area**")
    st.metric("As Required", f"{As_required:.1f} mm²")

with col2:
    st.markdown("**Analysis**")
    if design_code == "ACI 318":
        st.metric("Steel Strain (εs)", f"{es:.5f}")
        st.metric("Section Type", strain_status)
    else:
        # pull last computed C1/J from calculations list
        # (safe enough; these exist in ECP branch)
        st.metric("C1", next(x["result"] for x in calculations if x["variable"] == "C1"))
        st.metric("J used", next(x["result"] for x in calculations if x["variable"] == "J_used"))
        st.metric("Status", "OK" if strain_safe else "FAIL")

with col3:
    st.markdown("**Safety Status**")
    overall_safe = strain_safe and capacity_safe
    if overall_safe:
        st.success("DESIGN IS SAFE")
    else:
        st.error("DESIGN FAILED")
    st.metric("Utilization", f"{utilization:.1f}%")

# Reinforcement Selection Section
st.markdown("---")
st.markdown('<h2 class="section-header">🔧 Reinforcement Selection</h2>', unsafe_allow_html=True)

# Auto suggestions
st.markdown("### Automatic Suggestions")
col1, col2, col3 = st.columns(3)

suggestion_count = 0
for diameter in [10, 12, 14, 16, 18, 20, 22, 25]:
    area_per_bar = rebar_data[diameter][0]
    num_bars = math.ceil(As_required / area_per_bar)

    if num_bars <= 9 and suggestion_count < 6:
        total_area = rebar_data[diameter][num_bars - 1]
        excess = ((total_area - As_required) / As_required) * 100

        target_col = [col1, col2, col3][suggestion_count % 3]
        with target_col:
            st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        suggestion_count += 1

# Manual Selection
st.markdown("---")
st.markdown("### Manual Selection & Verification")

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    selected_diameter = st.selectbox("Bar Diameter (mm)", options=list(rebar_data.keys()), index=list(rebar_data.keys()).index(16))
with c2:
    selected_num_bars = st.selectbox("Number of Bars", options=list(range(1, 10)), index=3)

selected_As = rebar_data[selected_diameter][selected_num_bars - 1]

st.markdown("---")
st.markdown("### Selected Reinforcement Verification")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Selected Config", f"{selected_num_bars}Ø{selected_diameter}")
with c2:
    st.metric("Provided As", f"{selected_As:.1f} mm²")
    excess_percentage = ((selected_As - As_required) / As_required) * 100
    st.caption(f"Excess: {excess_percentage:+.1f}%")
with c3:
    check_As = selected_As >= As_required
    if check_As:
        st.success(f"✓ As Check\n{selected_As:.0f} ≥ {As_required:.0f}")
    else:
        st.error(f"✗ As Check\n{selected_As:.0f} < {As_required:.0f}")
with c4:
    if design_code == "ACI 318":
        a_selected = (selected_As * fy) / (0.85 * fcu * b)
        c_selected = a_selected / beta1
        es_selected = ((d - c_selected) / c_selected) * 0.003
        phi_Mn_selected = (phi * selected_As * fy * (d - a_selected / 2.0)) / 1e6
        check_capacity = phi_Mn_selected >= Mu
        if check_capacity:
            st.success(f"✓ Capacity Check\nφMn = {phi_Mn_selected:.2f} kN.m")
        else:
            st.error(f"✗ Capacity Check\nφMn = {phi_Mn_selected:.2f} kN.m")
    else:
        # ECP capacity with same J used for the section
        # (J already computed in calculations list)
        J_used_val = float(next(x["result"] for x in calculations if x["variable"] == "J_used"))
        Mn_selected = (selected_As * fy * J_used_val * d) / 1e6
        check_capacity = Mn_selected >= Mu
        if check_capacity:
            st.success(f"✓ Capacity Check\nMn = {Mn_selected:.2f} kN.m")
        else:
            st.error(f"✗ Capacity Check\nMn = {Mn_selected:.2f} kN.m")

# Rebar Table
st.markdown("---")
st.markdown("### Complete Rebar Area Table")

df_data = []
for diameter, areas in rebar_data.items():
    row = [diameter] + areas
    df_data.append(row)

df = pd.DataFrame(df_data, columns=["Ø (mm)", "1", "2", "3", "4", "5", "6", "7", "8", "9"]).set_index("Ø (mm)")
st.dataframe(df, use_container_width=True)
st.caption("Note: All areas in mm²")

# Footer
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.caption(f"Code: {design_code}")
with c2:
    st.caption("Type: Rectangular Beam")
with c3:
    st.caption("Analysis: Flexural Design")
