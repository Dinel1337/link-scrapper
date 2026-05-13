.PHONY: clean run auto auto-reverse

INT := 15
SKIP := 0
COUNT := 0

clean:
	@powershell -Command "taskkill /F /IM msedge.exe *>$$null; Write-Host 'Edge killed & port cleared' -ForegroundColor DarkGray; Start-Sleep 1"

run: clean
	cmd /c start msedge --remote-debugging-port=9222
	@powershell -Command "Write-Host 'Edge started' -ForegroundColor Green; Start-Sleep 2"
	powershell -Command "uv run python main.py"

auto-reverse: clean
	cmd /c start msedge --remote-debugging-port=9222
	@powershell -Command "Write-Host 'Edge started (auto mode, interval=$(INT)s, skip=$(SKIP), count=$(COUNT))' -ForegroundColor Green; Start-Sleep 2"
	powershell -Command "uv run python main.py --auto $(INT) -r --skip $(SKIP) --count $(COUNT)"

auto: clean
	cmd /c start msedge --remote-debugging-port=9222
	@powershell -Command "Write-Host 'Edge started (auto mode, interval=$(INT)s, skip=$(SKIP), count=$(COUNT))' -ForegroundColor Green; Start-Sleep 2"
	powershell -Command "uv run python main.py --auto $(INT) --skip $(SKIP) --count $(COUNT)"