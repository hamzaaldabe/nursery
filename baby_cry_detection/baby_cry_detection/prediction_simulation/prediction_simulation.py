# -*- coding: utf-8 -*-

import argparse
import logging
import os
import pickle
import timeit
import warnings

from baby_cry_detection.rpi_methods import Reader
from baby_cry_detection.rpi_methods.feature_engineer import FeatureEngineer
from baby_cry_detection.rpi_methods.majority_voter import MajorityVoter

from baby_cry_detection.rpi_methods.baby_cry_predictor import BabyCryPredictor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_path_data',
                        default='{}/../../'.format(
                            os.path.dirname(os.path.abspath(__file__))))
    parser.add_argument('--load_path_model',
                        default='{}/../../output/model/'.format(
                            os.path.dirname(os.path.abspath(__file__))))
    parser.add_argument('--save_path',
                        default='{}/../prediction/'.format(os.path.dirname(os.path.abspath(__file__))))

    # Arguments
    args = parser.parse_args()
    load_path_data = os.path.normpath(args.load_path_data)
    load_path_model = os.path.normpath(args.load_path_model)
    file_name = 'recorded.wav'
    save_path = os.path.normpath(args.save_path)

    # READ RAW SIGNAL

    start = timeit.default_timer()

    # Read signal (first 5 sec)
    file_reader = Reader(os.path.join(load_path_data, file_name))

    play_list = file_reader.read_audio_file()

    stop = timeit.default_timer()

    # FEATURE ENGINEERING

    start = timeit.default_timer()

    # Feature extraction
    engineer = FeatureEngineer()

    play_list_processed = list()

    for signal in play_list:
        tmp = engineer.feature_engineer(signal)
        play_list_processed.append(tmp)

    stop = timeit.default_timer()

    # MAKE PREDICTION

    logging.info('Predicting...')
    start = timeit.default_timer()

    # https://stackoverflow.com/questions/41146759/check-sklearn-version-before-loading-model-using-joblib
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)

        with open((os.path.join(load_path_model, 'model.pkl')), 'rb') as fp:
            model = pickle.load(fp)

    predictor = BabyCryPredictor(model)

    predictions = list()

    for signal in play_list_processed:
        tmp = predictor.classify(signal)
        predictions.append(tmp)

    # MAJORITY VOTE

    majority_voter = MajorityVoter(predictions)
    majority_vote = majority_voter.vote()

    stop = timeit.default_timer()

    print(majority_vote)


if __name__ == '__main__':
    main()
