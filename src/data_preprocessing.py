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
    
def display_duplicated_example(df, example):
    
    duplicated_rows = df[df.duplicated()].index
    duplicated_nomC = df[df.duplicated()].loc[:,'NomCommercial'].values
    
    # return df.loc[duplicated_rows[example],:]
    return df.loc[:, df['NomCommercial'] == duplicated_nomC[example]]
    # return duplicated_nomC[1]
    


def display_example(df, example_type, unpack=True):
    
    if example_type == 'duplicated_but_with_typo':
        cond1 = df['NomCommercial'] == 'CITRULLINE MALATE'
        cond2 = df['FormeGalenique'] == 'Poudre'
        cond3 = df['ResponsableEtiquetage'] == 'INDIEX SPORT NUTRITION SPAIN SL'
        to_drop = ['ModeEmploi', 'Gamme', 'population_a_risques', 'plantes', 'familles_plantes', 'parties_plantes', 'objectif_effet']
        display(df[cond1 & cond2 & cond3].drop(to_drop, axis=1))

    elif example_type == 'duplicated_unclear':
        cond1 = df['NomCommercial']=='Beauté'
        cond2 = df['FormeGalenique']=='Capsule'
        cond3 = df['autres_ingredients']== 'gélatine,Eau purifiée,E422'
        display(df[cond1 & cond2 & cond3])
        
    elif example_type == 'duplicated_alarming':
        cond1 = df['NomCommercial']=='NEUROBOOST'
        cond2 = df['FormeGalenique']=='Gélule'
        display(df[cond1 & cond2])

        if unpack:
            for col in df.columns:
                print(f"\n\n{col}:")
                for index, row in df[cond1 & cond2].iterrows():
                        print(f"\t{index}: {row[col]}")


    
def top_categories_piechart(df, colname, top_n):
    
    colname = 'objectif_effet'
    
    data = df[colname].value_counts().head(top_n).values
    labels = df[colname].value_counts().head(top_n).index

    plt.pie(data, labels = labels, autopct='%.1f%%')
    plt.show()