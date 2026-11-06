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
      { scheme: "file", pattern: "**/.importlinter" },
      { scheme: "file", pattern: "**/setup.cfg" },
      { scheme: "file", pattern: "**/pyproject.toml" },
      { scheme: "file", language: "python" },
    ],
    outputChannel,
  };

  client = new LanguageClient("importLinterLs", "Import Linter", serverOptions, clientOptions);
  await client.start();
}

export async function stopServer(): Promise<void> {
  await client?.stop();
  client = undefined;
}
