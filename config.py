from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LLMConfig:
    base_url: str = "https://api.groq.com/openai/v1"
    model: str = "moonshotai/kimi-k2-instruct-0905"
    temperature: float = 0.2
    max_tokens: int = 512


@dataclass
class ChunkerConfig:
    min_tokens: int = 150
    max_tokens: int = 250
    overlap_pct: float = 0.15
    min_chunk_length: int = 15


@dataclass
class Config:
    # root
    base_dir: Path = Path(__file__).resolve().parent

    # computed paths (initialized in __post_init__)
    data_dir: Path = field(init=False)
    input_dir: Path = field(init=False)
    output_file: Path = field(init=False)
    chunks_file: Path = field(init=False)

    index_dir: Path = field(init=False)
    index_file: Path = field(init=False)
    index_chunks: Path = field(init=False)

    # LLM config
    llm: LLMConfig = field(default_factory=LLMConfig)

    # chunker
    chunker: ChunkerConfig = field(default_factory=ChunkerConfig)

    # embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    def __post_init__(self):
        # Data
        self.data_dir = self.base_dir / "data"
        self.input_dir = self.data_dir / "it-knowledge" / "canonical"
        self.output_file = self.data_dir / "output" / "output.txt"
        self.chunks_file = self.data_dir / "chunks" / "chunks_updated.json"

        # Index
        self.index_dir = self.base_dir / ".index"
        self.index_file = self.index_dir / "index.faiss"
        self.index_chunks = self.index_dir / "chunks_updated.pkl"

    def ensure_dirs(self):
        """
        Optionally create directories used by the config.
        Call this from your application entrypoint if you want auto-creation.
        """
        for p in (
            self.data_dir,
            self.output_file.parent,
            self.chunks_file.parent,
            self.index_dir,
        ):
            p.mkdir(parents=True, exist_ok=True)


config = Config()
