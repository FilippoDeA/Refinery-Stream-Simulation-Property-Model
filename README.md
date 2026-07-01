# 🛢️ Quantitative Refinery Blending & Commercial Arbitrage

**Bridging Process Engineering, Linear Programming, and Physical Commodities Trading**

Welcome to the Quantitative Refinery Blending repository. This project demonstrates a full-stack approach to refinery operations, transitioning from raw thermodynamic process simulation to a live, trader-facing commercial execution dashboard. 

To mirror real-world energy trading environments, this project is divided into two distinct operational files: an **Engineering Sandbox** (for process modeling and algorithm development) and a **Commercial Execution Desk** (for live supply-chain management and arbitrage capturing).

---

## 📂 1. The Engineering Sandbox (`Blending_Model_Notebook.ipynb`)

### 🧠 Explanation: The "Under the Hood" Mathematical Engine
This Jupyter Notebook serves as the quantitative research and development environment. It is designed to prove the underlying chemical and mathematical models before they are deployed to a trading floor. 
* **Process Simulation Bridge:** Uses the `pythonnet` library to establish a headless connection to **DWSIM**, extracting live steady-state thermodynamic data from simulated physical streams.
* **Non-Linear to Linear Transformation:** Simulates a LIMS database query and applies industry-standard power laws ($RVP^{1.25}$) to linearize non-linear vapor pressure curves.
* **SciPy Optimization:** Constructs a rigid Linear Programming (LP) matrix to minimize the volumetric cost of a USGC Regular 87 blend using the `highs` dual-simplex algorithm.

### ⚙️ Instructions: How to Run the Notebook
1. **Prerequisites:** You must have [DWSIM](https://dwsim.org/) installed on your local machine.
2. **Path Configuration:** Open the notebook and navigate to **Section 1**. Update the `dwsim_path` and `flowsheet_path` variables to point directly to your local DWSIM installation folder and the downloaded `.dwxmz` flowsheet.
3. **Execution:** Run the notebook cell by cell. Watch the terminal output as it verifies the DWSIM bridge, scrapes live proxy prices via `yfinance`, and calculates the theoretical optimal blend matrix.

---

## 💻 2. The Commercial Execution Desk (`app.py`)

### 📊 Explanation: The Trader-Facing Web Application
Traders and operations managers do not run Jupyter Notebooks—they use interactive dashboards. `app.py` wraps the core LP mathematical engine into a **Streamlit** web application, adding critical physical supply chain constraints and risk management tools.
* **Physical Tank Logistics:** Introduces dynamic bounding based on current tank farm inventory and target batch sizes, preventing the algorithm from suggesting physically impossible blends.
* **Shadow Pricing (Sensitivity Analysis):** Extracts dual-values from the SciPy solver to tell the operator exactly how much profit is being choked by specific physical bottlenecks (e.g., maxed-out tanks or rigid RVP specs).
* **Terminal-Style UI:** Provides sliders, metric cards, and a one-click "EXECUTE" execution signal based on live Net Profit Margins (accounting for variable OPEX).

### 🚀 Instructions: How to Run the Dashboard
1. Open your terminal or command prompt.
2. Navigate (`cd`) to the directory where `app.py` is saved.
3. Execute the following command:

```bash
   streamlit run app.py
```

4. A local server will start, and your default web browser will automatically open to http://localhost:8501.
5. Interact: Adjust the "Current Tank Inventories" sliders on the left sidebar to simulate a supply chain bottleneck (e.g., artificially crash your Reformate supply), hit the Execute button, and watch the algorithm instantly pivot to capture the next best margin.

---

## 🛠️ 3. Installation & Setup (For Both Files)
To run this repository locally, you will need Python 3.8+ and the following specific libraries.

Clone the repository and install the dependencies via pip:
```bash
   git clone https://github.com/FilippoDeA/Refinery-Stream-Simulation-Property-Model
   cd <repository-folder>
   pip install scipy pandas numpy yfinance pythonnet streamlit
```

---

## 📝 4. Included Data Files

- `refinery_lims_data.csv`: A mock Laboratory Information Management System dataset containing empirical stream assays (RON, RVP).

- `Blending_Model.dwxmz`: The baseline DWSIM chemical flowsheet used by the Notebook bridge.
