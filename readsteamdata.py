import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import re
from tqdm import tqdm

### TODO: Do this in a jupyter file instead

# Merge the simple CSVs based on app_id
gamesdf = pd.read_csv("./games.csv", quotechar='"', escapechar='\\', dtype="str")
genresdf = pd.read_csv("./genres.csv", quotechar='"', escapechar='\\', dtype="str")
gamesdf = pd.merge(gamesdf, genresdf, on="app_id")
reviewsdf = pd.read_csv("./genres.csv", quotechar='"', escapechar='\\', dtype="str")
gamesdf = pd.merge(gamesdf, reviewsdf, on="app_id")

### TODO: NA values are written as \N. This screws up functions like the one below:
#gamesdf["release_date"] = pd.to_datetime(gamesdf["release_date"])

### TODO: Fix typing of each column

### Tags and categories need some pre-processing before being added to the DF
### Not sure if we want to use steamspy, promotional, or descriptions CSVs yet