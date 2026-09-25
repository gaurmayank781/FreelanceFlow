# 🛠️ Python Automation Toolkit

> **A practical, all-in-one automation platform built with Python and Streamlit — automate repetitive file, data, reporting, and email workflows through a clean web interface.**

**Python Automation Toolkit** transforms common manual tasks into simple, repeatable workflows. Instead of running individual Python scripts from the command line, users can upload their files, configure the required options, run an automation, and download the processed result directly from the browser.

Built with **Python + Streamlit**, the application provides a centralized interface for multiple productivity-focused automation tools while keeping each tool's core logic modular and reusable.

---

## ✨ Features

The toolkit currently includes **7 automation modules**:

| Tool                          | Description                                                                                        |
| ----------------------------- | -------------------------------------------------------------------------------------------------- |
| 📁 **Bulk Renamer**           | Rename multiple files using configurable numbered patterns                                         |
| 🗂️ **Folder Organizer**      | Automatically organize files into folders based on file type                                       |
| 📊 **CSV Merger**             | Combine multiple CSV files, including files with different column structures                       |
| 🧹 **Data Cleaner**           | Clean and standardize datasets by normalizing columns, removing whitespace, blanks, and duplicates |
| 📈 **Excel Report Generator** | Convert CSV datasets into professionally formatted multi-sheet Excel reports                       |
| 📄 **PDF Report Generator**   | Generate structured PDF reports from CSV data                                                      |
| ✉️ **Email Automation**       | Send personalized bulk emails using CSV data and customizable templates                            |

---

## 🎯 Why This Project?

Many everyday workflows involve repetitive tasks such as:

* Renaming hundreds of files
* Organizing downloaded documents
* Combining multiple CSV datasets
* Cleaning inconsistent data
* Creating recurring Excel reports
* Generating PDF reports
* Sending personalized emails

These tasks are individually simple but become time-consuming when performed manually.

**Python Automation Toolkit** provides a single interface for automating these workflows without requiring users to interact with the command line or write Python code.

---

## 🖥️ Application Workflow

```text
                 ┌──────────────────────────┐
                 │      Streamlit UI        │
                 │      Web Interface       │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │      Select Automation   │
                 └────────────┬─────────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
       File Automation   Data Automation   Reporting
             │                │                │
             ▼                ▼                ▼
       Rename / Organize  Clean / Merge   Excel / PDF
                              │
                              ▼
                       Email Automation
                              │
                              ▼
                 ┌──────────────────────────┐
                 │   Process in Workspace   │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │   Download Result        │
                 └──────────────────────────┘
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/gaurmayank781/FreelanceFlow.git
cd FreelanceFlow
```

### 2. Create a Virtual Environment

Using Python's built-in virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the Application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## 🧰 How to Use

### Step 1 — Launch the application

Start the Streamlit server:

```bash
streamlit run app.py
```

### Step 2 — Select a tool

Choose an automation from the homepage or sidebar.

### Step 3 — Upload your files

Upload the required CSV, Excel, PDF, or other supported files.

### Step 4 — Configure the automation

Select the required options according to the selected tool.

### Step 5 — Run the automation

Click the appropriate action button.

### Step 6 — Download the result

Once processing is complete, download the generated output directly from the application.

---

# 📁 Project Structure

```text
PythonAutomationToolkit/
│
├── app.py
├── requirements.txt
├── webapp_utils.py
│
├── pages/
│   ├── bulk_renamer.py
│   ├── folder_organizer.py
│   ├── csv_merger.py
│   ├── data_cleaner.py
│   ├── excel_report.py
│   ├── pdf_report.py
│   └── email_automation.py
│
├── bulk_renamer/
│   ├── ...
│   └── tests/
│
├── folder_organizer/
│   ├── ...
│   └── tests/
│
├── csv_merger/
│   ├── ...
│   └── tests/
│
├── data_cleaner/
│   ├── ...
│   └── tests/
│
├── excel_automation/
│   ├── ...
│   └── tests/
│
├── pdf_generator/
│   ├── ...
│   └── tests/
│
└── email_automation/
    ├── ...
    └── tests/
```

### Architecture

The application follows a modular architecture where the **Streamlit interface acts as the presentation layer**, while each automation maintains its own independent implementation.

```text
Streamlit Application
        │
        ├── UI / User Input
        │
        ├── File Handling
        │
        ├── Automation Modules
        │       ├── Bulk Renamer
        │       ├── Folder Organizer
        │       ├── CSV Merger
        │       ├── Data Cleaner
        │       ├── Excel Generator
        │       ├── PDF Generator
        │       └── Email Automation
        │
        └── Output / Download
```

This separation makes individual tools easier to maintain, test, and extend.

---

# 🔐 Data & Security

The application is designed to minimize unnecessary persistence of uploaded data.

### Temporary Processing

Uploaded files are processed inside a temporary workspace.

```text
Upload
   ↓
Temporary Workspace
   ↓
Automation
   ↓
Generated Result
   ↓
Download
   ↓
Temporary Files Cleaned
```

Files are not intentionally stored as permanent application data.

### Email Automation Security

The email automation module includes several safeguards:

* **Dry-run mode is enabled by default**
* Actual sending requires explicit user confirmation
* SMTP credentials are used only for the current execution
* Credentials are not written to application files
* Credentials are not included in application logs

### Gmail

For Gmail SMTP authentication, use a **Google App Password** rather than your normal Google account password.

---

# 🧪 Testing

Each automation module can maintain its own test suite.

Run tests for an individual module:

```bash
pytest bulk_renamer
```

Or run the complete test suite:

```bash
pytest
```

Testing individual modules independently helps ensure that changes to the Streamlit interface do not unnecessarily affect the underlying automation logic.

---

# 🛠️ Tech Stack

| Technology          | Purpose                               |
| ------------------- | ------------------------------------- |
| **Python**          | Core application and automation logic |
| **Streamlit**       | Web-based user interface              |
| **Pandas**          | Data processing and CSV manipulation  |
| **OpenPyXL**        | Excel report generation               |
| **ReportLab**       | PDF generation                        |
| **Pytest**          | Automated testing                     |
| **SMTP**            | Email delivery                        |
| **Temporary Files** | Isolated file processing              |

---

# 📊 Use Cases

This toolkit can be useful for:

### 👨‍💻 Developers

Quickly automate repetitive development and file-management tasks.

### 📊 Data Analysts

Clean, merge, transform, and generate reports from CSV datasets.

### 💼 Freelancers

Automate repetitive client workflows without building separate scripts for every task.

### 🏢 Small Businesses

Simplify document organization, reporting, and routine email workflows.

### 🎓 Students & Researchers

Process datasets and generate structured reports with minimal manual work.

---

# 🔌 Command-Line Compatibility

The project was originally designed around individual command-line automation tools.

The Streamlit application provides a web interface **without removing the original automation logic**.

This means the underlying modules can continue to be used independently from the web application.

For example:

```bash
python bulk_renamer/main.py
```

Individual modules may have their own CLI instructions and README files.

---

# ☁️ Deployment

The application can be deployed to platforms that support Streamlit applications.

For example:

* Streamlit Community Cloud
* Local development environments
* Python-compatible cloud platforms
* Self-hosted environments

For local deployment:

```bash
streamlit run app.py
```

For Streamlit Community Cloud, connect the GitHub repository and configure the application entry point as:

```text
app.py
```

---

# 🔮 Future Improvements

Potential future improvements include:

* [ ] Drag-and-drop file management
* [ ] More advanced data-cleaning rules
* [ ] Custom Excel report templates
* [ ] Additional PDF layouts
* [ ] Scheduled automations
* [ ] Automation history
* [ ] User authentication
* [ ] Persistent project/workspace management
* [ ] Advanced email campaign analytics
* [ ] Task scheduling and recurring workflows
* [ ] Cloud storage integrations
* [ ] More file-format support
* [ ] Improved logging and execution reports

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

### Fork the repository

```bash
git fork
```

### Create a feature branch

```bash
git checkout -b feature/new-automation
```

### Commit your changes

```bash
git commit -m "Add new automation module"
```

### Push the branch

```bash
git push origin feature/new-automation
```

Then open a Pull Request.

---

# ⚠️ Disclaimer

This project is intended for **automation, productivity, and educational purposes**.

Users are responsible for reviewing generated files, configuring external services correctly, and ensuring that their use of email automation and uploaded data complies with applicable policies and regulations.

---

# 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

# 👨‍💻 Author

**Mayank Gour**

Python Developer • Data Scientist • Automation & Analytics

Building practical software solutions around **Python, automation, data processing, analytics, and AI-powered workflows**.

---

## ⭐ Support the Project

If you find this project useful:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐛 Report bugs
* 💡 Suggest new automation ideas
* 🤝 Contribute improvements

---

<p align="center">

**Built with Python 🐍 and Streamlit ⚡**

</p>
