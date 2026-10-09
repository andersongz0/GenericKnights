import shutil
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent
# Build against pristine game tables, never against GenericJobs' already
# merged snapshot.  The utility loader compares each mod to the base game;
# using GenericJobs as our starting point made this mod claim ownership of
# Dark/Onion rows as well as its own rows.
SOURCE_DB = ROOT / "analysis" / "base-tables.sqlite"
OUTPUT_DB = ROOT / "GenericKnights.sqlite"


def clone_row(connection, table, source_key, target_key, overrides=None):
    overrides = overrides or {}
    columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')]
    source = connection.execute(
        f'SELECT * FROM "{table}" WHERE Key = ?', (source_key,)
    ).fetchone()
    if source is None:
        raise RuntimeError(f"Missing {table} row {source_key}")

    values = dict(zip(columns, source))
    values["Key"] = target_key
    values.update(overrides)
    placeholders = ", ".join("?" for _ in columns)
    names = ", ".join(f'"{column}"' for column in columns)
    connection.execute(f'DELETE FROM "{table}" WHERE Key = ?', (target_key,))
    connection.execute(
        f'INSERT INTO "{table}" ({names}) VALUES ({placeholders})',
        [values[column] for column in columns],
    )


def main():
    shutil.copy2(SOURCE_DB, OUTPUT_DB)
    connection = sqlite3.connect(OUTPUT_DB)
    try:
        # JobType is a shared category table, not a table indexed by Job ID.
        # A2/A3 are custom Job IDs, but they must refer to the existing
        # generic visual categories: Knight (38) and Time Mage (44).
        # These categories define equipment/stats, not the native body index.
        # A2/A3 body resolution requires the loader's separate sprite-table
        # expansion; changing JobType alone cannot fix the byte overflow.
        # Keep named characters' command data, descriptions and overview pages.
        for language in ("en", "de", "fr", "ja"):
            holy_description = connection.execute(
                f'SELECT Description FROM "Job-{language}" WHERE Key = 30'
            ).fetchone()[0]
            rune_description = connection.execute(
                f'SELECT Description FROM "Job-{language}" WHERE Key = 50'
            ).fetchone()[0]
            clone_row(
                connection,
                f"Job-{language}",
                76,  # generic Knight visual route
                0xA2,
                {
                    "Name": "Holy Knight",
                    "Unknown4": "Holy Knight",
                    "Description": holy_description,
                    "jobtype+Id": 38,
                    "jobcommand+Id": 0xA2,
                    # The value is the job-icon resource index, not the
                    # generic-job position.  It must match j_162_uitx.
                    "TexturePartsIndex": 0xA2,
                    "uijobabilityhelp+Id": 24,
                    "HideJobTree": 0,
                },
            )
            clone_row(
                connection,
                f"Job-{language}",
                81,  # generic Time Mage visual route
                0xA3,
                {
                    "Name": "Rune Knight",
                    "Unknown4": "Rune Knight",
                    "Description": rune_description,
                    "jobtype+Id": 44,
                    "jobcommand+Id": 0xA3,
                    # Likewise this points at j_163_uitx.
                    "TexturePartsIndex": 0xA3,
                    "uijobabilityhelp+Id": 31,
                    "HideJobTree": 0,
                },
            )

            # Commands get their own IDs so their Action Ability lists can be
            # copied intact while Reaction/Support/Movement stay empty in the
            # runtime JobCommandData table.
            clone_row(connection, f"JobCommand-{language}", 40, 0xA2)
            clone_row(connection, f"JobCommand-{language}", 41, 0xA3)

        # Generic-job positions 22 and 23 back A2 and A3.  Generic job IDs in
        # the requirement arrays are zero-based: Knight=2, White Mage=5,
        # Time Mage=7.
        clone_row(
            connection,
            "GeneralJob",
            20,
            22,
            {
                "Comment": "GenericKnights: Holy Knight",
                "RequiredJobIds": "[2,5]",
                "RequiredJobLevels": "[8,8]",
                "RequiredJobPositions": "[1,2]",
            },
        )
        clone_row(
            connection,
            "GeneralJob",
            20,
            23,
            {
                "Comment": "GenericKnights: Rune Knight",
                "RequiredJobIds": "[2,7]",
                "RequiredJobLevels": "[8,8]",
                "RequiredJobPositions": "[1,2]",
            },
        )

        # Two gender-specific character shapes per job.  Clone an equivalent
        # generic base shape, rather than a shape introduced by GenericJobs.
        # Native shapes 163..169 belong to named WotL characters, even though
        # they are absent from pristine CharShape.nxd. New shapes start at 170
        # and are registered by FFTModLoader.visuals.json (not JobType).
        for target_key in range(170, 174):
            clone_row(
                connection,
                "CharShape",
                100 + (target_key % 2),
                target_key,
                {"Comment": f"GenericKnights sprite {target_key}"},
            )

        connection.commit()
    finally:
        connection.close()

    # NXD is a complete table snapshot. Removing inherited rows here would
    # instruct the runtime merger to delete them from the live game table.


if __name__ == "__main__":
    main()
