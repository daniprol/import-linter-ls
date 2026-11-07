import * as vscode from "vscode";
import {
  LanguageClient,
  type LanguageClientOptions,
  type ServerOptions,
} from "vscode-languageclient/node";

import { findInterpreter } from "./python";

// The extension is a thin client: the language server is the Python program `import_linter_ls`.
// VS Code starts it as a child process and talks to it over stdin/stdout.
let client: LanguageClient | undefined;

const CONFIG_FILE_PATTERNS = ["**/.importlinter", "**/setup.cfg", "**/pyproject.toml"];

export async function startServer(outputChannel: vscode.LogOutputChannel): Promise<void> {
  const interpreter = await findInterpreter();
  outputChannel.info(`Starting import-linter-ls with ${interpreter}`);

  const serverOptions: ServerOptions = {
    command: interpreter,
    args: ["-m", "import_linter_ls"],
  };

  const clientOptions: LanguageClientOptions = {
    // Files the server wants to hear about. The server decides which of them hold import-linter config.
    documentSelector: [
      ...CONFIG_FILE_PATTERNS.map(pattern => ({ scheme: "file", pattern })),
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
