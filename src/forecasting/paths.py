"""Repository and run-relative locations; imports never create files."""
from dataclasses import dataclass
from pathlib import Path
import re

REPOSITORY = Path(__file__).resolve().parents[2]


def confined_path(directory: Path, relative: str) -> Path:
    path = directory / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(directory.resolve()):
        raise ValueError("Model reference escapes its run directory.")
    return path


@dataclass(frozen=True)
class RepositoryLayout:
    """Immutable repository root with the project's existing operational layout."""

    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.resolve())

    @property
    def dataset(self) -> Path:
        return self.root / "data" / "raw" / "supply_chain_dataset1.csv"

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
    def output_root(self) -> Path:
        return self.root / "outputs" / "revised-forecasting"

    def repository_path(self, relative: str) -> Path:
        """Resolve other declared repository inputs, without accessing their contents."""
        path = self.root / relative
        if Path(relative).is_absolute() or not path.resolve().is_relative_to(self.root):
            raise ValueError("Repository reference escapes its root.")
        return path

    def run_directory(self, run_id: str) -> Path:
        if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", run_id):
            raise ValueError("run_id must be a safe, nonempty local directory name.")
        output = self.output_root
        resolved_output = output.resolve()
        if not resolved_output.is_relative_to(self.root):
            raise ValueError("Output directory must stay inside the repository.")
        if resolved_output != output:
            raise ValueError("Forecasting output root must not redirect to another directory.")
        result = output / run_id
        if not result.resolve().is_relative_to(resolved_output):
            raise ValueError("Run directory must stay inside the forecasting output root.")
        return result

    @staticmethod
    def validation_model_directory(directory: Path) -> Path:
        return confined_path(directory, "models/validation")

    @staticmethod
    def candidate_model_directory(
        directory: Path, model: str, horizon: int, configuration_id: str, fold_id: int,
    ) -> Path:
        base = RepositoryLayout.validation_model_directory(directory)
        return confined_path(directory, (base / model / f"h{horizon}" / configuration_id / f"fold-{fold_id}").relative_to(directory).as_posix())

    @staticmethod
    def preprocessing_state_directory(directory: Path, model: str, horizon: int, fold_id: int) -> Path:
        return confined_path(directory, f"models/preprocessing/{model}/h{horizon}/fold-{fold_id}")


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
