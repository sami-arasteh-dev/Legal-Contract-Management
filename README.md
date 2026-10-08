# Smart Legal Contract Management & Generation System

A Flask-based web application for AI-assisted contract drafting, analysis, archival, and export. Designed for Persian legal standards with A4-optimized print output, multi-format document parsing, and a centralized local database.

## 📋 Features
- **AI Contract Generation:** Structured, legally formatted contract creation based on user inputs.
- **Document Parsing:** Extracts and paginates content from `.pdf`, `.doc`, `.docx`, and `.html` files.
- **Legal Analysis & Correction:** AI-powered risk assessment, clause fixing, and custom prompt execution.
- **Contract Archive:** SQLite-backed CRUD operations with reference numbering, timestamps, and live search.
- **Print-Ready Output:** Enterprise-grade inline CSS and `@media print` rules for flawless A4 export.
- **Sample Library:** Browse and load pre-stored contract templates from the `sample_contracts` directory.
- **RTL & Persian UI:** Fully right-to-left interface with Vazirmatn font and Persian date display.

## 🏗 Architecture & Tech Stack
| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.x, Flask |
| **Database** | SQLite (`contracts.db`) |
| **AI/LLM** | OpenAI Python SDK (custom base URL: `https://api.gapgpt.app/v1`) |
| **Model** | `gemini-3-pro-preview` |
| **Document Processing** | `PyPDF2`, `python-docx`, `BeautifulSoup4` |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, RTL layout |
| **Deployment** | Standalone Flask server (`host='0.0.0.0', port=5566`) |

## 📦 Prerequisites
- Python 3.8 or higher
- `pip` package manager
- Valid API key for an OpenAI-compatible endpoint
- Internet connection (for LLM API calls)

## 🛠 Installation & Setup
1. Clone or extract the project directory.
2. Install dependencies:
   ```bash
   pip install flask openai PyPDF2 python-docx beautifulsoup4
   ```
3. Ensure the following directories exist (they are auto-created on first run):
   - `uploads/`
   - `sample_contracts/`
4. Launch the application:
   ```bash
   python app.py
   ```
5. Access the UI at `http://localhost:5566`.

## ⚙️ Configuration
- **LLM Endpoint & Key:** Configured in `app.py`:
  ```python
  client = OpenAI(
      base_url="https://api.gapgpt.app/v1",
      api_key="sk-..."
  )
  ```
  *Note: The API key is currently hardcoded. For production, migrate to environment variables.*
- **Database:** Auto-initializes on startup. Schema includes `id`, `title`, `party_a`, `party_b`, `content`, `raw_data`, `created_at`, `ref_number`.
- **Date Handling:** Persian date is currently hardcoded (`۱۴۰۵/۰۴/۰۲`). Consider integrating `jdatetime` for dynamic localization.

## 📖 Usage
### 1. Generate Contract
- Navigate to **Tab 1: تنظیم قرارداد جدید**.
- Fill in contract type, subject, parties, amount, duration, obligations, clauses, and special notes.
- Click **تولید نسخه اینترپرایز قرارداد**. The system returns a formatted HTML contract with a unique reference number.
- Use **ذخیره در سیستم** to persist the contract, or **چاپ با فرمت A4** to trigger browser print.

### 2. Manage Archives
- Navigate to **Tab 2: آرشیو و مدیریت**.
- Use the search bar to filter contracts by reference number, subject, or parties.
- Click **نمایش** to load a contract into the generator, or **حذف** to remove it.

### 3. Analyze & Upload Documents
- Navigate to **Tab 3: تحلیل و قراردادهای نمونه**.
- Upload a `.pdf`, `.docx`, or `.html` file, or select a file from the sample library.
- Pages are extracted and displayed in a sidebar. Click a page to edit/view in the main editor.
- Use AI tools:
  - **تحلیل ریسک‌ها:** Risk assessment report.
  - **اصلاح حقوقی:** Clause correction & formatting.
  - **اعمال جادو:** Custom LLM prompt execution.

## 📁 Project Structure
```
project/
├── app.py                  # Flask backend, routes, DB, LLM integration
├── index.html              # Frontend UI, CSS, JS, print styles
├── uploads/                # Temporary storage for uploaded files (auto-cleaned)
├── sample_contracts/       # Directory for pre-loaded .doc/.docx templates
└── contracts.db            # SQLite database (auto-generated)
```

## 🔌 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves `index.html` |
| `POST` | `/api/generate` | Generates contract HTML + reference number |
| `GET` | `/api/contracts` | Retrieves all stored contracts |
| `POST` | `/api/contracts` | Saves a new/updated contract |
| `GET` | `/api/contracts/<id>` | Retrieves a single contract |
| `DELETE` | `/api/contracts/<id>` | Deletes a contract |
| `GET` | `/api/samples` | Lists available sample files |
| `GET` | `/api/samples/<filename>` | Extracts paginated content from a sample |
| `POST` | `/api/upload` | Uploads & parses PDF/DOCX/HTML |
| `POST` | `/api/analyze` | Sends content to LLM for analysis/correction |

## ⚠️ Technical Notes
- **Synchronous LLM Calls:** The `ask_llm()` function blocks until the API responds. Consider async routing for high-concurrency environments.
- **File Cleanup:** Uploaded files are deleted immediately after text extraction to prevent storage bloat.
- **Inline CSS:** Contract styling uses inline styles for maximum print compatibility. External stylesheets are not injected into the generated HTML.
- **Security:** No authentication or input sanitization is implemented. Not recommended for public-facing deployment without additional security layers.
- **Model Routing:** Uses an OpenAI-compatible SDK but routes to a custom endpoint (`gapgpt.app`). Compatible with any OpenAI-style API.

## 🔮 Development Recommendations
- Migrate the hardcoded API key to `os.environ` or a `.env` file.
- Replace the static Persian date with `jdatetime` for accurate calendar conversion.
- Implement user authentication and role-based access control.
- Add pagination and indexing to the SQLite database for large contract archives.
- Containerize with Docker for reproducible deployments.

## 📄 License
License not specified in the provided files. Default to MIT for open-source distribution unless otherwise stated.

---
*Documentation generated based on actual project files. No external assumptions or fabricated capabilities included.*
