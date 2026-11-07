import * as vscode from "vscode";

import { onDidChangePythonEnvironment } from "./python";
import { startServer, stopServer } from "./server";

/** VS Code calls this once, the first time one of the "activationEvents" in package.json happens. */
export async function activate(context: vscode.ExtensionContext): Promise<void> {
  // "Output" panel > "Import Linter": the server's log messages end up here.
  const outputChannel = vscode.window.createOutputChannel("Import Linter", { log: true });
  context.subscriptions.push(outputChannel);

  const restart = async () => {
    await stopServer();
    await startServer(outputChannel);
  };

  context.subscriptions.push(
    vscode.commands.registerCommand("importLinterLs.restart", restart),
    // A changed interpreter or setting only matters when the server restarts.
    vscode.workspace.onDidChangeConfiguration(async (event) => {
      if (event.affectsConfiguration("importLinterLs")) {
        await restart();
      }
    }),
    // Restart when the user selects another Python environment.
    ...(await onDidChangePythonEnvironment(restart)),
  );

  await startServer(outputChannel);
}

/** VS Code calls this when it closes or the extension is disabled. */
export async function deactivate(): Promise<void> {
  await stopServer();
}
