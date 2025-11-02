# CV Evaluation System 🚀

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Ready-green.svg)](https://fastapi.tiangolo.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Powered-orange.svg)](https://crewai.com/)

An intelligent CV evaluation system powered by CrewAI framework, specifically designed for **Immigration applications**. This system uses a multi-agent AI approach to provide comprehensive, objective evaluations of candidate credentials and their alignment with U.S. strategic interests.

## ✨ Key Features

- **🤖 Multi-Agent AI System**: Three specialized AI agents work collaboratively to evaluate CVs
- **📊 Dual Evaluation Matrix**: Assesses both personal credentials and national importance
- **⚖️ Weighted Scoring**: Balanced evaluation (60% credentials + 40% national importance)
- **🔄 Automated Workflow**: Seamless integration with MongoDB for data management
- **🚀 RESTful API**: Easy-to-use FastAPI endpoints for evaluation requests

## 🏗️ AI Agent Architecture

```
┌─────────────────────────────────────┐
│         Lead Adjudicator            │
│    (Final Synthesis & Decision)     │
└─────┬───────────────────────────────┘
      │
┌─────┴───────────────────────────────┐
│  Credentials    │  National Importance│
│    Analyst      │      Analyst        │
│   (Academic     │   (Policy Focus)    │
│  Credentials)   │                     │
└─────────────────┴─────────────────────┘
```

## 📋 Evaluation Criteria

### Credentials Scoring (1-10)
- **High (8-10)**: PhD from reputable university, top-tier publications, high citations, major awards
- **Medium (5-7)**: Master's/PhD, solid publication record, moderate citations, some awards
- **Low (1-4)**: Basic advanced degree, minimal publications, low citations

### National Importance Scoring (1-10)
- **High (8-10)**: AI development, semiconductors, national security, cancer research, clean energy
- **Medium (5-7)**: General healthcare, economic growth, education impact
- **Low (1-4)**: Abstract or indirect benefits to U.S. interests

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- MongoDB instance
- Required dependencies (see `pyproject.toml`)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cv-evaluation
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Configure MongoDB**
   Update the connection details in `main.py`:
   ```python
   MONGO_URI = "your-mongodb-uri"
   DB_NAME = "your-database"
   INPUT_COLLECTION = "input-collection-name"
   OUTPUT_COLLECTION = "output-collection-name"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 🔧 API Usage

### Evaluate a CV

**Endpoint**: `POST /run-cv-evaluation/{document_id}`

**Request**:
```bash
curl -X POST "http://localhost:8000/run-cv-evaluation/507f1f77bcf86cd799439011" \
     -H "Content-Type: application/json"
```

**Response**:
```json
{
  "message": "Crew executed successfully!",
  "output": {
    "_id": "507f1f77bcf86cd799439011",
    "status": "completed",
    "results": {
      "task_1": "Credentials Score: 8/10\nStrong academic background with PhD from top-tier university...",
      "task_2": "National Importance Score: 9/10\nWork directly addresses critical AI development priorities...",
      "task_3": "Overall Rating: Strong Candidate for NIW\nExcellent credentials combined with highly relevant research..."
    }
  }
}
```

## 📁 Project Structure

```
cv-evaluation/
├── main.py              # FastAPI application & CrewAI executor
├── cv-evaluator.py      # Core evaluation logic (duplicate)
├── pyproject.toml       # Project dependencies
└── README.md           # This file
```

## 🎯 Use Cases

- **Immigration Law Firms**: Streamline NIW case preparation
- **Academic Institutions**: Evaluate research candidates
- **Government Agencies**: Assess strategic importance of applicants
- **Research Organizations**: Score grant applications

## 🛠️ Technology Stack

- **Framework**: [CrewAI](https://crewai.com/) for multi-agent orchestration
- **API**: [FastAPI](https://fastapi.tiangolo.com/) for high-performance endpoints
- **Database**: [MongoDB](https://www.mongodb.com/) for data persistence
- **Language**: Python 3.12+

## 📊 Output Format

The system generates comprehensive evaluation reports including:
- Individual agent assessments
- Weighted final scores
- Detailed justifications
- Overall candidate rating (Strong/Moderate/Weak)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using CrewAI framework for intelligent CV evaluation**