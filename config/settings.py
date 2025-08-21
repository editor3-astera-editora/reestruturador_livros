import os 
from pathlib import Path 
from dotenv import load_dotenv

load_dotenv()

# --- Project Directories ---
BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
INPUT_DIR = ARTIFACTS_DIR / "input"
OUTPUT_DIR = ARTIFACTS_DIR / "output"
INTERMEDIATE_DIR = ARTIFACTS_DIR / "intermediate"
VECTORSTORE_DIR = ARTIFACTS_DIR / "vectorstore"

# --- Input/Output Files ---
INPUT_FILENAME = "livro_original.docx"
MARKDOWN_FILENAME = "livro_em_markdown.md"
STRUCTURE_MAP_FILENAME = "mapeamento_estrutura.json"
OUTPUT_FILENAME = "livro_reestruturado.docx"

# --- LLM and Embedding Models ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-4o"
EMBEDDING_MODEL = "text-embedding-3-small"

# --- RAG Configuration ---
CHUNK_SIZE_CHILD = 400
CHUNK_SIZE_PARENT = 2000

# --- LLM API Parameters for High Fidelity ---
LLM_TEMPERATURE = 0.2
LLM_TOP_P = 0.3

# --- Create directories if they don't exist ---
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)