# Automate WebScrapping

## Requirements

- Install the pipenv requirements form the `lockfile.json` for clean setup and implementations.
- For more clear results in terminal.
  - Install a font that support ascii emojis and icons `from nerdfont`.
- Run the script form the main directory, assume main directory is at root of this project `MAWebScrapping/`


### Notes

You need to restart your `pipenv` to make sure any changes to the environment
variables will be initialized. Currently I am using `.env` file to add all the environment variables.

## Web driver

I am currently using

```shell
geckodriver 0.30.0 (d372710b98a6 2021-09-16 10:29 +0300)\n
`pipenv run python -c "import selenium;print(selenium.__version__)"`\n
Loading .env environment variables...\n
`4.1.2`\n
```



## Objectives

Crawling update to obtain newer press release&disclosure data from August 2021.
Next week, I'd like ask you to crawl this again in the same format.
Previous Work: it was done in July 2021 and so we have data for the period (to July 2021)
I'd like to extend data and therefore wanna have one for the period from August
2021 until latest(March 2022). Can you do that?

## Release and Disclosure data

period: August 2021 ~ March 2022

## Planning and Progress of work

We need to address the following feature

- Modularity
- Scalability for new modern applications.
- Fetching the articles asynchronously (maybe we can get asncio model)
- Automate in CLI using Rich library

## How to run

There are several ways to run and automate the script.

```shell
for ((i = 1; i  <= 37; i ++)); do echo -ne '\e[31m'"\uf6d5"'\e[0m'; echo '  Running Now Batch_'${i}; pipenv run python -m src.main Batch_${i}; done
```

## Development status update

Adding more features to the current automation project.

### Mon.March.14th 2022

- [x] Adding a tester for the html elements to check if the website has not broken.
- [x] Adding same logic from checking logic to the part of Fresh starting.
- [x] Keep aggregate the panda data frame of all the processed symbols, current implementations doesn't support such feature.
- [ ] Accept user input CLI args for keywords for the specified period such as start_time, end_time, today, last_week, ..etc.
- [ ] Migrate to docker with python3.8.4.
- [x] Check for exhaustive run for all historical articles if the logic can still stand.

### Tue Mar. 22nd 2022
- How to run the script from starting point
```shell
	pipenv --python 3.8.8
	pipenv lock --pre
	pipenv install -r requirements.txt # these requirements generated from previous project using : pipenv run pip freeze > requirements.txt
```
## References used:

1. Locating Elements using selenium  https://selenium-python.readthedocs.io/locating-elements.html
2. Getting emoji symbols from here: https://emojipedia.org/

