# LoL Compare

LoL Compare is a full-stack application designed to analyse and compare League of Legends data. The project is structured as a monorepo managed by Bun, featuring a Python FastAPI backend for data processing, a React frontend for visualisation, and AWS CDK for infrastructure as code.

## 📂 Project Structure

The repository is organised into three main packages:

- **`backend/`**: A Python-based API using FastAPI, Poetry, and Scikit-learn for data analysis and machine learning tasks.
- **`frontend/`**: A React application built with Vite, TypeScript, and TailwindCSS for the user interface.
- **`cdk/`**: Infrastructure definitions using AWS CDK (TypeScript) for deploying the application to AWS.

## 🚀 Getting Started

### Prerequisites

- **[Bun](https://bun.sh/)** (v1.3.1+)
- **[Python](https://www.python.org/)** (v3.12+)
- **[Poetry](https://python-poetry.org/)** (Backend dependency management)
- **[Node.js](https://nodejs.org/)** (Required for AWS CDK)
- **AWS CLI** configured with appropriate credentials (if deploying)

### Installation

1. **Root Dependencies**
   Install the root level dependencies (including Husky for git hooks):
   ```bash
   bun install
   ```

2. **Backend Setup**
   Navigate to the backend directory and install Python dependencies:
   ```bash
   cd backend
   poetry install
   ```

3. **Frontend Setup**
   Navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend
   bun install
   ```

4. **Infrastructure Setup**
   Navigate to the CDK directory and install dependencies:
   ```bash
   cd cdk
   npm install
   ```

## 💻 Development

### Running the Project

You can run both the backend and frontend concurrently using the root-level script:

```bash
bun run start-dev
```

Alternatively, you can run services individually:

**Backend (FastAPI):**
```bash
cd backend
poetry run uvicorn app.main:app --reload --port 8000
```

**Frontend (Vite):**
```bash
cd frontend
bun run dev
```

### Infrastructure (AWS CDK)

To deploy or synthesise the infrastructure:

```bash
cd cdk
# Compile TypeScript to JS
npm run build

# Compare deployed stack with current state
npx cdk diff

# Deploy to default AWS account/region
npx cdk deploy
```

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 19
- **Build Tool:** Vite
- **Language:** TypeScript
- **Styling:** TailwindCSS v4
- **State/Data Fetching:** TanStack Query
- **Visualisation:** Victory Charts
- **Icons:** Lucide React

### Backend
- **Framework:** FastAPI
- **Package Manager:** Poetry
- **Data Science:** Pandas, NumPy, Scikit-learn, UMAP-learn
- **AWS Integration:** Mangum (Lambda adapter)
- **Linting:** Ruff

### Infrastructure
- **IaC:** AWS CDK
- **Language:** TypeScript

---

*This project was initialised using `bun init`.*