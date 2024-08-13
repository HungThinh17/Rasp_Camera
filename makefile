# USER = pi
# ADDRESS = 127.0.0.1
USER = hungnp
ADDRESS = 192.168.1.17
SHAREPOINT_ADDRESS = 192.168.1.8
SHAREPOINT = /app
MOUNTPOINT = /mnt/app
APP = newSLI.py

syncResource:
	# Do share the target folder from windows first.. do it manually !!
	ssh $(USER)@$(ADDRESS) "sudo -S mkdir -p $(MOUNTPOINT)"
	ssh $(USER)@$(ADDRESS) "sudo -S mount -t cifs -o username=hungnp,password=q123,file_mode=0777,dir_mode=0777 //$(SHAREPOINT_ADDRESS)$(SHAREPOINT) $(MOUNTPOINT)"

installDependencies:
	ssh $(USER)@$(ADDRESS) "sudo -S chmod +x $(MOUNTPOINT)/installDependencies.sh"
	ssh $(USER)@$(ADDRESS) "cd $(MOUNTPOINT)/ && sudo ./installDependencies.sh"

removeDependencies:
	ssh $(USER)@$(ADDRESS) "sudo -S chmod +x $(MOUNTPOINT)/removeDependencies.sh"
	ssh $(USER)@$(ADDRESS) "cd $(MOUNTPOINT)/ && sudo ./removeDependencies.sh"

debug:
	ssh $(USER)@$(ADDRESS) "sudo chmod -R 777 /dev/serial0"
	ssh -L 5678:localhost:5678 $(USER)@$(ADDRESS) "DISPLAY=:10 python $(MOUNTPOINT)/$(APP) --debug" || true

manualProfiling:
	ssh $(USER)@$(ADDRESS) "sudo rm -rf /mnt/app/profilings"
	ssh $(USER)@$(ADDRESS) "sudo chmod -R 777 /dev/serial0"
	ssh $(USER)@$(ADDRESS) "DISPLAY=:10 python $(MOUNTPOINT)/$(APP) --profiling" || true

clean:
	ssh $(USER)@$(ADDRESS) "sudo pgrep -f newSLI.py | xargs kill" || true
	@echo Done! && exit

