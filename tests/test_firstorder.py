# to run this test, from directory above:
# setenv PYTHONPATH /path/to/pyradiomics/radiomics
# nosetests --nocapture -v tests/test_firstorder.py

from radiomics import firstorder, imageoperations
from testUtils import RadiomicsTestUtils
import sys, os
import logging
from nose_parameterized import parameterized
from itertools import product

testUtils = RadiomicsTestUtils('firstorder')
firstOrderFeatures = None

def setup_module(module):
    # runs before anything in this file
    print ("") # this is to get a newline after the dots
    return

class TestFirstOrder:

    #
    # Generate the test cases that test each feature for each test case / data
    # set.
    # The custom function name generation utility ensures that all the features
    # are tested for one data set before moving on to calculating features for
    # another data set.
    #
    def generate_scenarios():
      global testUtils
      # get the list of test cases for which we have baseline information
      testCases = testUtils.getTestCases()
      logging.info('generate_scenarios: testCases = %s', testCases)

      # get the list of LoG sigma values for which we have baseline information
      sigmas = [0.0] + testUtils.getLaplacianSigmas()
      logging.info('generate_scenarios: sigmas = %s', sigmas)

      # get the list of features we'll be testing so we can generate the
      # tuples of testcase:sigma:feature to iterate over
      featureNames = firstorder.RadiomicsFirstOrder.getFeatureNames()
      logging.info('generate_scenarios: featureNames = %s', featureNames)
      test_tuples = []
      for test_tuple in product(testCases, sigmas, featureNames):
        test_tuples.append(test_tuple)
      logging.info('generate_scenarios: test_tuples = %s', test_tuples)

      for test_tuple in test_tuples:
        yield test_tuple

    global testUtils
    @parameterized.expand(generate_scenarios(), testcase_func_name=testUtils.custom_name_func)
    def test_scenario(self, testCase, sigma, featureName):
      print("")
      global testUtils
      logging.info('test_scenario: testCase = %s, sigma = %f, featureName = %s', testCase, sigma, featureName)
      # set the test case and only recalculate features if there are changes
      testCaseChanged = testUtils.setTestCase(testCase)
      testImage = testUtils.getImage()
      # if it's a new test case or the sigma changed, rerun LoG
      sigmaChanged = testUtils.setSigma(sigma)
      if testCaseChanged or sigmaChanged:
        logging.info('test_scenario: recalculating LoG with sigma %f', sigma)
        # relies on applyLoG returning the image unchanged if sigma is 0.0
        logImage = imageoperations.applyLoG(testImage, sigma)
        testImage = logImage
      global firstOrderFeatures
      if firstOrderFeatures == None or testCaseChanged or sigmaChanged:
        logging.info("Instantiating FirstOrder for testCase %s/", testCase)
        firstOrderFeatures = firstorder.RadiomicsFirstOrder(testImage, testUtils.getMask())

      firstOrderFeatures.disableAllFeatures()
      firstOrderFeatures.enableFeatureByName(featureName)
      firstOrderFeatures.calculateFeatures()
      # get the result and test it
      val = firstOrderFeatures.featureValues[featureName]
      testUtils.checkResult(featureName, val)

