import os
import sys
import subprocess

# The FlaskMigrate migration files (migrations/versions) can't be present from the start,
# as FlaskMigrate does not start when the migrations-directory is already present.
# Thus, there is a small workaround that has to be done:
# 1. move migrations/versions to versions.install and remove migrations-directory
# 2. do 'flask db init' to initialize the db (creates migrations-directory)
# 3. move the version-files from versions.install to migrations/versions
# 4. do 'flask db upgrade' to apply the migration files

flenv = os.environ.copy()
flenv["FLASK_APP"] = "dmcp.py"

def step(text):
    sys.stdout.write("%s: " % text)

def success():
    sys.stdout.write("ok\n")

def fail(text):
    sys.stdout.write("failed\n")
    sys.stderr.write("%s\n" % text)
    exit(1)

def mv(src, dst):
    try:
        os.rename(src, dst)
        success()
    except Exception:
        fail(sys.exc_info()[1])

def rm(path):
    try:
        os.rmdir(path)
        success()
    except Exception:
        fail(sys.exc_info()[1])

def exec_cmd(cmd):
    proc = subprocess.Popen(cmd.split(" "), env=flenv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if proc.returncode == 0:
        success()
    else:
        fail(err.strip().decode())

# ----------------------------------------------------

step("check migration status")
if False == os.path.isfile("migrations/env.py"):
    success()
else:
    fail("migrations/env.py already exists - db is already be initialized!")

# ----------------------------------------------------
step("move migration files to temporary directory")
mv("migrations/versions", "versions.install")

# ----------------------------------------------------
step("delete migrations directory")
rm("migrations")

# ----------------------------------------------------
step("execute 'flask db init'")
exec_cmd("venv/bin/flask db init")

# ----------------------------------------------------
step("move migration files to migrations/versions") 
mv("versions.install", "migrations/versions")

# ----------------------------------------------------
step("execute 'flask db upgrade'")
exec_cmd("venv/bin/flask db upgrade")

# ----------------------------------------------------
print("db setup done!")
exit(0)
