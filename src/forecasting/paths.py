"""Repository and run-relative locations; imports never create files."""
from dataclasses import dataclass
from pathlib import Path
import re

REPOSITORY = Path(__file__).resolve().parents[2]
VALIDATED_DATASET_RELATIVE_PATH = Path("data/processed/validated/supply-chain-dataset1-validated-v1/validated.parquet")


def confined_path(directory: Path, relative: str) -> Path:
    path = directory / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(directory.resolve()):
        raise ValueError("Model reference escapes its run directory.")
    return path


@dataclass(frozen=True)
class RepositoryLayout:
    """Immutable repository root and approved forecasting storage locations."""

    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.resolve())

    @property
    def dataset(self) -> Path:
        return self.root / VALIDATED_DATASET_RELATIVE_PATH

    @property
    def execution_record(self) -> Path:
        return self.root / "data" / "processed" / "forecasting" / "validation_authorization.json"

    @property
    def protocol(self) -> Path:
        return self.root / "docs" / "protocol.md"

    @property
    def feature_contract(self) -> Path:
        return self.root / "docs" / "forecasting-feature-engineering.md"

    @property
    def artifact_root(self) -> Path:
        return self.root / "artifacts" / "forecasting"

    @property
    def model_root(self) -> Path:
        return self.root / "models" / "forecasting"

    @property
    def draft_report_root(self) -> Path:
        return self.root / "reports" / "forecasting" / "drafts"

    @property
    def output_root(self) -> Path:
        """Compatibility alias for machine-readable run evidence."""
        return self.artifact_root

    def repository_path(self, relative: str) -> Path:
        """Resolve other declared repository inputs, without accessing their contents."""
        path = self.root / relative
        if Path(relative).is_absolute() or not path.resolve().is_relative_to(self.root):
            raise ValueError("Repository reference escapes its root.")
        return path

    def _run_directory(self, root: Path, run_id: str) -> Path:
        if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", run_id):
            raise ValueError("run_id must be a safe, nonempty local directory name.")
        return self._owned_path(root / run_id)

    def _owned_path(self, path: Path) -> Path:
        """Reject symlink redirection and existing non-directory ancestors."""
        relative = path.relative_to(self.root)
        current = self.root
        for component in relative.parts:
            if current.exists() and not current.is_dir():
                raise ValueError("Forecasting storage ancestors must be directories.")
            current = current / component
            if current.is_symlink():
                raise ValueError("Forecasting storage must not redirect through a symlink.")
        if path.resolve() != path:
            raise ValueError("Forecasting storage must stay at its declared repository location.")
        return path

    def run_directory(self, run_id: str) -> Path:
        """Canonical artifact-run anchor; resolution never creates directories."""
        return self._run_directory(self.artifact_root, run_id)

    def model_run_directory(self, run_id: str) -> Path:
        return self._run_directory(self.model_root, run_id)

    def draft_report_directory(self, run_id: str) -> Path:
        return self._run_directory(self.draft_report_root, run_id)

    @classmethod
    def from_artifact_directory(cls, directory: Path) -> "RepositoryLayout":
        """Resolve only an absolute canonical artifacts/forecasting/<run_id> anchor."""
        if (not directory.is_absolute() or directory.parent.name != "forecasting"
                or directory.parent.parent.name != "artifacts"):
            raise ValueError("A canonical forecasting artifact run directory is required.")
        layout = cls(directory.parents[2])
        if directory != layout.run_directory(directory.name):
            raise ValueError("A canonical forecasting artifact run directory is required.")
        return layout

    @staticmethod
    def validation_model_directory(directory: Path) -> Path:
        layout = RepositoryLayout.from_artifact_directory(directory)
        return layout._owned_path(layout.model_run_directory(directory.name) / "validation")

    @staticmethod
    def candidate_model_directory(
        directory: Path, model: str, horizon: int, configuration_id: str, fold_id: int,
    ) -> Path:
        layout = RepositoryLayout.from_artifact_directory(directory)
        base = RepositoryLayout.validation_model_directory(directory)
        path = confined_path(base, f"{model}/h{horizon}/{configuration_id}/fold-{fold_id}")
        return layout._owned_path(path)

    @staticmethod
    def preprocessing_state_directory(directory: Path, model: str, horizon: int, fold_id: int) -> Path:
        layout = RepositoryLayout.from_artifact_directory(directory)
        base = layout.model_run_directory(directory.name)
        path = confined_path(base, f"preprocessing/{model}/h{horizon}/fold-{fold_id}")
        return layout._owned_path(path)


DEFAULT_LAYOUT = RepositoryLayout(REPOSITORY)


# Compatibility wrappers retain the previous function signatures.
def approved_dataset(repository: Path = REPOSITORY) -> Path:
    return RepositoryLayout(repository).dataset


def execution_record(repository: Path = REPOSITORY) -> Path:
    return RepositoryLayout(repository).execution_record


def output_root(repository: Path = REPOSITORY) -> Path:
    return RepositoryLayout(repository).output_root


def run_directory(repository: Path, run_id: str) -> Path:
    return RepositoryLayout(repository).run_directory(run_id)


def validation_models(directory: Path) -> Path:
    return RepositoryLayout.validation_model_directory(directory)
