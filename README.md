# Mandala MMS Image Importer
A Python package to import images from MMS into the Mandala Images site. The process involves two steps:

1. Importing metadata from MMS into the Drupal site
2. Rsyncing already converted images on the IIIF from their old names to the new ones

MMS has an api endpoint that returns JSON or XML. This is used by Drupal to import the metadata and return a new 
name for the image based on its Shanti Image ID (siid). This script takes an MMS ID or range of IDs and calls the 
Drupal endpoint for conversion (which is only available to admins), authenticating with the appropriate cookie. 
The endpoint returns json data which includes the new name for the file, and this script creates and, if chosen, 
executes the rsync command to put the file on the IIIF server. There is a special endpoint url on the IIIF server 
to distribute the image into its proper folder, which must be called after the conversion is done.

All MMS images (except corrupted ones) have been convert and are on the production IIIF server in folders based on 
their IDs. There are about 70000, and there are folders 0 through 7 which each contain images 0000.jp2 to 9999.jp2 
The folder number plus the image number represents the MMS ID. So image 12345.jp2 is at prod/0001/2345.jp2. The folders 
on the IIIF server for Mandala are "/test/" and "/prod/".

## Requirements
- Python 3.x+
- virtualenv (reccomended)

## Install
-   `pip install -r requirements.txt`

## Running 
- Run:
```
python import.py -t MMS -c {COOKIE} -hm {Full Destination Domain} -i {the ID of the MMS image to import}
```

The "Full Destination Domain" is the domain of the Drupal site into which the metadata is being imported, such as 
"https://images.mandala.virginia.edu"

- Non-required by important options:
  - `-coll` : the ID for the Images Collection in Drupal to which the new image should be added
  - `-p`    : the name of the default photographer to assign to the image, if the data is not in MMS
  - `-rs`   : whether to automatically rsync the image in the IIIF server (for MMS only)
  - `-d`    : the destination IIIF server, either `test` or `prod`, defaults to `test`

Run `python import.py` for a full list of supported arguments.
