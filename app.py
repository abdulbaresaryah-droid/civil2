import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - ACI",
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
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div[data-testid="column"] {
        padding: 2px 5px !important;
    }
    .element-container {
        margin-bottom: 0px !important;
    }
    .katex {
        font-size: 0.95em;
    }
    </style>
""", unsafe_allow_html=True)

# Rebar data table
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

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True

# Reset function
def clear_all_inputs():
    keys_to_delete = ['fy', 'fcu', 'Mu', 'b', 'h', 'cover', 'phi', 'jd', 'beta1']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Title
st.markdown('<h1 class="main-header">🏗️ RC Section Design (ACI)</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Input Parameters")

# Clear button
if st.sidebar.button("🗑️ Clear All Inputs", type="secondary", use_container_width=True):
    clear_all_inputs()

st.sidebar.markdown("---")

# Input method
input_method = st.sidebar.radio("Input Method", ["Sliders", "Manual Input"])

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")

# Material properties
if input_method == "Sliders":
    st.sidebar.info("💡 Set all values to proceed")
    
    fy = st.sidebar.slider("Steel Yield Strength, fy (MPa)", 
                          min_value=0.0, max_value=600.0, 
                          value=st.session_state.get('fy', 0.0), 
                          step=10.0, key='fy')
    
    fcu = st.sidebar.slider("Concrete Strength, f'c (MPa)", 
                           min_value=0.0, max_value=50.0, 
                           value=st.session_state.get('fcu', 0.0), 
                           step=2.5, key='fcu')
else:
    fy = st.sidebar.number_input("Steel Yield Strength, fy (MPa)", 
                                value=None, min_value=0.0, max_value=600.0, 
                                step=10.0, key='fy', placeholder="Enter fy")
    fcu = st.sidebar.number_input("Concrete Strength, f'c (MPa)", 
                                 value=None, min_value=0.0, max_value=50.0, 
                                 step=2.5, key='fcu', placeholder="Enter f'c")

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")

if input_method == "Sliders":
    Mu = st.sidebar.slider("Ultimate Moment, Mu (kN.m)", 
                          min_value=0.0, max_value=500.0, 
                          value=st.session_state.get('Mu', 0.0), 
                          step=0.5, key='Mu')
else:
    Mu = st.sidebar.number_input("Ultimate Moment, Mu (kN.m)", 
                                value=None, min_value=0.0, 
                                step=0.1, key='Mu', placeholder="Enter Mu")

st.sidebar.markdown("---")
st.sidebar.subheader("Section Dimensions")

if input_method == "Sliders":
    b = st.sidebar.slider("Width, b (mm)", 
                         min_value=0.0, max_value=2000.0, 
                         value=st.session_state.get('b', 0.0), 
                         step=50.0, key='b')
    
    h = st.sidebar.slider("Height, h (mm)", 
                         min_value=0.0, max_value=1000.0, 
                         value=st.session_state.get('h', 0.0), 
                         step=10.0, key='h')
    
    cover = st.sidebar.slider("Cover (mm)", 
                             min_value=0.0, max_value=75.0,
                             value=st.session_state.get('cover', 0.0), 
                             step=5.0, key='cover')
else:
    b = st.sidebar.number_input("Width, b (mm)", 
                               value=None, min_value=0.0, 
                               step=50.0, key='b', placeholder="Enter b")
    h = st.sidebar.number_input("Height, h (mm)", 
                               value=None, min_value=0.0, 
                               step=10.0, key='h', placeholder="Enter h")
    cover = st.sidebar.number_input("Cover (mm)", 
                                   value=None, min_value=0.0, max_value=75.0, 
                                   step=5.0, key='cover', placeholder="Enter cover")

st.sidebar.markdown("---")
st.sidebar.subheader("Design Parameters")

if input_method == "Sliders":
    phi = st.sidebar.slider("Strength Reduction Factor, φ", 
                           min_value=0.0, max_value=0.9,
                           value=st.session_state.get('phi', 0.0), 
                           step=0.05, key='phi')
    
    jd = st.sidebar.slider("Moment Arm Factor, jd", 
                          min_value=0.0, max_value=0.95,
                          value=st.session_state.get('jd', 0.0), 
                          step=0.01, key='jd')
    
    beta1 = st.sidebar.slider("β₁ Factor", 
                             min_value=0.0, max_value=0.85,
                             value=st.session_state.get('beta1', 0.0), 
                             step=0.05, key='beta1')
else:
    phi = st.sidebar.number_input("Strength Reduction Factor, φ", 
                                 value=None, min_value=0.0, max_value=0.9, 
                                 step=0.05, key='phi', placeholder="Enter φ")
    jd = st.sidebar.number_input("Moment Arm Factor, jd", 
                                value=None, min_value=0.0, max_value=0.95, 
                                step=0.01, key='jd', placeholder="Enter jd")
    beta1 = st.sidebar.number_input("β₁ Factor", 
                                   value=None, min_value=0.0, max_value=0.85, 
                                   step=0.05, key='beta1', placeholder="Enter β₁")

# Validation - Must check ALL values are greater than 0
if input_method == "Sliders":
    all_inputs_valid = all([
        fy > 0,
        fcu > 0,
        Mu > 0,
        b > 0,
        h > 0,
        cover >= 0,  # cover can be 0
        h > cover,   # h must be > cover
        phi > 0,
        jd > 0,
        beta1 > 0
    ])
else:
    all_inputs_valid = all([
        fy is not None and fy > 0,
        fcu is not None and fcu > 0,
        Mu is not None and Mu > 0,
        b is not None and b > 0,
        h is not None and h > 0,
        cover is not None and cover >= 0,
        h is not None and cover is not None and h > cover,
        phi is not None and phi > 0,
        jd is not None and jd > 0,
        beta1 is not None and beta1 > 0
    ])

if not all_inputs_valid:
    st.warning("⚠️ Please enter all input values to proceed with calculations")
    if input_method == "Sliders":
        st.info("💡 Set all sliders to appropriate values")
        st.info("⚠️ Make sure: h > cover")
    else:
        st.info("💡 Fill in all required parameters in the sidebar")
    st.stop()

# Calculations - التحقق من القيم قبل الحساب
try:
    # Step 1: Effective depth
    d = h - cover
    
    if d <= 0:
        st.error("❌ Error: Effective depth d = h - cover must be > 0")
        st.stop()
    
    # Step 2: Convert Mu to N.mm
    Mu_Nmm = Mu * 1e6  # kN.m to N.mm
    
    # Step 3: Initial As using approximate formula
    # Mu = φ * As * fy * jd * d
    # As = Mu / (φ * fy * jd * d)
    denominator_initial = phi * fy * jd * d
    if denominator_initial == 0:
        st.error("❌ Error: φ * fy * jd * d cannot be zero")
        st.stop()
    
    As_initial = Mu_Nmm / denominator_initial
    
    # Step 4: Initial depth of compression block
    # a = (As * fy) / (0.85 * f'c * b)
    denominator_a = 0.85 * fcu * b
    if denominator_a == 0:
        st.error("❌ Error: 0.85 * f'c * b cannot be zero")
        st.stop()
    
    a_initial = (As_initial * fy) / denominator_a
    
    # Step 5: Refined As using exact formula
    # Mu = φ * As * fy * (d - a/2)
    # As = Mu / [φ * fy * (d - a/2)]
    lever_arm = d - a_initial/2
    if lever_arm <= 0:
        st.error("❌ Error: Lever arm (d - a/2) must be > 0")
        st.stop()
    
    As_calculated = Mu_Nmm / (phi * fy * lever_arm)
    
    # Step 6: Minimum steel area
    # As,min = max(0.25*√f'c/fy * bw*d, 1.4/fy * bw*d)
    As_min_1 = (0.25 * math.sqrt(fcu) / fy) * b * d
    As_min_2 = (1.4 / fy) * b * d
    As_min = max(As_min_1, As_min_2)
    
    # Step 7: Required As
    As_required = max(As_calculated, As_min)
    
    # Step 8: Final depth of compression block
    a_final = (As_required * fy) / denominator_a
    
    # Step 9: Neutral axis depth
    c = a_final / beta1
    
    # Step 10: Steel strain
    if c <= 0:
        st.error("❌ Error: Neutral axis depth c must be > 0")
        st.stop()
    
    es = ((d - c) / c) * 0.003
    
    # Step 11: Design moment capacity
    phi_Mn_Nmm = phi * As_required * fy * (d - a_final/2)
    phi_Mn = phi_Mn_Nmm / 1e6  # N.mm to kN.m
    
    # Step 12: Safety checks
    strain_safe = es >= 0.002
    capacity_safe = phi_Mn >= Mu
    
    if es >= 0.005:
        strain_status = "Tension ✓"
    elif es >= 0.002:
        strain_status = "Transition ⚠"
    else:
        strain_status = "Compression ✗"
    
    utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0

except ZeroDivisionError:
    st.error("❌ Calculation Error: Division by zero detected. Please check your inputs.")
    st.stop()
except Exception as e:
    st.error(f"❌ Calculation Error: {str(e)}")
    st.stop()

# Input Summary
st.markdown('<h2 class="section-header">📋 Input Summary</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Mu", f"{Mu:.2f} kN.m")
    st.metric("b", f"{b:.0f} mm")
with col2:
    st.metric("h", f"{h:.0f} mm")
    st.metric("cover", f"{cover:.0f} mm")
with col3:
    st.metric("fy", f"{fy:.0f} MPa")
    st.metric("f'c", f"{fcu:.1f} MPa")
with col4:
    st.metric("φ", f"{phi:.2f}")
    st.metric("jd", f"{jd:.2f}")

# Calculations
st.markdown('<h2 class="section-header">🔢 Calculations</h2>', unsafe_allow_html=True)

# Create calculation steps
calculations = []

# Step 1: d
calculations.append({
    'step': '1',
    'description': 'Effective Depth',
    'formula': r'd = h - \text{cover}',
    'substitution': rf'{h:.0f} - {cover:.0f}',
    'result': f'{d:.1f} mm',
    'variable': 'd'
})

# Step 2: As initial
calculations.append({
    'step': '2',
    'description': 'Initial As',
    'formula': r'A_s = \frac{M_u}{\phi f_y jd \cdot d}',
    'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \times {fy:.0f} \times {jd:.2f} \times {d:.1f}}}',
    'result': f'{As_initial:.1f} mm²',
    'variable': 'As,init'
})

# Step 3: a initial
calculations.append({
    'step': '3',
    'description': 'Depth of Block',
    'formula': r"a = \frac{A_s f_y}{0.85 f'_c b}",
    'substitution': rf'\frac{{{As_initial:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}',
    'result': f'{a_initial:.2f} mm',
    'variable': 'a'
})

# Step 4: As calculated
calculations.append({
    'step': '4',
    'description': 'Refined As',
    'formula': r'A_s = \frac{M_u}{\phi f_y (d - a/2)}',
    'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \times {fy:.0f} \times ({d:.1f} - {a_initial/2:.2f})}}',
    'result': f'{As_calculated:.1f} mm²',
    'variable': 'As,calc'
})

# Step 5: As min
calculations.append({
    'step': '5',
    'description': 'Minimum As',
    'formula': r'A_{s,min} = \max\left(\frac{0.25\sqrt{f_c^\prime}}{f_y}b_w d, \frac{1.4}{f_y}b_w d\right)',
    'substitution': rf'\max\left(\frac{{0.25 \times {math.sqrt(fcu):.2f}}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}, \frac{{1.4}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}\right)',
    'result': f'{As_min:.1f} mm²',
    'variable': 'As,min'
})

# Step 6: As required
governing = "minimum" if As_required == As_min else "calculated"
calculations.append({
    'step': '6',
    'description': 'Required As',
    'formula': r'A_{s,req} = \max(A_s, A_{s,min})',
    'substitution': rf'\max({As_calculated:.1f}, {As_min:.1f})',
    'result': f'{As_required:.1f} mm² ({governing})',
    'variable': 'As,req'
})

# Step 7: a final
calculations.append({
    'step': '7',
    'description': 'Final a',
    'formula': r"a = \frac{A_{s,req} f_y}{0.85 f'_c b}",
    'substitution': rf'\frac{{{As_required:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}',
    'result': f'{a_final:.2f} mm',
    'variable': 'a,final'
})

# Step 8: c
calculations.append({
    'step': '8',
    'description': 'Neutral Axis',
    'formula': r'c = \frac{a}{\beta_1}',
    'substitution': rf'\frac{{{a_final:.2f}}}{{{beta1:.2f}}}',
    'result': f'{c:.2f} mm',
    'variable': 'c'
})

# Step 9: εs
calculations.append({
    'step': '9',
    'description': 'Steel Strain',
    'formula': r'\varepsilon_s = \frac{d-c}{c} \times 0.003',
    'substitution': rf'\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \times 0.003',
    'result': f'{es:.5f}',
    'variable': 'εs'
})

# Step 10: Check εs
calculations.append({
    'step': '10',
    'description': 'Check εs',
    'formula': r'\varepsilon_s \geq 0.002',
    'substitution': f'{es:.5f} ≥ 0.002',
    'result': f'{"PASS ✓" if strain_safe else "FAIL ✗"} ({strain_status})',
    'variable': 'Check'
})

# Step 11: φMn
calculations.append({
    'step': '11',
    'description': 'Design Capacity',
    'formula': r'\phi M_n = \phi A_{s,req} f_y (d - a/2)',
    'substitution': rf'{phi:.2f} \times {As_required:.1f} \times {fy:.0f} \times ({d:.1f} - {a_final/2:.2f})',
    'result': f'{phi_Mn:.2f} kN.m',
    'variable': 'φMn'
})

# Step 12: Check capacity
calculations.append({
    'step': '12',
    'description': 'Capacity Check',
    'formula': r'\phi M_n \geq M_u',
    'substitution': f'{phi_Mn:.2f} ≥ {Mu:.2f}',
    'result': f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)',
    'variable': 'Check'
})

# Display calculations
for calc in calculations:
    col1, col2, col3, col4 = st.columns([0.4, 2.5, 2.5, 1.6])
    
    with col1:
        st.markdown(f"**{calc['step']}**")
    
    with col2:
        st.markdown(f"**{calc['description']}:** ${calc['formula']}$")
    
    with col3:
        st.latex(calc['substitution'])
    
    with col4:
        if 'PASS' in calc['result'] or 'SAFE' in calc['result']:
            st.success(calc['result'])
        elif 'FAIL' in calc['result'] or 'UNSAFE' in calc['result']:
            st.error(calc['result'])
        else:
            st.info(f"**{calc['result']}**")

# Summary
st.markdown("---")
st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📏 Required Steel Area**")
    st.metric("As Required", f"{As_required:.1f} mm²")
    st.metric("Effective Depth", f"{d:.1f} mm")

with col2:
    st.markdown("**🔍 Analysis**")
    st.metric("Neutral Axis (c)", f"{c:.2f} mm")
    st.metric("c/d ratio", f"{(c/d):.3f}")
    st.metric("Steel Strain (εs)", f"{es:.5f}")
    st.metric("Section Type", strain_status)

with col3:
    st.markdown("**✅ Safety Status**")
    overall_safe = strain_safe and capacity_safe
    
    if overall_safe:
        st.success("### ✅ DESIGN IS SAFE")
    else:
        st.error("### ❌ DESIGN FAILED")
    
    st.markdown("**Checks:**")
    st.markdown(f"{'✅' if strain_safe else '❌'} Steel Strain: {es:.5f} {'≥' if strain_safe else '<'} 0.002")
    st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: φMn={phi_Mn:.2f} {'≥' if capacity_safe else '<'} Mu={Mu:.2f}")
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel")
    
    st.metric("Capacity Ratio", f"{phi_Mn/Mu:.2f}")

# Reinforcement Selection Section
st.markdown("---")
st.markdown('<h2 class="section-header">🔧 Reinforcement Selection</h2>', unsafe_allow_html=True)

# Auto suggestions
st.markdown("### 💡 Automatic Suggestions")
col1, col2, col3 = st.columns(3)

suggestion_count = 0
for diameter in [10, 12, 14, 16, 18, 20, 22, 25]:
    area_per_bar = rebar_data[diameter][0]
    num_bars = math.ceil(As_required / area_per_bar)
    
    if num_bars <= 9 and suggestion_count < 6:
        total_area = rebar_data[diameter][num_bars - 1]
        excess = ((total_area - As_required) / As_required) * 100
        
        if suggestion_count % 3 == 0:
            with col1:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        elif suggestion_count % 3 == 1:
            with col2:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        else:
            with col3:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        
        suggestion_count += 1

# Manual Selection
st.markdown("---")
st.markdown("### 🎯 Manual Selection & Verification")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    selected_diameter = st.selectbox(
        "Bar Diameter (mm)",
        options=list(rebar_data.keys()),
        index=list(rebar_data.keys()).index(16)
    )

with col2:
    selected_num_bars = st.selectbox(
        "Number of Bars",
        options=list(range(1, 10)),
        index=3
    )

# Get selected reinforcement area
selected_As = rebar_data[selected_diameter][selected_num_bars - 1]

# Verify selected reinforcement
st.markdown("---")
st.markdown("### ✅ Selected Reinforcement Verification")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Selected Config", f"{selected_num_bars}Ø{selected_diameter}")

with col2:
    st.metric("Provided As", f"{selected_As:.1f} mm²")
    excess_percentage = ((selected_As - As_required) / As_required) * 100
    st.caption(f"Excess: {excess_percentage:+.1f}%")

with col3:
    check_As = selected_As >= As_required
    if check_As:
        st.success(f"✓ As Check\n{selected_As:.0f} ≥ {As_required:.0f}")
    else:
        st.error(f"✗ As Check\n{selected_As:.0f} < {As_required:.0f}")

with col4:
    # Re-calculate capacity with selected As
    a_selected = (selected_As * fy) / (0.85 * fcu * b)
    c_selected = a_selected / beta1
    es_selected = ((d - c_selected) / c_selected) * 0.003
    phi_Mn_selected = (phi * selected_As * fy * (d - a_selected/2)) / 1e6
    
    check_capacity = phi_Mn_selected >= Mu
    if check_capacity:
        st.success(f"✓ Capacity Check\nφMn = {phi_Mn_selected:.2f} kN.m")
    else:
        st.error(f"✗ Capacity Check\nφMn = {phi_Mn_selected:.2f} kN.m")

# Detailed verification
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Analysis with Selected Steel**")
    st.metric("a (selected)", f"{a_selected:.2f} mm")
    st.metric("c (selected)", f"{c_selected:.2f} mm")
    st.metric("c/d ratio", f"{(c_selected/d):.3f}")

with col2:
    st.markdown("**⚡ Strain Analysis**")
    st.metric("εs (selected)", f"{es_selected:.5f}")
    
    if es_selected >= 0.005:
        st.success("✓ Tension Controlled")
    elif es_selected >= 0.002:
        st.warning("⚠ Transition Zone")
    else:
        st.error("✗ Compression Controlled")

with col3:
    st.markdown("**🎯 Final Status**")
    final_safe = check_As and check_capacity and (es_selected >= 0.002)
    
    if final_safe:
        st.success("### ✅ SELECTED CONFIG IS SAFE")
    else:
        st.error("### ❌ SELECTED CONFIG FAILED")
    
    st.metric("Utilization", f"{(Mu/phi_Mn_selected)*100:.1f}%")

# Rebar Table
st.markdown("---")
st.markdown("### 📋 Complete Rebar Area Table")

df_data = []
for diameter, areas in rebar_data.items():
    row = [diameter] + areas
    df_data.append(row)

df = pd.DataFrame(df_data, columns=['Ø (mm)', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
df = df.set_index('Ø (mm)')

st.dataframe(df, use_container_width=True)
st.caption("📝 Note: All areas in mm²")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏗️ **Code**: ACI 318")
with col2:
    st.caption("📐 **Type**: Rectangular Beam")
with col3:
    st.caption("🔧 **Analysis**: Flexural Design")
