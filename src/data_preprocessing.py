import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def display_missing_values_counts(df, normalized = False):
    title = '\n Missing Values per Column' + (' %' if normalized  else '')
    dashline = '\n'+'-'*len(title)
    
    normalization_factor = len(df)/100 if normalized else 1
    
    print(dashline, title, dashline)    
    return df.isna().sum() // normalization_factor



def display_duplicates_count(df):
    title = '\n Duplicated Entries'
    dashline = '\n'+'-'*len(title)
    
    print(dashline, 
          title + ': ' + str(df.duplicated().sum()), 
          dashline)

    


def display_example(df, example_type, unpack=True):
    
    if example_type == 'duplicated_but_with_typo':
        cond1 = df['NomCommercial'] == 'citrulline malate'#'CITRULLINE MALATE'.lower()
        cond2 = df['FormeGalenique'] == 'poudre'#'Poudre'.lower()
        cond3 = df['ResponsableEtiquetage'] == 'indiex sport nutrition spain sl'#'INDIEX SPORT NUTRITION SPAIN SL'.lower()
        to_drop = ['ModeEmploi', 'Gamme', 'population_a_risques', 'plantes', 'familles_plantes', 'parties_plantes', 'objectif_effet']
        display(df[cond1 & cond2 & cond3].drop(to_drop, axis=1))

    elif example_type == 'duplicated_unclear':
        cond1 = df['NomCommercial']=='Beauté'.lower()
        cond2 = df['FormeGalenique']=='Capsule'.lower()
        cond3 = df['autres_ingredients']== 'gélatine,Eau purifiée,E422'.lower()
        display(df[cond1 & cond2 & cond3])
        


def display_duplicated_versions(df, to_exclude, index, unpack = True):
    '''
    Display all duplicated versions of the example row indicated by the index.
    '''
    # Drop columns to exclude
    df_subset = df.drop(to_exclude, axis=1)
    
    # Extract the example row as a Series
    example = df_subset.loc[index]
    
    # Ensure type consistency
    # mask = (df_subset == example).all(axis=1)                        # considers that Nan != Nan (wrong)
    mask = df_subset.apply(lambda row: row.equals(example), axis=1)    # handles well Nan == Nan
    
    # Count and display matching rows
    print(f"Number of matches: {mask.sum()}")
    
    # Retrieve and return matching rows from the original DataFrame
    matching_rows = df[mask]
    
    if unpack:
        for col in to_exclude:
            print(f"\n\n{col}:")
            for idx, row in matching_rows.iterrows():
                    print(f"\t{idx}: {row[col]}")
    
    return matching_rows


    
def top_categories_piechart(df, colname, top_n):
    
    colname = 'objectif_effet'
    
    data = df[colname].value_counts().head(top_n).values
    labels = df[colname].value_counts().head(top_n).index

    plt.pie(data, labels = labels, autopct='%.1f%%')
    plt.show()