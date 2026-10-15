# MMA3001-Project
Unit Project's repository for MMA3001


## 🤖 AI Acknowledgement for Project README

This section details the use of Artificial Intelligence (AI) tools in the development of this project, adhering to principles of transparency, accountability, and ethical data handling.

### **1. AI Tools Utilised**

*   **Google Gemini 2.5 (LLM)**: Accessed from July 2024 to August 2024.
    *   *Known biases*: As a large language model, Gemini may reflect biases present in its training data, and outputs were critically reviewed for fairness and accuracy.
*   **GitHub Copilot**: Integrated into the development environment (VS Code) during the project timeline (July-August 2024).
    *   *Known biases*: Copilot's suggestions are based on patterns in publicly available code, which may not always represent best practices or ethical considerations. All suggestions were reviewed and adapted.

### **2. How AI Was Used**

AI tools were employed to assist with various aspects of the project, specifically:

*   **Code Generation & Refinement**: Google Gemini 2.5 was used to generate initial boilerplate code for several functions and classes. GitHub Copilot provided inline code suggestions for syntax completion, common patterns, and small utility functions. All AI-generated code was thoroughly reviewed, debugged, and significantly modified or expanded to fit project requirements and coding standards.
*   **Documentation & Explanation**: Gemini 2.5 assisted in drafting initial versions of README sections, comments, and explanatory text for complex algorithms. These drafts were subsequently edited, clarified, and personalised to ensure accuracy and reflect the project's specific context.
*   **Problem Solving & Ideation**: AI tools were occasionally used to explore different approaches to specific programming challenges or to understand unfamiliar library functions. The insights gained were then independently verified and implemented.

### **3. Human Oversight and Responsibility**

I maintained full human oversight throughout the project lifecycle. All AI-generated content, whether code or text, underwent rigorous validation and verification. This included:

*   **Manual Review**: Every line of AI-generated code was manually inspected for correctness, efficiency, security vulnerabilities, and adherence to project conventions.
*   **Testing**: All components, including those with AI-assisted development, were thoroughly tested to confirm functionality and accuracy.
*   **Critical Analysis**: AI outputs were treated as suggestions, not definitive solutions. I assumed full responsibility for the accuracy, reliability, and ethical implications of all final project deliverables.
*   **Data Security**: No sensitive, proprietary, or confidential project data was ever inputted into public AI models to ensure data privacy and prevent intellectual property leakage.

### **4. Ethical Commitment**

This project adheres to ethical AI use, recognising AI as a powerful tool that augments human capability. The application of AI was transparent, documented, and guided by informed professional judgment, ensuring that its contribution is responsible and aligned with professional engineering standards.

## Project structure

- `data/` — local raw CSV inputs. Contents are ignored by Git; keep `data/.gitkeep` so the folder exists after cloning.
- `derived/` — generated preprocessing datasets, validation results, and reports.
- `notebooks/` — exploratory and analysis notebooks.
- `test/` — automated or focused test files.
- `source/` — reusable project code.
- `examples/` — example inputs or usage material.
- `docs/` — project and preprocessing documentation.

Run `pre-Processing.ipynb` from the repository root. Run the preprocessing cell first, then work through the occupancy investigation audit and analysis cells. The investigation examines occupancy across academic-semester phases, week-to-week changes, and within-day peaks; its reports are written under `derived/occupancy_investigation/reports/`. The notebook selects the newest complete environmental and occupancy CSV exports in `data/`. The previous semester-cycle investigation is preserved in `notebooks/archive/semester_cycle_occupancy_investigation.ipynb`, with its historical reports under `derived/archive/semester_cycle_occupancy_investigation/reports/`. The earlier environmental-occupancy comparison remains exploratory: environmental measurements currently overlap occupancy only from May to mid-June 2024, and the sensor-to-room mapping is unverified.
See [the preprocessing documentation](docs/preprocessing.md) for the input contract, processing decisions, outputs, validation, benchmarks, assumptions, and limitations.


## 🤖 AI Acknowledgement for Project README

This section details the use of Artificial Intelligence (AI) tools in the development of this project, adhering to principles of transparency, accountability, and ethical data handling.

### **1. AI Tools Utilised**

*   **Google Gemini 2.5 (LLM)**: Accessed from July 2024 to August 2024.
    *   *Known biases*: As a large language model, Gemini may reflect biases present in its training data, and outputs were critically reviewed for fairness and accuracy.
*   **GitHub Copilot**: Integrated into the development environment (VS Code) during the project timeline (July-August 2024).
    *   *Known biases*: Copilot's suggestions are based on patterns in publicly available code, which may not always represent best practices or ethical considerations. All suggestions were reviewed and adapted.

### **2. How AI Was Used**

AI tools were employed to assist with various aspects of the project, specifically:

*   **Code Generation & Refinement**: Google Gemini 2.5 was used to generate initial boilerplate code for several functions and classes. GitHub Copilot provided inline code suggestions for syntax completion, common patterns, and small utility functions. All AI-generated code was thoroughly reviewed, debugged, and significantly modified or expanded to fit project requirements and coding standards.
*   **Documentation & Explanation**: Gemini 2.5 assisted in drafting initial versions of README sections, comments, and explanatory text for complex algorithms. These drafts were subsequently edited, clarified, and personalised to ensure accuracy and reflect the project's specific context.
*   **Problem Solving & Ideation**: AI tools were occasionally used to explore different approaches to specific programming challenges or to understand unfamiliar library functions. The insights gained were then independently verified and implemented.

### **3. Human Oversight and Responsibility**

I maintained full human oversight throughout the project lifecycle. All AI-generated content, whether code or text, underwent rigorous validation and verification. This included:

*   **Manual Review**: Every line of AI-generated code was manually inspected for correctness, efficiency, security vulnerabilities, and adherence to project conventions.
*   **Testing**: All components, including those with AI-assisted development, were thoroughly tested to confirm functionality and accuracy.
*   **Critical Analysis**: AI outputs were treated as suggestions, not definitive solutions. I assumed full responsibility for the accuracy, reliability, and ethical implications of all final project deliverables.
*   **Data Security**: No sensitive, proprietary, or confidential project data was ever inputted into public AI models to ensure data privacy and prevent intellectual property leakage.

### **4. Ethical Commitment**

This project adheres to ethical AI use, recognising AI as a powerful tool that augments human capability. The application of AI was transparent, documented, and guided by informed professional judgment, ensuring that its contribution is responsible and aligned with professional engineering standards.
