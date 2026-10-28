# Run Harness² from a chat

English | [中文](harness2.zh.md)

This optional integration adds `/harness2 on|off|status` to a dsh chat. When enabled, each new text task runs a full Harness² adaptation cycle on project copies before dsh receives the selected response, changes and harness. New chats start with the mode off.

## Install

Use this fork's `feat/harness2-integration` branch, Node 24, Python 3.12 or 3.13, and an existing dsh 0.2.0-rc.2 installation with a configured model. Other dsh versions are not qualified by this example. From this checkout:

```sh
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install 'harness2 @ git+https://github.com/LuciyVI/harness2.git@dsh-integration-v3'
python apps/cli/config/examples/harness2/install.py --profile web
```

The companion fork supplies the Python executor and adaptation engine. If `dsh` is not on `PATH`, set `HARNESS2_DSH_COMMAND` to your installed launcher, for example `node /absolute/path/to/dsh/lib/bin.js`, before installation. The installer locates that runtime's dependencies, adds a marked block to the existing profile patch and creates a private backup; it does not change the npm runtime or provider configuration.

Restart dsh through your normal profile launch and select a project workspace with `workspace-write` permissions. Model and search endpoints must already be reachable.

## Use

Send one command in the chat:

```text
/harness2 on
/harness2 status
/harness2 off
```

The selection belongs to that chat and restores from its recorded command events. Commands do not call a model. With the mode on, a task runs baseline execution, harness edits and probes, composition, final execution and experience reflection. At the default `k=1`, the single composed final is adopted without a comparison call; completion does not establish a quality gain.

Trial runs leave the live project untouched. The regular dsh agent receives the selected artifacts, inspects them and applies the requested project changes with its ordinary tools. Turning the mode off cancels an active cycle and disables later cycles; plugin disposal waits for its worker to finish. Solver and improver children cannot start nested adaptation cycles.

## Limits and recovery

Each model session has a 3600-second default deadline; a complete cycle includes several sessions. Change `timeout`, `k` or `outputRoot` in the installed `harness2-mode` entry. Status reports the active artifact path; the adjacent log reports progress. Failed and cancelled runs retain their artifacts and are not successful results.

Use the Python environment installed above to watch all session states. The viewer selects the newest cycle by default; supply the path from `/harness2 status` to select another:

```sh
watch -n 2 harness2-dsh-status
watch -n 2 harness2-dsh-status --cycle /absolute/path/to/cycles/<cycle-id>
```

`Deep diving` in the outer chat means it is waiting for the cycle. The viewer shows recorded steps, phase, termination reason and event age, without model or tool payloads. An unchanged `step_start` can be waiting for a response or tool; event age does not measure model inactivity. `max-tokens` is an exhausted model output budget, separate from the session deadline. The log reports failed attempts, retries and the final cycle result. Improver recordings stay under the cycle's `audit/`; the viewer also finds legacy improver recordings linked from the log under `/tmp`.

Text tasks and project files are supported. Use ordinary dsh for chat attachments. In a Git project, snapshots select tracked files and non-ignored untracked inputs. Git submodules and nested repositories are excluded without traversing their contents. This keeps ignored build trees and local reference repositories out of the snapshot. Plain folders use the runtime and credential filters. Internal symbolic links are relocated into each copy; external and broken links are rejected.

Default limits remain 100 MB and 10,000 entries. Configure `snapshotMaxBytes`, `snapshotMaxFiles` and project-relative `snapshotExclude` globs in the installed plugin entry when needed. `snapshot.json` records byte/file counts, largest selected files and exclusion reasons, including Git submodules; it is retained on a planning failure and names the metric and path that exceeded the limit.

After a failed turn, send the original task again to create a fresh cycle. An old failure card remains a record of its original attempt. Remove the integration with:

```sh
python apps/cli/config/examples/harness2/install.py --profile web --uninstall
```

## Verify without a model key

The profile test boots the installed dsh against a localhost fake model, checks command output and durable events, and runs the real Python cycle. It does not establish behavior with a production inference service:

```sh
HARNESS2_TEST_DSH_COMMAND="$HARNESS2_DSH_COMMAND" \
  python -m unittest discover -s apps/cli/tests/profiles/harness2 -v
```
