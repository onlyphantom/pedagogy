# this file is to clean the responses in database

from joblib import load
from pathlib import Path

import pandas as pd
import numpy as np
import sqlite3, string, re

conn = sqlite3.connect('test.db')

my_model = load(str(Path().absolute())+'/model/sentiment/model.joblib')
word_vector = load(str(Path().absolute())+'/model/sentiment/vector.joblib')

rs = pd.read_sql_query("SELECT * FROM response", conn)

rs.loc[:,'sentiment'] = '-'
rs.loc[:,'comments'] = rs['comments'].astype(str)
rs.loc[:,'comments'] = rs['comments'].apply(lambda x: x.lower())
rs.loc[:,'comments'] = rs['comments'].apply(lambda x: x.translate(str.maketrans("","", string.punctuation)))
rs.loc[:,'comments'] = rs['comments'].apply(lambda x: x.translate(str.maketrans("","", string.digits)))
rs.loc[:,'comments'] = rs['comments'].apply(lambda x: re.sub(' +', ' ',x).strip())
rs['comments'].replace(['','None'], np.nan, inplace=True)
rs['comments'].fillna('-',inplace=True)
rs.loc[:,'sentiment'] = my_model.predict(word_vector.transform(rs['comments']))

# write to sql after data cleansing
# rs.to_sql('response', con=conn, if_exists='replace', index=False)