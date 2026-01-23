# System Requirements - Aviation Performance Tool

This document defines the system behavior using the **EARS** (Easy Approach to Requirements Syntax) patterns.

## Status Definitions

| Status | Description |
|--------|-------------|
| `Draft` | Requirement is under discussion, not yet approved |
| `Approved` | Requirement is approved and ready for implementation |
| `Rejected` | Requirement is rejected; AI may delete or reformulate it |
| `Implemented` | Code for this requirement exists |
| `Verified` | Tests for this requirement pass |

---

## Priority Definitions

| Level | Classification | Definition |
|---|---|---|
| **P1** | **Critical/Safety** | Essential for flight-safe calculations. The app is unusable without this (e.g., M&B core, interpolation, unit conversion). |
| **P2** | **Operational/Efficiency** | Significant value and error reduction in the cockpit (e.g., METAR-fetch, passenger profiles, wind calculation). |
| **P3** | **Comfort/Future** | Facilitates documentation or administration (e.g., PDF-export, cloud-sync, favorites). |

---

## 0. General & System Requirements (SYS)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-SYS-01** | Ubiquitous | The system shall be fully functional without an active internet connection; all aircraft profiles and calculation logic shall be stored locally. | Approved | **P1** | Ensure usability in remote airfields or during flight. |
| **REQ-SYS-02** | Ubiquitous | The system shall store aircraft profiles and flight plans in a standardized, portable format (JSON). | Approved | **P1** | Human-readable format and future-proofing. |
| **REQ-SYS-03** | Ubiquitous | The system shall support global and per-profile unit configuration (kg/lbs, gal/L) with automatic normalization to SI units. | Approved | **P1** | Core mitigation for unit-entry errors (H-01). |

---

## 1. Aircraft Management (AC)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-AC-01** | Ubiquitous | The system shall allow users to create, read, update, and delete aircraft profiles. | Approved | **P1** | Core functionality for fleet management. |
| **REQ-AC-02** | Ubiquitous | The system shall store the Basic Empty Mass, Center of Gravity (CG), and MTOM, supporting date-based versioning for weighing reports. | Approved | **P1** | Critical for M&B safety; weight changes over time due to repairs/modifications. |
| **REQ-AC-03** | Event-driven | When a new aircraft registration is entered, the system shall verify that the registration format is valid. | Approved | **P2** | Pre-validation of registration identity (e.g., D-EBPF). |
| **REQ-AC-04** | Unwanted Behavior | If an aircraft registration already exists, then the system shall display an error message "Aircraft registration already exists". | Approved | **P2** | Avoid data duplication and confusion between aircraft records. |
| **REQ-AC-05** | Ubiquitous | The system shall allow the creation of aircraft profiles via a configuration file (no hard-coding) that defines MTOM, Empty Weight, CG limits, and Moment Arms. | Approved | **P1** | Facilitates "easy maintenance" without software re-compilation. |
| **REQ-AC-06** | Event-driven | When a certification category is selected (e.g., "Normal" vs. "Utility"), the system shall dynamically update the MTOM, allowed stations (e.g., disabling rear seats), and valid CG envelope boundaries. | Approved | **P2** | Necessary for historical aircraft like Klemm KL 107 B with dual categories. |
| **REQ-AC-07** | Ubiquitous | The system shall support loading stations defined by variable moment tables (non-linear arms) in addition to fixed scalar arms. | Approved | **P1** | Supports swept-wing or complex tank configurations where CG shifts with fuel level. |
| **REQ-AC-08** | Ubiquitous | The system shall allow the definition of multiple independent fuel tanks, each with its own lever arm, capacity, and unusable fuel quantity. | Approved | **P1** | Accurate moment calculation for split tanks (e.g., Klemm hull tanks vs. wing tanks). |
| **REQ-AC-09** | Ubiquitous | The system shall store a "Valid From" date for each empty weight/arm value to support weighing report versioning. | Approved | **P2** | Traceability of legal weight data over the aircraft's lifecycle. |
| **REQ-AC-10** | State-driven | The system shall implement a status system for aircraft profiles (Draft vs. Verified). New or edited profiles must be "Verified" and locked before use; calculations performed with a "Draft" profile shall display a permanent, high-visibility warning. | Approved | **P1** | Prevents usage of unverified or typo-prone POH data bases. |
| **REQ-AC-12** | Ubiquitous | The system shall support multiple Envelope Categories (Normal, Utility, Aerobatic) per aircraft, each with independent CG envelope boundaries and MTOM limits. | Approved | **P1** | Full certification flexibility (e.g., Diamond DA 40 D polygonal envelopes). |
| **REQ-AC-13** | Ubiquitous | The system shall support independent units per aircraft (kg/lbs for mass, L/gal for volume) and convert them internally for calculation logic. | Approved | **P1** | Prevents manual unit conversion errors by the pilot. |

---

## 2. Mass & Balance (MB)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-MB-01** | Ubiquitous | The system shall calculate Total Weight and Center of Gravity (CG) based on load station inputs. | Approved | **P1** | Fundamental safety calculation for flight stability. |
| **REQ-MB-02** | State-driven | While in the calculation view, the system shall display a real-time CG envelope chart. | Approved | **P1** | Instant situational awareness for the pilot. |
| **REQ-MB-03** | Unwanted Behavior | If the calculated CG is outside the defined aircraft envelope, then the system shall display a visual warning. | Approved | **P1** | Prevents takeoff in an uncontrollable flight state. |
| **REQ-MB-04** | Unwanted Behavior | If the Total Weight exceeds MTOM, then the system shall display a visual warning in red. | Approved | **P1** | Prevents structural overload and certified limit violation. |
| **REQ-MB-05** | Ubiquitous | The system shall support graphical loading diagram display as an alternative to numerical CG calculation. | Approved | **P2** | Visual cross-check against POH diagrams. |
| **REQ-MB-06** | Ubiquitous | The system shall verify CG limits using a Point-in-Polygon algorithm to support non-linear, sloped envelopes (polygonal shapes). | Approved | **P1** | Required for modern aircraft (e.g., Diamond DA 40) with variable CG limits. |
| **REQ-MB-07** | Event-driven | The system shall automatically calculate and display the Center of Gravity for both the Take-off state AND the Landing state (Zero Fuel / Landing Fuel) and plot both points within the envelope diagram. | Approved | **P1** | Critical for detecting CG migration that might be safe at takeoff but dangerous at landing (e.g., Klemm). |
| **REQ-MB-08** | Ubiquitous | The system shall calculate and validate the Zero Fuel Mass (ZFM) against the aircraft's Maximum Zero Fuel Mass (MZFM) if specified. | Approved | **P2** | Protects wing structural integrity (bending relief limitations). |
| **REQ-MB-09** | Ubiquitous | The system shall render a dynamic CG graph displaying the envelope, the Zero Fuel Point, Take-off Point, and Landing Point, connected by a vector indicating the fuel burn shift. | Approved | **P2** | Displays the "history" of the flight's balance in one view. |
| **REQ-MB-10** | Unwanted Behavior | If the CG migration vector exits the envelope at any point, the system shall display a warning indicating when the CG becomes out of limits. | Approved | **P1** | Detects mid-flight limit violations before they occur. |
| **REQ-MB-11** | Ubiquitous | The system shall calculate moments using either fixed arms or variable moment tables for each loading station. | Approved | **P1** | Flexibility for standard vs. complex station geometry. |

---

## 3. Performance & FSM 3/75 (PF)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-PF-01** | Ubiquitous | The system shall calculate Takeoff Distance Required (TODR) based on FSM 3/75 formulas. | Approved | **P1** | Regulatory fallback for historic aircraft (Klemm KL 107 B). |
| **REQ-PF-02** | Ubiquitous | The system shall implement two distinct calculation modes per aircraft: Mode A (Interpolation from manufacturer tables) and Mode B (Algorithmic using FSM 3/75). | Approved | **P1** | Hybrid engine to support both modern (Tecnam/Diamond) and legacy aircraft. |
| **REQ-PF-03** | Event-driven | When wind speed is entered, the system shall correct the performance data using the headwind/tailwind component. | Approved | **P2** | Wind significantly affects T/O and Landing distances. |
| **REQ-PF-04** | Event-driven | If detailed take-off performance data are present in the aircraft POH, the system shall use those values; otherwise, it shall fall back to the standard FSM 3/75 formulas. | Approved | **P1** | Prioritize manufacturer data for higher precision. |
| **REQ-PF-05** | Ubiquitous | The system shall calculate Density Altitude based on aerodrome elevation, QNH, and temperature. | Approved | **P1** | Most critical Performance factor; prevents "Hot & High" accidents. |
| **REQ-PF-06** | Ubiquitous | The system shall allow a user-defined safety factor to be applied to the calculated takeoff/landing distance. | Approved | **P2** | Standard pilot practice to add margins (e.g., 1.3x) for safety. |
| **REQ-PF-07** | Ubiquitous | The system shall calculate CG for both takeoff state and landing state (zero fuel or landing fuel) to detect CG migration out of limits. | Approved | **P1** | Safety check for the entire duration of the flight. |
| **REQ-PF-08** | Event-driven | When a runway is selected, the system shall automatically suggest the appropriate surface factor for the calculation. | Approved | **P2** | Reduces manual lookup errors of grass/paved factors. |
| **REQ-PF-09** | Unwanted Behavior | If the calculated takeoff/landing distance exceeds the available TORA/LDA, the system shall display a flashing red warning (high‑visibility critical alert). | Approved | **P1** | Critical Go/No‑Go decision aid. |
| **REQ-PF-19** | Event-driven | When wind components are available, the system shall calculate and suggest the best runway choice based on the current wind components from the METAR. | Approved | **P2** | Optimizes performance and safety by selecting runway with most favorable headwind component. |
| **REQ-PF-10** | Ubiquitous | The system shall support both tabular performance data (with interpolation) and formula-based calculations. | Approved | **P1** | Flexibility for different POH documentation styles. |
| **REQ-PF-11** | Ubiquitous | The system shall store aircraft-specific correction factors for runway surface (grass, paved), slope, and wind components. | Approved | **P1** | Customization per aircraft type/STC requirements. |
| **REQ-PF-12** | Ubiquitous | For Mode A (tabular data), the system shall use bilinear interpolation to calculate performance values between grid points; extrapolation beyond table limits is permitted only as defined in REQ-PF-13. | Approved | **P1** | Prevents inaccuracies of linear interpolation while allowing controlled boundary operations. |
| **REQ-PF-13** | Ubiquitous | The system shall allow performance calculations within a 10% extrapolation range, distinguishing between "positive" and "negative" trends: worse conditions (higher Temp/Alt/Weight) shall be extrapolated linearly with a penalty; better conditions (lower Temp/Alt) shall be capped per REQ-PF-17. | Approved | **P1** | Prevents reckless optimistic extrapolation while providing data for slight boundary exceedance. |
| **REQ-PF-14** | Ubiquitous | For worse-condition extrapolation (REQ-PF-13), the system shall automatically apply a 20% safety penalty on top of all other factors. | Approved | **P1** | Conservative approach to account for uncertified data extrapolation. |
| **REQ-PF-15** | Ubiquitous | Whenever extrapolated data is used, the system shall display a prominent UI warning and require explicit user confirmation ("Pilot-in-Command acknowledges extrapolated data"). | Approved | **P1** | Ensures pilot awareness of the increased risk and non-certified status of the data. |
| **REQ-PF-16** | Ubiquitous | The system shall automatically calculate Pressure Altitude based on user inputs for Airport Elevation and QNH using the formula: PA = Elevation + (1013.25 - QNH) × 30. | Approved | **P1** | PA is the correct entry parameter for all POH charts. |
| **REQ-PF-17** | Ubiquitous | The system shall cap performance benefits at the POH minimum values. Calculated distances shall never be shorter than the best-case (shortest distance) scenario defined in the POH tables, even if physical conditions (e.g., negative density altitude) suggest otherwise. | Approved | **P1** | "Minimum Distance Rule": Prevents unsafe, optimistic performance credit outside certified data. |
| **REQ-PF-18** | Ubiquitous | For Mode B (FSM 3/75), the system shall apply cumulative correction factors: +1% per 1°C above ISA, +10% per 1% upslope, surface factors (Grass Dry +20%, Grass Wet +30%, Soft Ground +50%). | Approved | **P2** | Standardizes correction logic following FSM 3/75 guidelines. |
| **REQ-PF-19** | Ubiquitous | The system shall distinguish between physical performance (what the aircraft can do) and operational performance (physical × safety factor) in all outputs. | Approved | **P2** | Transparency about the safety margins applied. |
| **REQ-PF-21** | Event-driven | The system shall calculate the crosswind component based on the latest METAR and the selected runway's heading, and verify it against the aircraft's POH Demonstrated Crosswind Limit. | Approved | **P2** | High-risk safety check for takeoff and landing. |
| **REQ-PF-22** | Ubiquitous | When using FSM 3/75 algorithmic mode, the system shall display a disclaimer that values are based on standard factors and real performance may vary. | Approved | **P2** | Legal disclaimer for non-manufacturer-specific calculations. |
| **REQ-PF-23** | Ubiquitous | The system shall calculate T/O and LDG distances by interpolating POH performance data based on pressure altitude, temperature, and weight. | Approved | **P1** | Core calculation logic for all modern types. |
| **REQ-PF-24** | Ubiquitous | The system shall apply FSM 3/75 surcharges based on selected surface conditions (e.g., +20% for dry grass, +50% for soft grass). | Approved | **P1** | Detailed adjustment for airfield conditions. |

---

## 4. Detailed Aircraft Data (AD)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-AD-01** | Ubiquitous | The system shall store for each aircraft: registration, manufacturer, model, ICAO type designator. | Approved | **P1** | Identification of the aircraft record. |
| **REQ-AD-02** | Ubiquitous | The system shall store fuel configuration: number of tanks, for each tank capacity, default fuel quantity, arm/moment, unusable fuel, fuel type and alternative fuel type (MoGas, AvGas 100LL, Jet A-1, AvGas UL91, Diesel). | Approved | **P1** | Fuel density differs by type (e.g., diesel vs. avgas). |
| **REQ-AD-03** | Ubiquitous | The system shall store default fuel quantity used when creating a new calculation. | Approved | **P2** | Ease of use for typical mission profiles (e.g., full tanks). |
| **REQ-AD-04** | Ubiquitous | The system shall store seat configuration options (1 seat, 2 seats tandem, 2 seats side-by-side, 2 rows). | Approved | **P1** | Correct arm location for different cabin layouts. |
| **REQ-AD-05** | Ubiquitous | The system shall allow optional baggage area selection (yes/no). | Approved | **P1** | Prevents payload entry into non-existent compartments. |
| **REQ-AD-06** | Ubiquitous | The system shall store empty mass, MTOM, cruise speed, fuel consumption (mass or volume) for cruise, take-off, landing, and standard reserve values (minutes, % extra, final reserve minutes). | Approved | **P1** | Basic planning parameters for time and fuel. |
| **REQ-AD-07** | Ubiquitous | The system shall support units: volume (L, gal), mass (kg, lb), speed (km/h, mph, kt), arm (m) or moment (kg·m). | Approved | **P1** | Flexibility for international documentation. |
| **REQ-AD-08** | Ubiquitous | The system shall store checklists associated with each aircraft. | Approved | **P2** | Integrated safety documentation. |
| **REQ-AD-09** | Ubiquitous | The system shall define load points: each with name, arm/moment, and type-specific defaults (tank data or seat/baggage default mass). | Approved | **P1** | Pre-defined loading stations for faster data entry. |
| **REQ-AD-10** | Ubiquitous | The system shall define flight envelope limits: graph type (arm or moment) and load range defined by points (arm/moment + mass). | Approved | **P1** | Geometric basis for CG validation. |
| **REQ-AD-11** | Ubiquitous | The system shall store cost per hour and indicate whether fuel cost is included. | Approved | **P3** | Cost management feature for flight preparation. |
| **REQ-AD-12** | Ubiquitous | Aircraft configurations (limits, arms) shall be stored as data, allowing new aircraft to be added without code changes. | Approved | **P1** | Sustainability and user-extensibility of the tool. |
| **REQ-AD-13** | Ubiquitous | The system shall store the reference datum definition (description and location) for each aircraft. | Approved | **P1** | Ensures pilot understands the origin of the coordinate system. |
| **REQ-AD-14** | Ubiquitous | The system shall support multiple weight categories (Normal, Utility, Aerobatic) with independent MTOM and CG limits for each. | Approved | **P1** | Essential for dual-certified aircraft (e.g., Klemm). |
| **REQ-AD-15** | Ubiquitous | The system shall store propeller type (fixed pitch, constant speed, variable pitch) as this affects performance calculations. | Approved | **P2** | Propeller efficiency changes the takeoff distance. |
| **REQ-AD-16** | Ubiquitous | The system shall define which fluids are included in empty mass (engine oil, coolant, hydraulic fluid, unusable fuel). | Approved | **P1** | Clarity on what "Empty" means per manufacturer. |
| **REQ-AD-17** | Ubiquitous | The system shall store base performance values (takeoff roll, landing roll, takeoff distance over 15m/50ft obstacle, landing distance over 15m/50ft obstacle) for aircraft using FSM 3/75 mode. | Approved | **P1** | Base data points needed for algorithmic corrections. |
| **REQ-AD-18** | Ubiquitous | The system shall store a calculation method flag per aircraft profile: "table" for POH lookup or "fsm_factors" for FSM 3/75 algorithmic mode. | Approved | **P1** | Directs the calculation engine per profile. |

---

## 5. Fuel & Endurance (FE)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-FE-01** | Event-driven | When a fuel type is selected, the system shall automatically calculate mass using the specific density of that fuel type (e.g., AvGas = 0.72 kg/L, Jet A-1 = 0.84 kg/L). | Approved | **P1** | Prevents weight errors due to fuel density differences (e.g. Jet A-1 vs. AvGas). |
| **REQ-FE-02** | Ubiquitous | The system shall calculate maximum flight time (Endurance) based on available fuel quantity and planned fuel flow rate. | Approved | **P1** | Essential for flight planning and legal reserves check. |
| **REQ-FE-03** | Unwanted Behavior | If the calculated flight time is less than the reserve time, the system shall display a warning. | Approved | **P1** | Safety alert for insufficient fuel for the planned mission + reserves. |
| **REQ-FE-04** | Ubiquitous | The system shall support sequential fuel burn logic for aircraft with multiple tanks with different arms (e.g., "First Tank II, then Tank I"). | Approved | **P2** | Critical for aircraft where fuel burn significantly shifts the CG. |

---

## 6. Airport Database & Runway Infrastructure (AP)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-AP-01** | Ubiquitous | The system shall provide an airport database containing: ICAO code, name, elevation, available runways, available takeoff/landing distances (TORA/LDA), surface types, and slopes. | Approved | **P1** | Efficient data loading for calculation. |
| **REQ-AP-02** | Event-driven | When the user enters an ICAO code, the system shall load the associated airport data and display a list of available runways. | Approved | **P1** | Streamlined workflow. |
| **REQ-AP-03** | Unwanted Behavior | If an ICAO code is not found in the database, the system shall allow the user to manually enter airport data for the current calculation. | Approved | **P1** | Pilot authority to fly to airfields not in the database. |
| **REQ-AP-04** | Ubiquitous | The database shall store only the base surface type; the user shall select the current condition (wet/dry) in the calculation tool. | Approved | **P2** | Conditions change; base type (asphalt/grass) is constant. |
| **REQ-AP-05** | Optional Feature | Where available, the system shall integrate with free data sources such as OpenAIP or OurAirports. | Approved | **P3** | Scalability of airport coverage. |
| **REQ-AP-06** | Event-driven | When a user enters an ICAO code, the system shall fetch Airport Metadata (Name, Elevation, Latitude/Longitude) from a verified open-source database. | Approved | **P2** | Automation of airport elevation for Pressure Alt calculation. |
| **REQ-AP-07** | Event-driven | When an airport is identified, the system shall retrieve a list of all Available Runways, including their Identifiers (e.g., 08/26) and Surface Type (Asphalt, Grass, etc.). | Approved | **P2** | Required for surface factor application. |
| **REQ-AP-08** | Ubiquitous | For each retrieved runway, the system shall store and display the published Declared Distances (TORA, TODA, ASDA, LDA). | Approved | **P1** | Essential for Go/No-Go comparison. |
| **REQ-AP-09** | Ubiquitous | The system shall retrieve the Magnetic Heading of each runway to calculate crosswind and headwind components. | Approved | **P2** | Automation of wind correction. |
| **REQ-AP-10** | State-driven | While external airport data is being used, the system shall clearly mark these values as "External/Unverified" until confirmed by the user. | Approved | **P2** | Safety: Verification against AIP/Jeppesen. |
| **REQ-AP-11** | Ubiquitous | The system shall allow the user to manually edit or override any retrieved runway dimension (e.g., due to NOTAMs/Construction). | Approved | **P1** | Pilot-in-command authority. |

---

## 7. User Interface Behavior (UI)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-UI-01** | Event-driven | When the user selects a manufacturer from the dropdown, the model dropdown shall be populated with models for that manufacturer. | Approved | **P2** | Context-aware selection. |
| **REQ-UI-02** | Event-driven | When "Other" is selected for manufacturer, a free-text field shall be enabled and "Other" shall be automatically selected for model. | Approved | **P1** | Support for rare or one-off aircraft. |
| **REQ-UI-03** | Event-driven | When a model is selected, the ICAO type designator field shall be auto-filled. | Approved | **P2** | Faster and more accurate identification. |
| **REQ-UI-04** | Event-driven | When an ICAO type designator is entered, the system shall auto-select the matching manufacturer and model, or present a list if multiple matches exist with a default selection. | Approved | **P2** | Bidirectional lookup for convenience. |
| **REQ-UI-05** | Ubiquitous | The system shall provide a "Favorites" or "Recent Airports" list for quick access to frequently used aerodromes. | Approved | **P3** | Typical mission profile shortcut. |
| **REQ-UI-06** | Ubiquitous | The system shall allow users to create and manage "Standard Passenger" profiles with preset weights to accelerate flight planning. | Approved | **P2** | Operational efficiency for frequent flyers. |
| **REQ-UI-10** | Ubiquitous | The UI shall provide immediate visual feedback (Green/Amber/Red) for all limit checks (Mass, CG, Runway Length, Crosswind) without requiring a "Calculate" button press. | Approved | **P1** | Safety check at high-frequency entry. |
| **REQ-UI-11** | Ubiquitous | Numeric inputs shall be constrained to realistic physical ranges (e.g., QNH 900-1100 hPa, Temperature -40 to +50°C) to prevent data entry errors. | Approved | **P1** | Prevents fat-finger errors during planning. |
| **REQ-UI-12** | Event-driven | When a certification category is changed, the system shall immediately recalculate all limits and update the display. | Approved | **P1** | Dynamic context switching (e.g., for aerobatics). |
| **REQ-UI-13** | Ubiquitous | The CG envelope chart shall render a "Trend Line" connecting the Take-off CG point and the Landing CG point to visualize the fuel burn shift. | Approved | **P1** | Provides intuitive feedback on how the aircraft balance changes during flight. |

---

## 8. Usability & Quality (UQ)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-UQ-01** | Ubiquitous | Data entry shall be optimized for both mobile devices with touch input and desktop devices with mouse and keyboard. | Approved | **P2** | Tool is meant for cockpit use (tablet) and office prep (desktop). |
| **REQ-UQ-02** | Ubiquitous | The graphical CG envelope display shall be fully readable on screens with a diagonal of 5 inches or larger. | Approved | **P2** | Usability on smartphone-sized devices. |
| **REQ-UQ-03** | Ubiquitous | All numerical calculations shall have a precision of at least two decimal places to minimize rounding errors in the chain (mass → arm → moment). | Approved | **P1** | Precision in moments prevents accumulation of material errors. |
| **REQ-UQ-04** | Ubiquitous | The system shall support independent units per aircraft (kg/lbs, L/gal) and convert them internally for calculation logic. | Approved | **P1** | Follows the aircraft's source documentation units. |

---

## 9. Cloud, Sync & Collaboration (SC)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-SC-01** | Ubiquitous | The system shall store all user data (Aircraft, Flight Plans) in a centralized cloud database. | Approved | **P3** | Shared data across devices and backup. |
| **REQ-SC-02** | Ubiquitous | The system shall provide a User Authentication system to secure and identify data ownership. | Approved | **P3** | Protects user-specific weight data and profiles. |
| **REQ-SC-03** | Ubiquitous | User Authentication shall support Google and Apple account login. | Approved | **P3** | Convenience and simplified account management. |
| **REQ-SC-04** | Event-driven | When a user is logged into the same account on different devices, the system shall synchronize data changes in real-time or upon next connectivity. | Approved | **P3** | seamless workflow between planning (office) and execution (cockpit). |
| **REQ-SC-05** | Ubiquitous | The system shall allow owners to share their aircraft database with specific other registered users via an invitation or "Organization" feature. | Approved | **P3** | Fleet management for flight clubs or shared owners. |

---

## 10. Weather & Meteorological Data (WX)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-WX-01** | Event-driven | When a user enters an ICAO airport code, the system shall fetch the current METAR and TAF from a public aviation weather API (e.g., CheckWX, NOAA). | Approved | **P2** | Fetches real-time environmental input for Performance. |
| **REQ-WX-02** | Event-driven | When METAR data is received, the system shall auto-populate Wind Direction/Speed, Temperature, and QNH fields based on the latest METAR. | Approved | **P2** | Automation reduces human entry errors. |
| **REQ-WX-03** | State-driven | While a METAR/TAF indicates any form of liquid precipitation (RA, DZ), the system shall default the Runway Surface to "Wet". | Approved | **P2** | Safety-first default based on weather detection. |
| **REQ-WX-04** | State-driven | While a METAR/TAF indicates heavy precipitation (+RA) or long-lasting precipitation (> 2h in TAF), the system shall default Grass runways to "Soft Ground". | Approved | **P2** | FSM 3/75 safety factor for saturated ground. |
| **REQ-WX-05** | Ubiquitous | The system shall allow the user to manually override any weather-inferred surface condition. | Approved | **P2** | Pilot-in-command has final authority over runway state. |
| **REQ-WX-06** | Event-driven | When a runway is selected, the system shall calculate and display the Wind Components (Headwind, Tailwind, Crosswind) based on the latest METAR wind data and the selected runway's heading. | Approved | **P2** | Automation of wind correction for performance and safety. |
---

## 11. Documentation & Export (DOC)

| Req-ID | Pattern | Requirement | Status | Priority | Rationale / Context |
|--------|---------|-------------|--------|----------|---------------------|
| **REQ-DOC-01** | Ubiquitous | The system shall provide an export function (PDF or optimized print view) that summarizes TOM, LM, CG positions, and all performance results in a compact "Digital Loadsheet." | Approved | **P3** | Legal documentation and cockpit accessibility. |

---

## Traceability to Tests (Gherkin)

| Req-ID | Gherkin Feature | Scenario Name | Status |
|--------|-----------------|---------------|--------|
| REQ-AC-04 | `aircraft-crud.feature` | Error when creating duplicate registration | Draft |
| REQ-MB-03 | `mass-balance.feature` | Warning when CG is out of limits | Draft |
| REQ-MB-04 | `mass-balance.feature` | Warning when weight exceeds MTOW | Draft |
| REQ-MB-06 | `mass-balance.feature` | CG validation using polygonal envelope | Draft |
| REQ-PF-12 | `performance.feature` | Bilinear interpolation of performance data | Draft |
| REQ-SC-02 | `authentication.feature` | User login with Google/Apple | Draft |
| REQ-WX-01 | `weather.feature` | Fetch METAR on ICAO entry | Draft |

---

## Traceability to Code

| Req-ID | Source File(s) | Status |
|--------|----------------|--------|
| REQ-MB-01 | `backend/app/services/mass_balance.py` | Draft |
| REQ-PF-01 | `backend/app/services/performance.py` | Draft |
| REQ-AD-01 | `backend/app/models/aircraft.py` | Draft |
| REQ-MB-06 | `backend/app/services/cg_validation.py` | Draft |
| REQ-PF-12 | `backend/app/services/interpolation.py` | Draft |
| REQ-SC-02 | `backend/app/auth/` | Draft |
| REQ-WX-01 | `backend/app/services/weather.py` | Draft |

---

## Developer Appendix: Linear Extrapolation & Minimum Distance Logic (REQ-PF-13, REQ-PF-17)

Implementation must distinguish between "Negative" (optimistic) and "Positive" (worse) trends relative to performance.

```python
# 1. Determine Trend Direction
#    - If X_target > X_max_poh (Worse: High Temp/Weight/Alt): 
#      Follow Positive Extrapolation logic + 20% Penalty (REQ-PF-14).
#    - If X_target < X_min_poh (Better: Low Temp/Alt): 
#      Follow Negative Extrapolation logic -> APPLY MINIMUM DISTANCE RULE.

# 2. Positive Extrapolation (Worse Case)
#    - m = (V_max_poh - V_previous) / (X_max_poh - X_previous)
#    - V_ext = V_max_poh + m * (X_target - X_max_poh)
#    - V_final = V_ext * 1.20 (REQ-PF-14)

# 3. Negative Extrapolation (Better Case - REQ-PF-17)
#    - Logic: Never allow a result better than the best POH data point.
#    - V_final = V_min_poh (Clip/Floor to nearest boundary value)

# SUMMARY MATH:
# Result = MAX(POH_Boundary_Value, Extrapolated_Value) for distance increases.
# Result = POH_Boundary_Value for potential distance decreases below minimums.

# CRITICAL: 
# If X_target > X_boundary * 1.10 (Positive Buffer), raise BoundsExceededException (REQ-PF-13).
# If X_target < X_boundary (Negative), no buffer limit applies as we cap at V_min_poh anyway.
```
