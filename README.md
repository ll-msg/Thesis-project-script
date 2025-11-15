# Thesis-project-script
Scripts developed for Honour's thesis project.

## [dbTime](https://github.com/ll-msg/Thesis-project-script/blob/main/dbTime.py)
A python automation script that can be used to evaluate how database time scales with different dataset sizes. It simulates user interactions with the MGTdb web application and measure database time through PostgreSQL's `pg_stat_statments`.

The script contains the following main steps: 

- Simulate API calls that represent [MGTdb](https://www.mgtdb.unsw.edu.au/) features (e.g., `initial-isolate`).
- Log database time into a file.
- Perform isolate deletions (50k isolates each time until 70k isolates left) and repeat above operations.

### How to run
```python
python dbTime.py
```

## [constants](https://github.com/ll-msg/Thesis-project-script/blob/main/constants.py)
A file contains all the helper constants for [dbTime](https://github.com/ll-msg/Thesis-project-script/blob/main/dbTime.py) .

## [test_graphicalView](https://github.com/ll-msg/Thesis-project-script/blob/main/test_graphicalView.py)
A Django unit test script that can be used to validate the optimized graphical view feature in [MGTdb](https://www.mgtdb.unsw.edu.au/), specifically for Typhimurium and *Salmonella* databases. It can be performed with real databases hosted in the local environment. 

Each test in this script contains the following main steps:

- Build and execute a query to retrieve all the ST, CC or ODC values that match the conditions.
- Compute the top 10 values using Python.
- Compare the top 10 values with the expected value which was pre-computed using the optimized query.

### How to run
```python
pytest path-to-graphicalViewTest
```
Please notice that this test is required to be run inside the original MGT root folder.

## [tests_cCmerge](https://github.com/ll-msg/Thesis-project-script/blob/main/tests_cCmerge.py)
A Django unit test script that can be used to validate the optimized clonal complex merging method in [MGTdb](https://www.mgtdb.unsw.edu.au/), specifically for the Typhimurium database. The test database used in this script is constructed automatically by Django.

Each test in this script contains the following main steps:

- Compute the clonal complex using the optimized merging function.
- Compare with the expected value which was pre-computed through the pre-optimized merging function.

### How to run
```python
python manage.py test path-to-ccMergeTest --settings=path-to-settings
```
Please notice that this test is required to be run inside the original MGT root folder.
