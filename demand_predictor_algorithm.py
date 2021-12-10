# -*- coding: utf-8 -*-

"""
/***************************************************************************
 DemandPredictor
                                 A QGIS plugin
 This plugin takes in Irish census data as a csv and then according to the distribution function provided it predicts demand for small areas
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-12-06
        copyright            : (C) 2021 by Fiachra Barry
        email                : fiachrabarry@gmail.com
 ***************************************************************************/
"""

__author__ = 'Fiachra Barry'
__date__ = '2021-12-06'
__copyright__ = '(C) 2021 by Fiachra Barry'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import (QCoreApplication, QVariant)
from qgis.core import (QgsProcessing,
                       QgsField,
                       QgsFields,
                       QgsFeature,
                       QgsFeatureRequest,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString)
from math import *
import re

def calculate_score(male_func, female_func, age, gender, value, minimum_age=0, area=1):
    '''
    This is the function that calculates the output score. 
    Change the distribution functions in this function to 
    change how the score is calculated based on age/gender.

    The value parameter is the attribute value of the feature 
    at that particular field.
    '''

    # ensure minimum age is the right data type
    minimum_age = int(minimum_age)

    # check is the age parameter valid
    isValidAge = age and age > minimum_age 

    # calculate score based on area. gender and value
    if isValidAge and gender == 'F':
        score = ((eval(male_func)) * value)/area  # male distribution function
        return score
    elif isValidAge and gender == 'M':
        score = ((eval(female_func)) * value)/area  # female distribution function
        return score
    else:
        return 0
    


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


class DemandPredictorAlgorithm(QgsProcessingAlgorithm):

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    MALE_DIST_FUNCTION = 'MALE_DIST_FUNCTION'
    FEMALE_DIST_FUNCTION = 'FEMALE_DIST_FUNCTION'
    MINIMUM_AGE = 'MINIMUM_AGE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # add male and female distribution function parameters
        self.addParameter(
            QgsProcessingParameterString(
                self.MALE_DIST_FUNCTION,
                self.tr('Male Distribution Function'),
                "Function can be written using any of Python's math module but must use <age> as the variable",
                )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FEMALE_DIST_FUNCTION,
                self.tr('Female Distribution Function'),
                "Examples: 1/sqrt(age), (1/(20*sqrt(2*pi)))*exp(((age-22)**2)/(2*20**2))"
                )
        )

        # add a minimum age variable
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MINIMUM_AGE,
                self.tr('Minimum Age'),
                defaultValue = 0,
                minValue = 0,
                maxValue = 120
                )
        )        

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # get minimum age
        mini_age = self.parameterAsInt(parameters, self.MINIMUM_AGE, context)

        # get distribution functions
        male_dist = self.parameterAsString(parameters, self.MALE_DIST_FUNCTION, context)
        female_dist = self.parameterAsString(parameters, self.FEMALE_DIST_FUNCTION, context)

        # get input
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # create score field
        output_fields = QgsFields()
        output_fields.append(QgsField('Name', QVariant.String))
        output_fields.append(QgsField('Score', QVariant.Double))

        # create output
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context, output_fields, source.wkbType(), source.sourceCrs())


        # Compute the number of steps to display within the progress bar and
        # get features from source without geometry
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry))

        # create dictionary to store field index and the estimated age 
        # associated with the field as key value pairs
        fieldindex_age_dict = create_dict(source.fields().names())

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # initialise score for each feature
            score = 0

            # get attrbutes
            attrs = feature.attributes()

            # loop through attributes of feature
            for index, val in enumerate(attrs):

                # initialise age and gender
                age = None
                gender = None

                # get age and gender from the previously created dictionary
                try:
                    age = fieldindex_age_dict[index]['age']
                except:
                    pass

                try:
                    gender = fieldindex_age_dict[index]['gender']
                except:
                    pass
                
                # calculate score based on age and gender using previously created function
                score += calculate_score(male_dist, female_dist, age, gender,
                                         val, minimum_age = mini_age, area = feature['Shape__Area'])

            # set score and name attributes
            new_feature = QgsFeature(output_fields)
            new_feature.setAttribute('Score', score)
            try:
                new_feature.setAttribute('Name', feature['EDName'])
            except:
                pass
            
            # set new_feature geometry
            new_feature.setGeometry(feature.geometry())

            # Add a feature in the sink
            sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Demand Predictor'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return DemandPredictorAlgorithm()
