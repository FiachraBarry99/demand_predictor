from math import sqrt

def calculate_score(age, gender, value, minimum_age=0):
    '''
    This is the function that calculates the output score. 
    Change the distribution functions in this function to 
    change how the score is calculated based on age/gender.

    The value parameter is the attribute value of the feature 
    at that particular field.
    '''

    minimum_age = int(minimum_age)

    score = None

    isValidAge = age and age > minimum_age 

    if isValidAge and gender == 'F':
        score = (1/sqrt(age)) * value  # male distribution function
    elif isValidAge and gender == 'M':
        score = (1/sqrt(age)) * value  # female distribution function
    
    if score:
        return score
    else:
        return 0