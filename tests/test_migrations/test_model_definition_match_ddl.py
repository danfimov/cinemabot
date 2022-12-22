from contextlib import redirect_stderr
from functools import wraps
from io import StringIO

from alembic import command as alembic_command
from alembic.autogenerate.api import AutogenContext
from alembic.autogenerate.render import _render_cmd_body
from alembic.command import upgrade
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import Script, ScriptDirectory
from alembic.util.exc import CommandError


class AlembicTestFailure(AssertionError):
    def __init__(self, message: str, context: list[tuple[str, str]] | None = None) -> None:
        super().__init__(message)
        self.context = context


class RevisionSuccess(Exception):
    """Raise when a revision is successfully generated.

    In order to prevent the generation of an actual revision file on disk when running tests,
    this exception should be raised.
    """

    @classmethod
    def process_revision_directives(cls, fn):  # type: ignore
        """Wrap a real `process_revision_directives` function, while preventing it from completing."""

        @wraps(fn)
        def _process_revision_directives(context: MigrationContext, revision: Script, directives: list[Script]) -> None:
            fn(context, revision, directives)
            raise cls()

        return _process_revision_directives


def _sequence_directives(*directives):  # type: ignore
    def directive_wrapper(*args, **kwargs):  # type: ignore
        for directive in directives:
            if not directive:
                continue
            directive(*args, **kwargs)

    return directive_wrapper


def get_revisions(config: Config) -> list[Script]:
    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(config)

    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()
    return revisions


def run_command(alembic_config: Config, command, *args, **kwargs) -> None:  # type: ignore
    executable_command = getattr(alembic_command, command)
    try:
        # Hide the (relatively) worthless logs of the upgrade revision path, it just clogs
        # up the logs when errors actually occur, but without providing any context.
        buffer = StringIO()
        with redirect_stderr(buffer):
            executable_command(alembic_config, *args, **kwargs)
    except CommandError as e:
        raise RuntimeError(e)


def test_model_definitions_match_ddl(alembic_config: Config) -> None:
    def verify_is_empty_revision(migration_context: MigrationContext, __, directives) -> None:  # type: ignore
        script = directives[0]

        migration_is_empty = script.upgrade_ops.is_empty()
        if not migration_is_empty:
            autogen_context = AutogenContext(migration_context)
            rendered_upgrade = _render_cmd_body(script.upgrade_ops, autogen_context)

            if not migration_is_empty:
                raise AlembicTestFailure(
                    """
                    The models describing the DDL of your database are out of sync with the set of
                    steps described in the revision history. This usually means that someone has
                    made manual changes to the database's DDL, or some model has been changed
                    without also generating a migration to describe that change.
                    """,
                    context=[
                        (
                            "The upgrade which would have been generated would look like",
                            rendered_upgrade,
                        )
                    ],
                )

    revisions = get_revisions(alembic_config)
    head_revision = revisions[0]
    upgrade(alembic_config, head_revision.revision)

    config_directive = alembic_config.attributes.get("process_revision_directives", False)
    fn = RevisionSuccess.process_revision_directives(
        _sequence_directives(config_directive, verify_is_empty_revision)
    )

    try:
        return run_command(
            alembic_config,
            "revision",
            process_revision_directives=fn,
            autogenerate=True,
        )
    except RevisionSuccess:
        pass
