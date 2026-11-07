import * as vscode from "vscode";
import {
  LanguageClient,
  type LanguageClientOptions,
  type ServerOptions,
} from "vscode-languageclient/node";

import { findServerCommand } from "./python";

// The extension is a thin client: the language server is the Python program `import_linter_ls`.
// VS Code starts it as a child process and talks to it over stdin/stdout.
let client: LanguageClient | undefined;

const CONFIG_FILE_PATTERNS = ["**/.importlinter", "**/setup.cfg", "**/pyproject.toml"];

export async function startServer(outputChannel: vscode.LogOutputChannel): Promise<void> {
  const serverCommand = await findServerCommand(outputChannel);
  if (!serverCommand) {
    const message =
      "import-linter-ls was not found. Install it in your project (uv add --dev import-linter-ls) " +
      "or for your user (uv tool install import-linter-ls), then run Import Linter: Restart Language Server.";
    outputChannel.error(message);
    void vscode.window.showErrorMessage(message);
    return;
  }
  outputChannel.info(`Starting: ${serverCommand.command} ${serverCommand.args.join(" ")}`);

  const serverOptions: ServerOptions = serverCommand;

  const clientOptions: LanguageClientOptions = {
    // Files the server wants to hear about. The server decides which of them hold import-linter config.
    documentSelector: [
      ...CONFIG_FILE_PATTERNS.map((pattern) => ({ scheme: "file", pattern })),
      { scheme: "file", language: "python" },
    ],
    outputChannel,
  };

  client = new LanguageClient("importLinterLs", "Import Linter", serverOptions, clientOptions);
  await client.start();
}

export async function stopServer(): Promise<void> {
  // `stop()` throws if the server never started (for example, the interpreter was not found),
  // and that would also break the "Restart" command. `needsStop()` says whether there is anything to stop.
  if (client?.needsStop()) {
    await client.stop();
  }
  client = undefined;
}
