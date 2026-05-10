.PHONY: run

run:
	@powershell -Command "taskkill /F /IM msedge.exe *>utf8null; Write-Host 'Old Edge killed' -ForegroundColor DarkGray"
	cmd /c start msedge --remote-debugging-port=9222
	@powershell -Command "Write-Host 'Edge started' -ForegroundColor Green; Start-Sleep 2"
	powershell -Command "uv run python main.py"
