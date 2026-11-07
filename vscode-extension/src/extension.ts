import { PythonExtension } from "@vscode/python-extension";
import * as vscode from "vscode";

import { startServer, stopServer } from "./server";

/** VS Code calls this once, the first time one of the "activationEvents" in package.json happens. */
export async function activate(context: vscode.ExtensionContext): Promise<void> {
  // "Output" panel > "Import Linter": the server's log messages end up here.
  const outputChannel = vscode.window.createOutputChannel("Import Linter", { log: true });
  context.subscriptions.push(outputChannel);

  context.subscriptions.push(
    vscode.commands.registerCommand("importLinterLs.restart", async () => {
      await stopServer();
      await startServer(outputChannel);
    }),
    // A changed interpreter or setting only matters when the server restarts.
    vscode.workspace.onDidChangeConfiguration(async (event) => {
      if (event.affectsConfiguration("importLinterLs")) {
        await stopServer();
        await startServer(outputChannel);
      }
    }),
  );

  // Restart when the user picks another interpreter with "Python: Select Interpreter".
  const pythonExtension = await PythonExtension.api();
  context.subscriptions.push(
    pythonExtension.environments.onDidChangeActiveEnvironmentPath(async () => {
      await stopServer();
      await startServer(outputChannel);
    }),
  );

  await startServer(outputChannel);
}

/** VS Code calls this when it closes or the extension is disabled. */
export async function deactivate(): Promise<void> {
  await stopServer();
}
