#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::{
    collections::HashMap,
    process::{Command, Output},
};

#[derive(Debug, serde::Deserialize)]
struct BridgeRunRequest {
    input: String,
    dry_run: bool,
    no_email: bool,
    env_path: Option<String>,
}

#[tauri::command]
fn run_bridge(request: BridgeRunRequest) -> Result<HashMap<String, String>, String> {
    let mut cmd = Command::new("bridge-cli");
    if request.dry_run {
        cmd.arg("--dry-run");
    }
    if request.no_email {
        cmd.arg("--no-email");
    }
    cmd.arg("-i").arg(request.input);
    if let Some(env) = request.env_path {
        cmd.arg("--config").arg(env);
    }

    let output = cmd
        .output()
        .map_err(|e| format!("failed to spawn bridge-cli: {e}"))?;
    interpret_output(output)
}

fn interpret_output(output: Output) -> Result<HashMap<String, String>, String> {
    let mut map = HashMap::new();
    map.insert(
        "stdout".into(),
        String::from_utf8(output.stdout).unwrap_or_default(),
    );
    map.insert(
        "stderr".into(),
        String::from_utf8(output.stderr).unwrap_or_default(),
    );
    map.insert(
        "status".into(),
        output.status.code().map(|c| c.to_string()).unwrap_or_default(),
    );
    Ok(map)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![run_bridge])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
