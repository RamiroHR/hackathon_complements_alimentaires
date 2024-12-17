import pandas as pd
import numpy as np
import re

def apply_formatings(df, format, verbose = False):
    '''
    format dataframe df by applying the formatting steps in formating dict
    '''
    
    if format['lower_case']:     
        df = df.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
        if verbose: print("- Lower case the entire dataframe")
    
    if format['remove_redundant_information']:
        df = df.map(remove_redundant_information)
        if verbose: print("- Removed redundant information")
    
    if format['replace_decimal_point']:
        df = df.map(replace_decimal_point)
        if verbose: print("- Replaced decimal commas by points")

    if format['replace_commas_in_parenthesis']:
        df = df.map(replace_commas_in_parentheses)
        if verbose: print("- Replaced commas inside parenthesis by semicolons")
        
    if format['replace_ampersands']:
        df = df.map(replace_ampersands)
        if verbose: print("- Correctly encode ampersand symbols")
    
    return df

    
    

def remove_redundant_information(val):
    # Try to handle the string as a list, if it looks like one or like a doubled string, then split
    try:
        l = len(val)
        
        # Clean the string if it is like a list, strip the brackets & quotes, and split by commas
        if val.startswith('["') and val.endswith('"]'):
            cleaned_val = val[2:-2]  # Remove leading '["' and trailing '"]'
            items = [item.strip().strip('"') for item in cleaned_val.split('", "')]  # Split by '", "' and remove quotes

            # Check if the elements are identical
            if len(items) == 2 and items[0] == items[1]:
                return items[0]  # Return the single element if identical
            else:
                return ",".join(items)  # Join with comma if different

        # Clean a string that is duplicated after a comma
        elif val[:l//2] == val[l//2+1:] and val[l//2]==',':
            return val[:l//2]

        # Return original value if not a doubled-list or doubled-string
        else:
            return val  

    # In case of error, to handle NaNs, return the original value
    except Exception as e:
        return val  




# Function to replace commas in decimal numbers
def replace_decimal_point(value):
    '''
    Replace commas only when between digits.
    Skyp NaN values.
    ''' 
    if isinstance(value, str):
        return re.sub(r'(?<=\d),(?=\d)', '.', value)
    return value    



def replace_commas_in_parentheses(val):
    '''
    Use a regular expression to find anything inside parentheses and replace commas inside with semicolons
    '''
    if isinstance(val, str):
        return re.sub(r'\(([^()]*)\)', 
                      lambda m: f"({m.group(1).replace(',', ';')})", 
                      val)    

    return val  # Return original value if it's not a string



def replace_ampersands(val):
    '''
    Use a regular expression to find '&amp;' pattern and replace with '&' symbol
    '''
    if isinstance(val, str):
        return re.sub(r'&amp;', '&', val)
    return val



#############################################################################################################


def clean_data(df, steps, verbose = True):
    '''
    Apply the step defined in the step dictionary to the dataset.
    Return the cleaned dataset.
    '''
    
    if steps['drop_duplicates']:
        df.drop_duplicates(inplace = True)
        if verbose: print("- Simple duplicates removed")
    

    return df


#############################################################################################################


def enrich_data(df, steps, verbose = True):
    '''
    Pass a dictionary containing all datasets: df.
    Enrich dataset with each procedure mentioned in the step dictionary.
    Return the transformed datasets.
    '''
    
    if steps['gather_substances']:
        # Lookup dictionaries for plant:substances and plant_synonyms:substances
        plant_substances = create_lookup(df['plantes'])

        # Lookup dictionary from ingredients dataset
        ingredient_substances = create_lookup(df['ingredients'])

        # Apply function to gather all substances for each product
        df['complements']['substances'] = df['complements'].apply(gather_substances, axis = 1, 
                                                            plant_substances = plant_substances, 
                                                            ingredient_substances = ingredient_substances)
    
        if verbose: print("'substances' feature added")
    
    if steps['check_bio_label']:
        subset = ['NomCommercial', 'Marque', 'Gamme', 'Aromes']
        df['complements'] = verify_bio_label(df['complements'], subset)
        if verbose: print("'is_bio' feature created")
    
    if steps['check_quantity_mention']:
        df['complements'] = verify_quantity_in_name(df['complements'])
        if verbose: print("'has_quanity' feature added")
    
    return df['complements']



## Function to add entries to the lookup dictionary with multiple substances per key
def add_to_lookup(lookup, key, value):
    """
    Add substances associated with a key to the lookup dictionary. 
    If `value` contains a comma-separated list of substances, split and add them individually.
    """
    # Ensure the value is split into separate substances if comma-separated
    substances = [v.strip() for v in value.split(',')] if isinstance(value, str) else []
    
    if key in lookup:
        # Add each substance to the list if not already present
        for substance in substances:
            if substance not in lookup[key]:
                lookup[key].append(substance)
    else:
        # Initialize the key with the list of substances
        lookup[key] = substances


## Function to create a lookup dictionary using main names and synnonym names
def create_lookup(df):
    lookup_dict = {}
    
    # Populate the dictionary with main names : substances
    for _, row in df.iterrows():
        add_to_lookup(lookup_dict, row['name'], row['substances'])
    
    # Populate the dictionary with synonyms names : susbtances
    for _, row in df.iterrows():
        if pd.notna(row['synonyms']):  # Skip NaNs
            synonyms = [syn.strip() for syn in row['synonyms'].split(',')]  # Split and clean
            for synonym in synonyms:
                add_to_lookup(lookup_dict, synonym, row['substances'])

    return lookup_dict



def gather_substances(row, plant_substances, ingredient_substances):

    # Get list of plants
    ls_plants = [item.strip() for item in str(row['plantes']).split(',') if item.strip() and item != 'nan']
    
    # Get list of other ingredients
    ls_ingredients = [item.strip() for item in str(row['autres_ingredients']).split(',') if item.strip() and item != 'nan']
    
    # Get all substances from plants and ingredients
    ls_substances = []
    for plant in ls_plants:
        if plant in plant_substances:
            # ls_substances.extend(str(plant_substances[plant]).split(','))
            ls_substances.extend(plant_substances[plant])
    
    for ingredient in ls_ingredients:
        if ingredient in ingredient_substances:
            # ls_substances.extend(str(ingredient_substances[ingredient]).split(','))
            ls_substances.extend(ingredient_substances[ingredient])
    
    # Clean (spaces), remove repeated substances and return as a joined string
    ls_substances = list(set([item.strip() for item in ls_substances if item and item != 'nan']))

    return ','.join(ls_substances) if ls_substances else np.nan



def join_columns(row, subset):
    to_join = [str(row[col]) for col in subset]
    joined_str = ' - '.join(to_join)
    return joined_str


def verify_bio_label(df, subset):

    # join columns into a single auxiliar str column
    df['Nom_Marque_Gamme'] = df.apply(join_columns, axis=1, subset=subset)

    # Define a regex pattern for 'bio' keywords
    bio_labels = r"\b(bio|biologique)\b"      # Match single labels (\b is word boundary)
    
    # Apply regex to create a column to label 'bio' products
    df['is_bio'] = df['Nom_Marque_Gamme'].str.contains(
                                                bio_labels,  # Use the regex pattern
                                                flags=re.IGNORECASE,  # Case insensitive matching
                                                na=False  # Handle NaN gracefully
                                                )    
    
    df.drop('Nom_Marque_Gamme', axis=1, inplace=True)

    return df


def verify_quantity_in_name(df):

    # Match if 
    quantity_pattern = r"\b\d+([.,]?\d+)?\s?(mg|g|kg|µg|mcg|µl|ml|l|oz|lb)\b"
    
    # Apply regex to create a column to label 'bio' products
    df['has_quantity'] = df['NomCommercial'].str.contains(
                                                quantity_pattern,  # Use the regex pattern
                                                flags=re.IGNORECASE,  # Case insensitive matching
                                                na=False  # Handle NaN gracefully
                                                )
    
    return df


def save_dataset(df, path, filename, format):

    if format == 'csv':
        df.to_csv(path+filename+'.csv', index=False)
        print(f"File saved as '{path + filename +'.csv'}'")

    if format == 'json':
        ## lower case column names
        new_col_names = [name.lower() for name in df.columns]
        df_json = df.copy()
        df_json.columns = new_col_names
        
        df_json.to_json(path+filename+'.json', orient = 'split', compression = 'infer', index = 'false')
        print(f"File saved as '{path + filename +'.json'}'")

      
def reload_dataset(path, filename):

    if filename.split('.')[1]=='csv':
        df = pd.read_csv(path+filename, sep=',')
        print(f"Re-Loaded from '{path + filename}'")

    if filename.split('.')[1]=='json':
        df = pd.read_json(path+filename, orient ='split', compression = 'infer')
        print(f"Re-Loaded from '{path + filename}'")

    return df