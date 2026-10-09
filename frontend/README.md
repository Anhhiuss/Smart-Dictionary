# Smart Dictionary Frontend (Lexi)

A modern, university-level English–Vietnamese dictionary web application built with **React 18**, **TypeScript**, and **Vite**.

Lexi connects directly to the FastAPI backend to demonstrate real-world Data Structures and Algorithms in action:
- **Prefix Autocomplete**: Powered by an in-memory Trie index ($O(P + K)$ bounded search).
- **Approximate / Typo-tolerant Search**: Powered by dynamic-programming Levenshtein distance ($O(|Q| \cdot |W|)$) with length-difference pruning ($|len(W) - len(Q)| \le \text{max\_distance}$) and deterministic 5-tier ranking.
- **Persistent Dictionary Management**: Full CRUD operations backed by SQLite with automatic in-memory Trie synchronization.

---

## 1. Project Architecture

```
frontend/
├── index.html                   # HTML entry point with Lexi typography & branding
├── package.json                 # Dependencies (React 18, React Router v6, Lucide React)
├── tsconfig.json                # TypeScript strict configuration
├── vite.config.ts               # Vite bundler configuration with backend API proxy
├── .env.example                 # Environment variable templates
├── .env                         # Local environment configuration
└── src/
    ├── main.tsx                 # React DOM mount point
    ├── App.tsx                  # Application routing & layout shell
    ├── vite-env.d.ts            # Vite client type definitions
    ├── types/
    │   └── word.ts              # TypeScript interfaces mirroring FastAPI Pydantic schemas
    ├── services/
    │   ├── api.ts               # Centralized HTTP fetch client with error handling
    │   ├── search.service.ts    # Unified search & autocomplete suggestions API
    │   └── word.service.ts      # Dictionary word CRUD & system health API
    ├── hooks/
    │   └── useDebounce.ts       # React debounce hook for search queries (300ms)
    ├── utils/
    │   ├── debounce.ts          # Pure debounce helper
    │   └── normalizeQuery.ts    # Client-side input cleaning & NFC normalization
    ├── styles/
    │   ├── tokens.css           # Design tokens: palette (Forest/Charcoal/Ivory), elevation, spacing
    │   ├── typography.css       # Clean editorial typography (Lora & Inter)
    │   └── global.css           # Reset & base component styling
    ├── components/
    │   ├── layout/
    │   │   └── Header.tsx       # Navigation header with live backend/Trie index badge
    │   ├── search/
    │   │   ├── SearchBar.tsx           # Search input with keyboard navigation (Up/Down/Enter/Escape)
    │   │   ├── SuggestionDropdown.tsx  # Trie prefix suggestion dropdown with highlight
    │   │   └── SearchResultList.tsx    # Unified search results (Exact, Prefix, Fuzzy matches)
    │   ├── dictionary/
    │   │   └── WordDetailCard.tsx      # Comprehensive word view with IPA, word type, definitions, examples
    │   ├── management/
    │   │   ├── WordTable.tsx           # Paginated dictionary table with live search filter
    │   │   ├── WordFormModal.tsx       # Add/Edit modal dialog with validation
    │   │   └── DeleteWordDialog.tsx    # Safe deletion confirmation dialog
    │   └── feedback/
    │       ├── LoadingState.tsx        # Subtle editorial loading indicators
    │       ├── EmptyState.tsx          # Clean empty state placeholders
    │       └── ErrorState.tsx          # Friendly error states with retry triggers
    └── pages/
        ├── HomePage.tsx         # Primary search experience with Trie suggestions & Levenshtein results
        ├── WordDetailPage.tsx   # Direct word inspection route (/words/:word)
        └── ManagementPage.tsx   # Word management interface (/manage)
```

---

## 2. Prerequisites

- **Node.js**: v18.0.0 or later (Tested on Node v22.18.0)
- **npm**: v9.0.0 or later (Tested on npm 10.9.3)
- **Python**: v3.11+ with backend dependencies installed

---

## 3. Setup and Installation

### 3.1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3.2. Environment Configuration

Copy the example configuration to `.env`:

```bash
cp .env.example .env
```

Default configuration in `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 4. Running the Application

### 4.1. Start the Backend API (FastAPI)

In a separate terminal, start the FastAPI server from the project root:

```bash
# From repository root
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend starts at `http://localhost:8000`. You can verify its health at:
- `http://localhost:8000/api/health`
- `http://localhost:8000/docs` (Swagger UI)

### 4.2. Start the Frontend Development Server (Vite)

In your frontend terminal:

```bash
cd frontend
npm run dev
```

Vite will serve the application at:
```
http://localhost:5173
```

---

## 5. Available Scripts

Within the `frontend` directory:

- `npm run dev`: Starts the Vite development server with Hot Module Replacement (HMR).
- `npm run build`: Compiles TypeScript with `tsc` and bundles production assets using Vite.
- `npm run preview`: Locally previews the production build in `dist/`.
- `npm run typecheck`: Runs strict TypeScript type checking without generating build artifacts.

---

## 6. Design System & UI Principles

- **Editorial & Scholarly**: Clean serif headings (`Lora` / `Merriweather` fallback) and legible sans-serif body text (`Inter`).
- **Calm, High-Contrast Palette**:
  - Forest Green accent: `#1b4332`
  - Deep Charcoal text: `#1c201e`
  - Warm Ivory background: `#fcfbf9`
  - Subtle borders: `#e8e5dc`
- **Algorithm Transparency**:
  - Exact matches are marked with a distinct green tag.
  - Prefix suggestions display matched prefix characters in bold green.
  - Fuzzy matches prominently highlight the Levenshtein edit distance ($d = 1$, $d = 2$).
  - Header displays a real-time status indicator showing whether the backend is connected and how many words are indexed in the in-memory Trie.
