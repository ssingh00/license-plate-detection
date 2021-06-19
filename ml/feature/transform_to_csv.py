import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import argparse


# Initiate argument parser
parser = argparse.ArgumentParser(
    description="Sample TensorFlow XML-to-CSV converter")
parser.add_argument("-x",
                    "--xml_dir",
                    help="Path to the folder where the input .xml files are stored.",
                    type=str,
                   default=None)
parser.add_argument("-c",
                    "--csv_path",
                    help="Path of output .csv file. If none provided, then no file will be "
                         "written.",
                    type=str, default=None)

args = parser.parse_args()


def xml_to_csv(path):
    """Iterates through all .xml files (generated by labelImg) in a given directory and combines
    them in a single Pandas dataframe.

    Parameters:
    ----------
    path : str
        The path containing the .xml files
    Returns
    -------
    Pandas DataFrame
        The produced dataframe
    """

    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        filename = root.find('filename').text
        width = int(root.find('size').find('width').text)
        height = int(root.find('size').find('height').text)
        for member in root.findall('object'):
            bndbox = member.find('bndbox')
            value = (filename,
                     width,
                     height,
                     member.find('name').text,
                     int(bndbox.find('xmin').text),
                     int(bndbox.find('ymin').text),
                     int(bndbox.find('xmax').text),
                     int(bndbox.find('ymax').text),
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height',
                   'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df




def main():
    examples = xml_to_csv(os.path.join(args.xml_dir,'annotations'))
    if args.csv_path is None:
        args.csv_path = os.path.join(args.xml_dir,'annot_csv')
        if not os.path.exists(args.csv_path):
            os.makedirs(args.csv_path)
        
    examples.to_csv(os.path.join(args.csv_path,f"{args.xml_dir.split('/')[-1]}_cars_dataset.csv"), index=None)
    print('Successfully created the CSV file: {}'.format(args.csv_path))        


if __name__ == '__main__':
    main()