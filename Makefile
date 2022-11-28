help:
	@exec echo "---------------------------------------------------------------" | lolcat 2>&1
	@exec echo "█▀█ █▀█ █▀█ ░░█ █▀▀ █▀▀ ▀█▀   ▀█▀ █▀▀ █▀▄▀█ █▀█ █░░ ▄▀█ ▀█▀ █▀▀" | lolcat 2>&1
	@exec echo "█▀▀ █▀▄ █▄█ █▄█ ██▄ █▄▄ ░█░   ░█░ ██▄ █░▀░█ █▀▀ █▄▄ █▀█ ░█░ ██▄" | lolcat 2>&1
	@exec echo " " | lolcat 2>&1
	@exec echo "                █▄▄ █░█ █ █░░ █▀▄ █▀▀ █▀█" | lolcat 2>&1
	@exec echo "                █▄█ █▄█ █ █▄▄ █▄▀ ██▄ █▀▄" | lolcat 2>&1
	@exec echo "---------------------------------------------------------------" | lolcat 2>&1
	@exec echo "-------------------------- HELP -------------------------------" | lolcat 2>&1
	@exec echo "            To setup the project type make setup" | lolcat 2>&1
	@exec echo "            To test the project type make test" | lolcat 2>&1
	@exec echo "            To run the project type make run" | lolcat 2>&1
	@exec echo "              ->[setup]" | lolcat 2>&1
	@exec echo "              ->[clean]" | lolcat 2>&1
	@exec echo "----------------------- Run Section ---------------------------" | lolcat 2>&1
	@exec echo "              ->[run_jupyter]" | lolcat 2>&1
	@exec echo "              ->[run_tester]" | lolcat 2>&1
	@exec echo "              ->[run_full_batches]" | lolcat 2>&1
	@exec echo "              ->[run_specific_batch]" | lolcat 2>&1
	@exec echo "---------------------------------------------------------------" | lolcat 2>&1

setup:
	@echo "Running System Installtion and configuration"
	sh -c "./constructProject.sh"
	@echo "Create the Project structure"
	@echo "Installing the virtualenv using $(shell pipenv --version)"
	@echo "with necessary python libraries ... "
	pipenv --python 3.8.8
	pipenv lock --pre
	pipenv install -r requirements.txt # these requirements generated from previous project using : pipenv run pip freeze > requirements.txt
	pipenv check
	@echo "Installing In-developemetn libraries"
	#pipenv install pytest --dev
	@echo "Activate the virtualenv .."
	#@rm -f ./basicPackages.txt ./constructProject.sh
	pipenv shell

run_jupyter:
	pipenv run jupyter notebook --port=9999 --no-browser

run_tester:
	pipenv run python -m src.tester.checkingBatches

run_full_batches:
	for ((i = 1; i  <= 37; i ++)); do echo -ne '\e[31m'"\uf6d5"'\e[0m'; echo '  Running Now Batch_'${i}; pipenv run python -m src.main Batch_${i}; done

run_specific_batch:
	pipenv run python -m src.main "Batch_${1}"

clean:
	@cp  ~/.Gscript/project_template_builder/cleaningScript.sh ./.
	@echo "Cleaning and removing the virtualenv ..."
	@echo "Exiting the virtualenv: $(shell exit)"
	@echo "Remove the virtualenv: $(shell pipenv --rm && exit)"
	@echo "Remove the virtualenv files AGPL "
	rm -f Pipfile Pipfile.lock requirements.txt
	sh -c "./cleaningScript.sh"
	@echo "Please use manually the command exit to exit the virtualenv: <exit>"
	rm -f Makefile cleaningScript.sh constructProject.sh basicPackages.txt



