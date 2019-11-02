.PHONY: windows linux

windows:
	powershell ./scripts/make_release_windows.ps1

linux:
	./scripts/make_release_linux.sh
