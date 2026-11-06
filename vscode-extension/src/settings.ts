import * as vscode from "vscode";

// All user settings of the extension live under "importLinterLs" (see "configuration" in package.json).
const settings = () => vscode.workspace.getConfiguration("importLinterLs");

/** The interpreter the user typed in settings, or "" when they want the Python extension's choice. */
export function getInterpreterSetting(): string {
  return settings().get<string>("interpreter", "");
}
