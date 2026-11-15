# Ask Your Floor Plan
## An Evidence-First AI-Powered Floor Plan Question Answering System

Built for the Ashian Tech Intern Take-Home Assignment.

Ask natural-language questions about floor plans and receive answers grounded in structured SQLite records, SQL queries, and supporting database evidence.

## 1. Project Overview

This project converts floor-plan images and segmentation masks into structured component records. It uses image processing, heuristic semantic mapping, SQLite, and a Gemini-assisted question-answering pipeline.

A Streamlit interface allows users to ask questions about rooms, doors, windows, walls, and floor-plan statistics.

The system is designed to retrieve answers from stored data rather than inventing information.

## 2. Key Features

- Loads floor-plan images and segmentation masks.
- Uses OpenCV connected-component extraction.
- Assigns candidate semantic labels using colour and geometric heuristics.
- Stores extracted elements and relationships in SQLite.
- Accepts natural-language questions.
- Uses Gemini to generate SQL and explain query results.
- Restricts SQL execution to read-only queries and permitted tables.
- Displays answers, SQL queries, and database evidence.
- Provides deterministic retrieval as a fallback.
- Declines unsupported questions when the available data cannot answer them.
- Includes a Streamlit interface and automated evaluation tests.

## 3. Technology Stack

| Category | Technologies |
|---|---|
| Language | Python 3.11 |
| Image Processing | OpenCV, NumPy |
| Database | SQLite |
| LLM | Google Gemini 2.5 Flash |
| Interface | Streamlit |
| Query Language | SQL |
| Testing | pytest |

## 4. System Architecture

```text
Floor Plan Images and Masks
             |
             v
      Image Processing
             |
             v
 Connected Component Extraction
             |
             v
       Semantic Mapping
             |
             v
        SQLite Database
             |
             v
       User Question
             |
             v
     Gemini SQL Generation
             |
             v
    Read-Only SQL Validation
             |
             v
       SQLite Execution
             |
             v
      Database Evidence
             |
             v
     Answer Generation
             |
             v
      Streamlit Interface
```

If Gemini is unavailable or generated SQL cannot be executed, supported questions can use the deterministic retrieval engine.

## 5. Project Structure

```text
ashian-floorplan-ai/
|
|-- app.py
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- .env
|
|-- dataset/
|   |-- images/
|   |-- masks/
|
|-- src/
|   |-- assistant.py
|   |-- cli.py
|   |-- gemini_client.py
|   |-- retrieval_engine.py
|   |-- semantic_mapping.py
|   |-- build_dataset.py
|   |-- extract_components.py
|   |-- update_database.py
|   |-- visualize_extraction.py
|   |-- verify_dataset.py
|   |-- verify_semantics.py
|
|-- tests/
|   |-- test_evaluation.py
|   |-- test_retrieval.py
|
|-- outputs/
    |-- floorplan.db
    |-- evaluation_report.md
    |-- semantic_mapping_report.md
    |-- improved_overlays/
    |-- room_contours/
    |-- visualizations/
```

Additional helper scripts and generated files are also included in the project.

## 6. Database Design

The SQLite database contains the following main tables:

### plans
Stores floor-plan identifiers and references to source images and masks.

### elements
Stores extracted components, including:
- Element ID and plan ID
- Element type
- Class ID and colour
- Pixel area
- Bounding-box coordinates
- Width and height
- Centroid coordinates

### element_links
Stores candidate relationships between extracted elements, including room-to-window relationships.

### semantic_mappings
Stores per-plan semantic colour mappings and the method used.

### Other tables
The database also contains `components` and `floorplan_features` tables used by the extraction and retrieval workflows.

## 7. Installation and Setup

### Prerequisites
- Python 3.11
- pip
- A Google Gemini API key

### Step 1: Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ashian-floorplan-ai
```

### Step 2: Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Never commit your actual API key.

### Step 5: Run the application

```bash
streamlit run app.py
```

The application will display a local URL in the terminal. Open it in your browser.

### Step 6: Run automated tests

```bash
python -m pytest -v
```

The existing evaluation and retrieval tests are included in the `tests` directory.

## 8. Example Questions

| Question | Database Result |
|---|---|
| How many rooms does plan 12 have? | 12 rooms |
| What is the largest room in plan 7? | Room ID 327, area 203711 pixels |
| Which plans have more than 3 doors? | 99 plans |
| Which room in plan 4 has no windows? | Room IDs 174, 177, 179 |
| What is the average number of rooms across all plans? | 8.8 |

The application displays the generated SQL and supporting database evidence so users can inspect how an answer was obtained.

### Unsupported Questions

Example:

Question: What is the rent for plan 1?

Response: Rent information is not available in the database.

The system should not invent an answer when the required information is unavailable.

## 9. Evaluation

Part 3A: Evaluation was selected for this assignment.

The evaluation suite contains 20 questions with expected database results.

Current test results:

- Passed: 20/20
- Evaluation accuracy: 100%
- Failed: 0

The complete results are available in:

`outputs/evaluation_report.md`

The project also includes automated retrieval tests.

Important: This evaluation measures database question-answer correctness against reference queries. It does not measure the accuracy of the computer-vision segmentation or establish that semantic labels are human-verified ground truth.

## 10. Limitations

- Semantic class assignments are inferred using colour and geometric heuristics.
- Segmentation-mask colours are not independently verified against human-annotated labels.
- Connected components do not always correspond to individual architectural rooms.
- Some room boundaries may merge adjacent spaces or extend across walls.
- Element-to-room relationships are approximate and may contain errors.
- Areas are measured in pixels, not physical square metres.
- Results depend on the quality and consistency of the supplied masks.
- The evaluation validates database retrieval, not the underlying visual extraction accuracy.

## 11. Future Improvements

- Use a verified class palette or manually annotated samples.
- Improve room separation using wall-aware segmentation and contour analysis.
- Validate extraction against manually labelled ground truth.
- Improve spatial relationships between rooms, doors, and windows.
- Add confidence scores for extracted elements.
- Extend the evaluation suite with visual extraction metrics.
- Support uploading and processing new floor plans.

## 12. Security

- API keys are stored in environment variables.
- Generated SQL is validated before execution.
- Database access for assistant queries is restricted to read-only operations and permitted tables.
- API credentials must not be included in public repositories.


Project: Ask Your Floor Plan
Focus: Computer Vision, Data Extraction, SQLite, SQL, LLM Integration, and Evaluation.



