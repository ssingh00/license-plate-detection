import os
import re
from shutil import copyfile
import argparse
import math
import random
from google.cloud import storage

storage_client = storage.Client()




def create_copy(source_file,dest_file, filename, gcs=False):
    if gcs:
        source_bucket = storage_client.bucket(source_file.split('/')[2])
        source_blob = source_bucket.blob(os.path.join(*source_file.split('/')[3:]))
        destination_bucket = storage_client.bucket(dest_file.split('/')[2])
        blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket,os.path.join(*dest_file.split('/')[3:]))
    else:
        copyfile(source_file,dest_file)
        
    

def iterate_dir(source, dest, ratio, copy_xml, gcs):
    images=[]
    source = source.replace('\\', '/')
    dest = dest.replace('\\', '/')
    train_dir = os.path.join(dest, 'train')
    test_dir = os.path.join(dest, 'test')
    
    if not gcs:
        if not os.path.exists(train_dir):
            os.makedirs(os.path.join(train_dir, 'images'))
            os.makedirs(os.path.join(train_dir, 'annotations'))
        if not os.path.exists(test_dir):
            os.makedirs(os.path.join(test_dir, 'images'))
            os.makedirs(os.path.join(test_dir, 'annotations'))

        images = [f for f in os.listdir(os.path.join(source, 'images')) 
                  if re.search(r'([a-zA-Z0-9\s_\\.\-\(\):])+(?i)(.jpg|.jpeg|.png)$', f)]
    else:
        prefix = "/".join(source.split('/')[3:])+'/images/'
        for blob in storage_client.list_blobs(source.split('/')[2], prefix=prefix):
            images.append(blob.name.replace(prefix, ""))
        
        
    
    num_images = len(images)
    num_test_images = math.ceil(ratio*num_images)
    
    for i in range(num_test_images):
        idx = random.randint(0, len(images)-1)
        filename = images[idx]
        create_copy(os.path.join(source,'images', filename),
                 os.path.join(test_dir,'images', filename),filename, gcs)
        if copy_xml:
            xml_filename = os.path.splitext(filename)[0]+'.xml'
            create_copy(os.path.join(source, 'annotations', xml_filename),
                     os.path.join(test_dir,'annotations', xml_filename),xml_filename, gcs)
        images.remove(images[idx])

    for filename in images:
        create_copy(os.path.join(source, 'images', filename),
                 os.path.join(train_dir, 'images', filename),filename,gcs)
        if copy_xml:
            xml_filename = os.path.splitext(filename)[0]+'.xml'
            create_copy(os.path.join(source, 'annotations', xml_filename),
                     os.path.join(train_dir, 'annotations', xml_filename),xml_filename,gcs)


def main():

    # Initiate argument parser
    parser = argparse.ArgumentParser(description="Partition dataset of images into training and testing sets",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-i', '--imageDir',
        help='Path to the folder where the image dataset is stored. If not specified, the CWD will be used.',
        type=str,
        default=os.getcwd()
    )
    parser.add_argument(
        '-o', '--outputDir',
        help='Path to the output folder where the train and test dirs should be created. '
             'Defaults to the same directory as IMAGEDIR.',
        type=str,
        default=None
    )
    parser.add_argument(
        '-r', '--ratio',
        help='The ratio of the number of test images over the total number of images. The default is 0.1.',
        default=0.1,
        type=float)
    parser.add_argument(
        '-x', '--xml',
        help='Set this flag if you want the xml annotation files to be processed and copied over.',
        default=True,
        type=bool
    )
    parser.add_argument(
        '-g', '--gcs',
        help='Set this flag if you want to use gcs bucket',
        default=False,
        type=bool
    )
    args = parser.parse_args()
    
    if args.gcs and args.imageDir==os.getcwd():
        print(f"Provide Google cloud storage path as --imageDir=gs://XXXXX-XXXX-XX/data")

    if args.outputDir is None:
        args.outputDir = args.imageDir

    # Now we are ready to start the iteration
    iterate_dir(args.imageDir, args.outputDir, args.ratio, args.xml, args.gcs)


if __name__ == '__main__':
    main()