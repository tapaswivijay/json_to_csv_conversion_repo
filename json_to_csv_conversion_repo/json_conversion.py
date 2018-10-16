# script containing function convert_json_to_csv which processes JSON files to .csv one at a time by calling from the main script

import json
import pandas as pd
from pandas.io.json import json_normalize

# .json to .csv conversion function
def convert_json_to_csv(filepath):

        # to open filepath passed as argument from main script
	with open(filepath, 'rU') as f:
		json_parsed = json.load(f)
	
        # normalize the dict of parsed json 	
	df = json_normalize(json_parsed)	

        # To fetch the columns from dataframe which has values as nested lists
	a = df.applymap(lambda x: isinstance(x, list)).all()
	L = a.index[a].tolist()

	df['row_index'] = df.reset_index().index
        
        # To iterate through the columns containing the nested lists as values and to flatten them further into multiple rows
	for idx,i in enumerate(L):
		col_name = i.encode("utf-8")		
		df5 = pd.DataFrame()
		df5 = df[col_name].apply(pd.Series)
		
		for index, row in df5.iterrows():
				prefix_name = i + '_'				
				df1 = pd.DataFrame()
				df_dictionary_col = pd.DataFrame()

				df1 = json_normalize(row).add_prefix(prefix_name)
				df1['row_index'] = index
				df_dictionary_col = df_dictionary_col.append(df1)	
		
		dataframe_name = "df" + str(idx)		
		dataframe_name = df_dictionary_col
		
                # To merge the intial dataframe with all the flattened nested list column dataframes based on the row_index
		if idx == 0:
			df_intermediate = pd.DataFrame()
			df_intermediate = pd.merge(left=df,right=dataframe_name, how='right')
		else:
			df_intermediate = pd.merge(left=df_intermediate,right=dataframe_name, how='left')

        # To remove unnecessary columns from dataframe
	df_intermediate.drop(['batters.batter','topping'], axis=1, inplace=True)
	return df_intermediate
