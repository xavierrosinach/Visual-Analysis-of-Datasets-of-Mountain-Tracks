from preprocessing import main_preprocessing
from fmm_algorithm import main_fmm
from postprocessing import main_postprocessing
from edges_postprocessing import main_edges_postprocessing

# Main function - calls all zones
def main():

    # Define the data path
    data_path = '../../Data'

    # Canigo
    main_preprocessing(data_path, 'canigo')
    main_fmm(data_path, 'canigo')
    main_postprocessing(data_path, 'canigo')
    main_edges_postprocessing(data_path, 'canigo')

    # Matagalls
    main_preprocessing(data_path, 'matagalls')
    main_fmm(data_path, 'matagalls')
    main_postprocessing(data_path, 'matagalls')
    main_edges_postprocessing(data_path, 'matagalls')

    # Vall Ferrera
    main_preprocessing(data_path, 'vallferrera')
    main_fmm(data_path, 'vallferrera')
    main_postprocessing(data_path, 'vallferrera')
    main_edges_postprocessing(data_path, 'vallferrera')

    # Example - Matagalls subset
    main_preprocessing(data_path, 'exemple')
    main_fmm(data_path, 'exemple')
    main_postprocessing(data_path, 'exemple')
    main_edges_postprocessing(data_path, 'exemple')

main()