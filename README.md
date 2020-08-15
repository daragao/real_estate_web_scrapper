[![codecov](https://codecov.io/gh/daragao/real_estate_web_scrapper/branch/master/graph/badge.svg)](https://codecov.io/gh/daragao/real_estate_web_scrapper)

# AWS real estate Web scrapping playgound

Although the name of the repo has not changed, this has evolved into a more generic repo, about creating an AWS serveless pipeline.

Everything is done using python 3.7.

The most interesting part of the repo at the moment is the [`lambda/`](lambda) directory. That is where the Lambda funcitons pushed ot AWS live.
Basically the pipeline is a function that scraps a website and stores a json with relevant data in an dynamodb, and a function that tries to find the geo location of each add saved to the db.

Nothing very fancy, but all in good fun
