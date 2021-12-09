import re

def create_dict(fieldname_list):
    '''
    This is a function which parses the field names and stores the result in a dictionary. The dictionary is formtted with
    the key being the field index and the value being another dictionary containing the age and the gender (F for female 
    and M for male)

    If you wish to expand this model to use other sources of data (anything besides Irish census data) then this function 
    must be changed to parse the new format.
    '''

    dict_result = {}

    for index, field_name in enumerate(fieldname_list):

        # search the field names for fields that match the pattern 
        # below which finds the fields with only single age numbers not ranges
        single_match = re.match(r'T1_1AGE(\d+)(F|M)', field_name)

        # if there is a match store that match in the dict_result 
        # as the key and the single number as the value
        if single_match:
            dict_result[index] = {'age': int(single_match.group(1)), 'gender': single_match.group(2)}

        
        # search the field names for fields that match the pattern below 
        # which finds the fields with age ranges not single numbers given
        range_match = re.match(r'T1_1AGE(\d+)_(\d+)(F|M)', field_name)

        # if there is a match store that match in the dict_result 
        # as the key and the average/middle value of the range as the value
        if range_match:
            range_start = int(range_match.group(1))
            range_end = int(range_match.group(2))
            
            dict_result[index] = {'age': (range_start + range_end)/2, 'gender': range_match.group(2)}


    return dict_result