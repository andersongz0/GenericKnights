import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parent
db = sqlite3.connect(root / "GenericKnights.sqlite")

jobs = db.execute(
    'SELECT "Key", Name, "jobtype+Id", "jobcommand+Id", '
    'TexturePartsIndex, "uijobabilityhelp+Id" FROM "Job-en" '
    'WHERE "Key" IN (162,163) ORDER BY "Key"'
).fetchall()
requirements = db.execute(
    'SELECT "Key", RequiredJobIds, RequiredJobLevels, RequiredJobPositions '
    'FROM GeneralJob WHERE "Key" IN (22,23) ORDER BY "Key"'
).fetchall()
shapes = db.execute(
    'SELECT COUNT(*), MIN("Key"), MAX("Key") FROM CharShape '
    'WHERE "Key" BETWEEN 170 AND 173'
).fetchone()
shape_columns = [row[1] for row in db.execute('PRAGMA table_info(CharShape)')]
shape_payload_columns = [column for column in shape_columns if column not in ("Key", "Comment")]
shape_payload_sql = ", ".join(f'"{column}"' for column in shape_payload_columns)
template_shapes = [db.execute(
    f'SELECT {shape_payload_sql} FROM CharShape WHERE "Key" = ?', (key,)
).fetchone() for key in (100, 101)]
new_shapes = db.execute(
    f'SELECT {shape_payload_sql} FROM CharShape '
    'WHERE "Key" BETWEEN 170 AND 173 ORDER BY "Key"'
).fetchall()

expected_jobs = [
    (162, "Holy Knight", 38, 162, 162, 24),
    (163, "Rune Knight", 44, 163, 163, 31),
]
expected_requirements = [
    (22, "[2,5]", "[8,8]", "[1,2]"),
    (23, "[2,7]", "[8,8]", "[1,2]"),
]

assert jobs == expected_jobs, jobs
assert requirements == expected_requirements, requirements
assert shapes == (4, 170, 173), shapes
# The gender-specific shape records must retain every runtime lookup field of
# the equivalent pristine generic shape.  Only Key and Comment may differ.
assert new_shapes == template_shapes * 2, new_shapes
assert db.execute('SELECT COUNT(*) FROM "Job-en"').fetchone()[0] >= 164
assert db.execute('SELECT COUNT(*) FROM GeneralJob').fetchone()[0] == 23
assert db.execute('SELECT COUNT(*) FROM CharShape').fetchone()[0] == 163
print("GenericKnights NXD round-trip verification passed.")
print(jobs)
print(requirements)
print(shapes)
print("CharShape 170..173 match male/female Knight templates; native named shapes preserved.")
