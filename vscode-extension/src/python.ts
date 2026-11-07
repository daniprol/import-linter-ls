import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import * as path from "node:path";
import { promisify } from "node:util";

import { PythonEnvironments } from "@vscode/python-environments";
import { PythonExtension } from "@vscode/python-extension";
import * as vscode from "vscode";

import { getInterpreterSetting } from "./settings";

/** How to start the server: a program and its arguments. */
export interface ServerCommand {
  command: string;
  args: string[];
}

/**
 * Find how to start the server. In order:
 * 1. the `importLinterLs.interpreter` setting,
 * 2. the project's environment, from the Python Environments extension or the Python extension,
 *    if `import-linter-ls` is installed there,
 * 3. the `import-linter-ls` command on the PATH (for example from `uv tool install import-linter-ls`).
 * Returns undefined when none of them works.
 */
export async function findServerCommand(
  outputChannel: vscode.LogOutputChannel,
): Promise<ServerCommand | undefined> {
  const fromSettings = getInterpreterSetting();
  if (fromSettings) {
    outputChannel.info(`Using the interpreter from the importLinterLs.interpreter setting`);
    return { command: fromSettings, args: ["-m", "import_linter_ls"] };
  }

  const projectPython = await findProjectPython();
  if (projectPython && (await canImportServer(projectPython))) {
    outputChannel.info(`Using the project's environment`);
    return { command: projectPython, args: ["-m", "import_linter_ls"] };
  }
  if (projectPython) {
    outputChannel.info(
      `import-linter-ls is not installed in the project's environment (${projectPython})`,
    );
  }

  // A command installed with `uv tool install` or `pipx` already starts with its own Python,
  // so we do not need to know where that Python is.
  const fromPath = findOnPath("import-linter-ls");
  if (fromPath) {
    outputChannel.info(`Using the import-linter-ls command on the PATH`);
    return { command: fromPath, args: [] };
  }
  return undefined;
}

/**
 * The Python of the environment the user selected for this workspace.
 *
 * Two Microsoft extensions can tell us. The newer Python Environments extension is only in charge when
 * the `python.useEnvironmentsExtension` setting is on. Otherwise the Python extension is.
 */
async function findProjectPython(): Promise<string | undefined> {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri;

  if (usesPythonEnvironmentsExtension()) {
    try {
      const environments = await PythonEnvironments.api();
      const environment = await environments.getEnvironment(workspaceFolder);
      return environment?.execInfo.run.executable;
    } catch {
      return undefined; // the extension is not installed or failed to start
    }
  }

  try {
    const pythonExtension = await PythonExtension.api();
    const environmentPath = pythonExtension.environments.getActiveEnvironmentPath(workspaceFolder);
    const environment = await pythonExtension.environments.resolveEnvironment(environmentPath);
    return environment?.executable.uri?.fsPath;
  } catch {
    return undefined; // the extension is not installed or failed to start
  }
}

function usesPythonEnvironmentsExtension(): boolean {
  return vscode.workspace
    .getConfiguration("python")
    .get<boolean>("useEnvironmentsExtension", false);
}

/** Whether `python` has `import-linter-ls` installed. */
async function canImportServer(python: string): Promise<boolean> {
  try {
    await promisify(execFile)(python, ["-c", "import import_linter_ls"]);
    return true;
  } catch {
    return false;
  }
}

/** The full path of `command` if it is in one of the PATH folders, like the `which` shell command. */
function findOnPath(command: string): string | undefined {
  const fileName = process.platform === "win32" ? `${command}.exe` : command;
  for (const folder of (process.env.PATH ?? "").split(path.delimiter)) {
    const candidate = path.join(folder, fileName);
    if (folder && existsSync(candidate)) {
      return candidate;
    }
  }
  return undefined;
}

/**
 * Call `onChange` when the user selects another Python environment, in whichever extension is in charge.
 * Returns the subscriptions, so that VS Code can remove them when the extension stops.
 */
export async function onDidChangePythonEnvironment(
  onChange: () => void,
): Promise<vscode.Disposable[]> {
  try {
    if (usesPythonEnvironmentsExtension()) {
      const environments = await PythonEnvironments.api();
      return [environments.onDidChangeEnvironment(onChange)];
    }
    const pythonExtension = await PythonExtension.api();
    return [pythonExtension.environments.onDidChangeActiveEnvironmentPath(onChange)];
  } catch {
    return []; // neither extension is available: only our own setting can change the interpreter
  }
}
