import pandas as pd
import numpy as np
import re

def apply_formatings(df, format):
    '''
    format dataframe df by applying the formatting steps in formating dict
    '''
    
    if format['lower_case']:     
        df = df.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
    
    if format['remove_redundant_information']:
        df = df.map(remove_redundant_information)
    
    if format['replace_decimal_point']:
        df = df.map(replace_decimal_point)

    if format['replace_commas_in_parenthesis']:
        df = df.map(replace_commas_in_parentheses)
    
    
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




def clean_data(df, steps):
    '''
    Apply the step defined in the step dictionary to the dataset.
    Return the cleaned dataset.
    '''
    
    if steps['drop_duplicates']:
        df.drop_duplicates(inplace = True)
    

    
    return df















