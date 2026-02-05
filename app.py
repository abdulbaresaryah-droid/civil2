import math
from typing import Optional

import pandas as pd
import streamlit as st

st.set_page_config(page_title="RC Section Design - ACI / ECP", page_icon="🏗️", layout="wide")

st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

# Rebar areas (mm^2)
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
    50: [1963.5, 3928, 5892, 7856, 9820, 11784, 13748, 15712, 17676],
}


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# -----------------------------
# Synced input (number + slider)
# -----------------------------
def _ensure_synced_keys(base_key: str, default: float, lo: float, hi: float) -> None:
    v = st.session_state.get(base_key, default)
    v = clamp(float(v), lo, hi)
    st.session_state[base_key] = v

    num_key = f"{base_key}__num"
    sld_key = f"{base_key}__sld"

    if num_key not in st.session_state:
        st.session_state[num_key] = v
    if sld_key not in st.session_state:
        st.session_state[sld_key] = v


def _sync_from_num(base_key: str) -> None:
    num_key = f"{base_key}__num"
    sld_key = f"{base_key}__sld"
    v = float(st.session_state[num_key])
    st.session_state[base_key] = v
    st.session_state[sld_key] = v  # force slider to match number


def _sync_from_sld(base_key: str) -> None:
    num_key = f"{base_key}__num"
    sld_key = f"{base_key}__sld"
    v = float(st.session_state[sld_key])
    st.session_state[base_key] = v
    st.session_state[num_key] = v  # force number to match slider


def synced_control(
    label: str,
    base_key: str,
    lo: float,
    hi: float,
    step: float,
    default: float,
    unit: str = "",
    help_text: Optional[str] = None,
) -> float:
    _ensure_synced_keys(base_key, default, lo, hi)

    st.sidebar.markdown(f"**{label}** {unit}".rstrip())

    c1, c2 = st.sidebar.columns([1, 1])
    with c1:
        st.number_input(
            "number",
            min_value=lo,
            max_value=hi,
            step=step,
            key=f"{base_key}__num",
            label_visibility="collapsed",
            help=help_text,
            on_change=_sync_from_num,
            args=(base_key,),
        )
    with c2:
        st.slider(
            "slider",
            min_value=lo,
            max_value=hi,
            step=step,
            key=f"{base_key}__sld",
            label_visibility="collapsed",
            help=help_text,
            on_change=_sync_from_sld,
            args=(base_key,),
        )

    return float(st.session_state[base_key])


def _set_synced_value(base_key: str, v: float) -> None:
    st.session_state[base_key] = v
    st.session_state[f"{base_key}__num"] = v
    st.session_state[f"{base_key}__sld"] = v


# Defaults
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    _set_synced_value("fy", 420.0)
    _set_synced_value("fcu", 25.0)
    _set_synced_value("Mu", 100.0)
    _set_synced_value("b", 250.0)
    _set_synced_value("h", 500.0)
    _set_synced_value("cover", 40.0)
    _set_synced_value("phi", 0.90)
    _set_synced_value("jd", 0.90)
    _set_synced_value("beta1", 0.85)


def clear_all_inputs() -> None:
    for k in ["fy", "fcu", "Mu", "b", "h", "cover", "phi", "jd", "beta1"]:
        _set_synced_value(k, 0.0)
    st.rerun()


# -----------------------------
# UI
# -----------------------------
st.markdown('<h1 class="main-header">RC Section Design (ACI / ECP)</h1>', unsafe_allow_html=True)

st.sidebar.header("Input Parameters")

design_code = st.sidebar.radio("Design Code", ["ACI 318", "Egyptian Code (C1/J)"])
st.sidebar.markdown("---")

if st.sidebar.button("Clear All Inputs", type="secondary", use_container_width=True):
    clear_all_inputs()

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")
fy = synced_control("Steel Yield Strength, fy", "fy", 0.0, 600.0, 10.0, float(st.session_state["fy"]), "(MPa)")
fcu = synced_control("Concrete Strength, fcu", "fcu", 0.0, 60.0, 2.5, float(st.session_state["fcu"]), "(MPa)")

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")
Mu = synced_control("Ultimate Moment, Mu", "Mu", 0.0, 500.0, 0.5, float(st.session_state["Mu"]), "(kN.m)")

st.sidebar.markdown("---")
st.sidebar.subheader("Section Dimensions")
b = synced_control("Width, b", "b", 0.0, 2000.0, 50.0, float(st.session_state["b"]), "(mm)")
h = synced_control("Height, h", "h", 0.0, 1500.0, 10.0, float(st.session_state["h"]), "(mm)")
cover = synced_control("Cover", "cover", 0.0, 120.0, 5.0, float(st.session_state["cover"]), "(mm)")

st.sidebar.markdown("---")
st.sidebar.subheader("Design Parameters")

if design_code == "ACI 318":
    phi = synced_control("Strength Reduction Factor, phi", "phi", 0.0, 0.9, 0.05, float(st.session_state["phi"]))
    jd = synced_control("Moment Arm Factor, jd", "jd", 0.0, 0.95, 0.01, float(st.session_state["jd"]))
    beta1 = synced_control("beta1", "beta1", 0.0, 0.85, 0.05, float(st.session_state["beta1"]))
else:
    # ECP constants (always floats, never None)
    with st.sidebar.expander("ECP Constants", expanded=False):
        C1_min = st.number_input("C1 min", min_value=0.0, value=2.76, step=0.01)
        J_max = st.number_input("J max", min_value=0.0, max_value=1.0, value=0.95, step=0.01)
        k1 = st.number_input("k1", min_value=0.01, value=1.15, step=0.01)
        k2 = st.number_input("k2", min_value=0.01, value=0.90, step=0.01)

# -----------------------------
# Validation
# -----------------------------
if not (fy > 0 and fcu > 0 and Mu > 0 and b > 0 and h > 0 and cover >= 0 and h > cover):
    st.warning("Please enter valid inputs (ensure h > cover).")
    st.stop()

if design_code == "ACI 318":
    if not (phi > 0 and jd > 0 and beta1 > 0):
        st.warning("Please enter valid ACI parameters (phi, jd, beta1).")
        st.stop()

# -----------------------------
# Calculations
# -----------------------------
d = h - cover
Mu_Nmm = Mu * 1e6  # kN.m -> N.mm

calculations = []
calculations.append(
    {
        "step": "1",
        "description": "Effective Depth",
        "formula": r"d = h - \text{cover}",
        "substitution": rf"{h:.0f} - {cover:.0f}",
        "result": f"{d:.1f} mm",
    }
)

try:
    if design_code == "ACI 318":
        denom0 = phi * fy * jd * d
        if denom0 <= 0:
            raise ValueError("phi*fy*jd*d must be > 0")

        As0 = Mu_Nmm / denom0
        calculations.append(
            {
                "step": "2",
                "description": "Initial As",
                "formula": r"A_s = \frac{M_u}{\phi f_y jd \, d}",
                "substitution": rf"\frac{{{Mu_Nmm:.2e}}}{{{phi:.2f}\times{fy:.0f}\times{jd:.2f}\times{d:.1f}}}",
                "result": f"{As0:.1f} mm^2",
            }
        )

        denom_a = 0.85 * fcu * b
        if denom_a <= 0:
            raise ValueError("0.85*fcu*b must be > 0")

        a = (As0 * fy) / denom_a
        z = d - a / 2.0
        if z <= 0:
            raise ValueError("lever arm (d-a/2) must be > 0")

        As_calc = Mu_Nmm / (phi * fy * z)

        As_min_1 = (0.25 * math.sqrt(fcu) / fy) * b * d
        As_min_2 = (1.4 / fy) * b * d
        As_min = max(As_min_1, As_min_2)

        As_required = max(As_calc, As_min)

        phiMn = (phi * As_required * fy * (d - (As_required * fy) / denom_a / 2.0)) / 1e6
        capacity_safe = phiMn >= Mu

    else:
        # ---------- ECP (C1/J method) ----------
        # C1 = d / sqrt(Mu/(fcu*b))  (Mu in N.mm, fcu MPa=N/mm^2, b mm => inside sqrt is mm^2)
        denom = fcu * b
        if denom <= 0:
            raise ValueError("fcu*b must be > 0")

        inside = Mu_Nmm / denom
        if inside <= 0:
            raise ValueError("Mu/(fcu*b) must be > 0")

        C1 = d / math.sqrt(inside)

        calculations.append(
            {
                "step": "2",
                "description": "C1 (ECP)",
                "formula": r"C_1=\frac{d}{\sqrt{M_u/(f_{cu}\,b)}}",
                "substitution": rf"\frac{{{d:.1f}}}{{\sqrt{{{Mu_Nmm:.2e}/({fcu:.1f}\times{b:.0f})}}}}",
                "result": f"{C1:.3f}",
            }
        )

        if C1 < float(C1_min):
            st.error(f"Section fails C1 check: C1={C1:.3f} < C1min={float(C1_min):.2f}. Increase section or reduce Mu.")
            st.stop()

        disc = 0.25 - 1.0 / (float(k2) * (C1 ** 2))
        calculations.append(
            {
                "step": "3",
                "description": "Discriminant",
                "formula": r"0.25-\frac{1}{k_2 C_1^2}",
                "substitution": rf"0.25 - 1/({float(k2):.2f}\times {C1:.3f}^2)",
                "result": f"{disc:.6f}",
            }
        )

        if disc < 0:
            st.error("Section is over-reinforced by C1/J method (negative sqrt term). Increase section or reduce Mu.")
            st.stop()

        J_raw = (1.0 / float(k1)) * (0.5 + math.sqrt(disc))
        J_used = min(J_raw, float(J_max))

        calculations.append(
            {
                "step": "4",
                "description": "J (raw / used)",
                "formula": r"J=\frac{1}{k_1}\left(0.5+\sqrt{0.25-\frac{1}{k_2 C_1^2}}\right)",
                "substitution": rf"k1={float(k1):.2f}, k2={float(k2):.2f}",
                "result": f"J_raw={J_raw:.4f}, J_used={J_used:.4f}",
            }
        )

        denom_As = fy * J_used * d
        if denom_As <= 0:
            raise ValueError("fy*J*d must be > 0")

        As_calc = Mu_Nmm / denom_As

        # Minimum steel (keep as you had; adjust if you want exact ECP clause)
        As_min_1 = (0.6 / fy) * b * d
        As_min_2 = (0.225 * math.sqrt(fcu) / fy) * b * d
        As_min = max(As_min_1, As_min_2)

        As_required = max(As_calc, As_min)

        Mn = (As_required * fy * J_used * d) / 1e6  # kN.m
        capacity_safe = Mn >= Mu
        phiMn = Mn  # reuse display variable

except Exception as e:
    st.error(f"Calculation Error: {str(e)}")
    st.stop()

# -----------------------------
# Display
# -----------------------------
st.markdown('<h2 class="section-header">Input Summary</h2>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Code", "ACI" if design_code == "ACI 318" else "ECP")
    st.metric("Mu", f"{Mu:.2f} kN.m")
with c2:
    st.metric("b", f"{b:.0f} mm")
    st.metric("h", f"{h:.0f} mm")
with c3:
    st.metric("cover", f"{cover:.0f} mm")
    st.metric("d", f"{d:.1f} mm")
with c4:
    st.metric("fy", f"{fy:.0f} MPa")
    st.metric("fcu", f"{fcu:.1f} MPa")

st.markdown('<h2 class="section-header">Calculations</h2>', unsafe_allow_html=True)
for calc in calculations:
    a, bcol, c, dcol = st.columns([0.4, 2.6, 2.6, 1.4])
    with a:
        st.markdown(f"**{calc['step']}**")
    with bcol:
        st.markdown(f"**{calc['description']}**: ${calc['formula']}$")
    with c:
        st.latex(calc["substitution"])
    with dcol:
        st.info(calc["result"])

st.markdown("---")
st.markdown('<h2 class="section-header">Design Summary</h2>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("As required", f"{As_required:.1f} mm^2")
with c2:
    st.metric("Capacity", f"{phiMn:.2f} kN.m")
with c3:
    st.success("SAFE" if capacity_safe else "UNSAFE")

# Reinforcement suggestions
st.markdown("---")
st.markdown('<h2 class="section-header">Reinforcement Selection</h2>', unsafe_allow_html=True)

st.markdown("Automatic Suggestions")
col1, col2, col3 = st.columns(3)
suggestion_count = 0
for diameter in [10, 12, 14, 16, 18, 20, 22, 25]:
    area_per_bar = rebar_data[diameter][0]
    num_bars = math.ceil(As_required / area_per_bar)
    if 1 <= num_bars <= 9 and suggestion_count < 6:
        total_area = rebar_data[diameter][num_bars - 1]
        excess = ((total_area - As_required) / As_required) * 100.0
        target = [col1, col2, col3][suggestion_count % 3]
        with target:
            st.info(f"{num_bars}Ø{diameter}\nAs = {total_area:.0f} mm^2\n(+{excess:.1f}%)")
        suggestion_count += 1

st.markdown("---")
st.markdown("Manual Selection & Verification")
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    selected_diameter = st.selectbox("Bar Diameter (mm)", options=list(rebar_data.keys()), index=list(rebar_data.keys()).index(16))
with c2:
    selected_num_bars = st.selectbox("Number of Bars", options=list(range(1, 10)), index=3)

selected_As = rebar_data[selected_diameter][selected_num_bars - 1]
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Selected", f"{selected_num_bars}Ø{selected_diameter}")
with c2:
    st.metric("As provided", f"{selected_As:.1f} mm^2")
with c3:
    if selected_As >= As_required:
        st.success("As OK")
    else:
        st.error("As NOT OK")
with c4:
    if design_code == "ACI 318":
        a_sel = (selected_As * fy) / (0.85 * fcu * b)
        phiMn_sel = (phi * selected_As * fy * (d - a_sel / 2.0)) / 1e6
        st.metric("Capacity", f"{phiMn_sel:.2f} kN.m")
    else:
        # Use same ECP J_used computed above (only exists in ECP run)
        # If you want per-selection recalculation of J, you'd need to recompute C1/J for the same section (unchanged).
        Mn_sel = (selected_As * fy * (J_used if design_code != "ACI 318" else 0.0) * d) / 1e6
        st.metric("Capacity", f"{Mn_sel:.2f} kN.m")

# Rebar table
st.markdown("---")
st.markdown("Complete Rebar Area Table")
df_data = []
for dia, areas in rebar_data.items():
    df_data.append([dia] + areas)
df = pd.DataFrame(df_data, columns=["Ø (mm)", "1", "2", "3", "4", "5", "6", "7", "8", "9"]).set_index("Ø (mm)")
st.dataframe(df, use_container_width=True)
