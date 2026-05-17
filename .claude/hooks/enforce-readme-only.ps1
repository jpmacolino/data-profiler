# Reads PreToolUse JSON input from stdin.
# Allows Edit calls only when targeting README.md in the project root.
# Exits 0 to allow, exit 2 to block.

$input_json = [Console]::In.ReadToEnd()
$payload = $input_json | ConvertFrom-Json

$file_path = $payload.tool_input.file_path

if (-not $file_path) {
    [Console]::Error.WriteLine("Hook error: no file_path in tool input.")
    exit 2
}

$basename = Split-Path $file_path -Leaf

if ($basename.ToLower() -eq "readme.md") {
    $output = @{
        hookSpecificOutput = @{
            hookEventName = "PreToolUse"
            permissionDecision = "allow"
            permissionDecisionReason = "doc-writer is scoped to README.md"
        }
    } | ConvertTo-Json -Depth 3
    [Console]::Out.WriteLine($output)
    exit 0
}

[Console]::Error.WriteLine("doc-writer is scoped to README.md only. Attempted edit on: $file_path")
exit 2