$extensions = @(
  'ms-python.python',
  'ms-python.vscode-pylance',
  'ms-toolsai.jupyter',
  'ms-azuretools.vscode-docker',
  'eamodio.gitlens',
  'esbenp.prettier-vscode',
  'dbaeumer.vscode-eslint',
  'bradlc.vscode-tailwindcss',
  'ms-ossdata.vscode-postgresql',
  'mtxr.sqltools',
  'EditorConfig.EditorConfig',
  'PKief.material-icon-theme'
)

foreach ($ext in $extensions) {
  Write-Host "Installing $ext"
  $code = Get-Command code -ErrorAction SilentlyContinue
  if (-not $code) {
    Write-Error "VS Code CLI 'code' not found in PATH. Ensure 'code' command is available and retry."
    exit 1
  }
  & code --install-extension $ext --force
}

Write-Host "All install commands finished."
