import { PythonExtension } from "@vscode/python-extension";

import { getInterpreterSetting } from "./settings";

/**
 * Find the Python interpreter that runs the server. In order:
 * 1. the `importLinterLs.interpreter` setting,
 * 2. the interpreter selected in the Python extension (the one shown in the status bar),
 * 3. plain `python`, found on the PATH.
 */
export async function findInterpreter(): Promise<string> {
  const fromSettings = getInterpreterSetting();
  if (fromSettings) {
    return fromSettings;
  }

  const pythonExtension = await PythonExtension.api();
  const environmentPath = pythonExtension.environments.getActiveEnvironmentPath();
  const environment = await pythonExtension.environments.resolveEnvironment(environmentPath);
  // FIXME: we should probably check if python is a correct executable and not just assume "python" works.
  // also check if python3 is available on the PATH before falling back to "python".
  return environment?.executable.uri?.fsPath ?? "python";
}
