import os
import glob
import warnings

import numpy as np

from numpy import ndarray
from torchxrayvision.utils import normalize


def find_dcm_files(root_folder):
    # Recursively search for all .dcm files in the root folder and subfolders
    dcm_files = glob.glob(os.path.join(root_folder, '**', '*.dcm'), recursive=True)
    return dcm_files


# https://drive.google.com/file/d/15qXjH5uBzTog9_siyctwqd7LA8vWTOmC/view
def read_xray_dcm(path: os.PathLike) -> ndarray:
    """read a dicom-like file and convert to numpy array 

    Args:
        path (PathLike): path to the dicom file

    Returns:
        ndarray: 2D single array image for a dicom image scaled between -1024, 1024
    """
    try:
        import pydicom
    except ImportError:
        raise Exception("Missing Package Pydicom. Try installing it by running `pip install pydicom`.")

    # get the pixel array
    ds = pydicom.dcmread(path, force=True)

    # we have not tested RGB, YBR_FULL, or YBR_FULL_422 yet.
    if ds.PhotometricInterpretation not in ['MONOCHROME1', 'MONOCHROME2']:
        raise NotImplementedError(f'PhotometricInterpretation `{ds.PhotometricInterpretation}` is not yet supported.')

    data = ds.pixel_array
    
    # LUT for human friendly view
    data = pydicom.pixel_data_handlers.util.apply_voi_lut(data, ds, index=0)

    # `MONOCHROME1` have an inverted view; Bones are black; background is white
    # https://web.archive.org/web/20150920230923/http://www.mccauslandcenter.sc.edu/mricro/dicom/index.html
    if ds.PhotometricInterpretation == "MONOCHROME1":
        warnings.warn(f"Coverting MONOCHROME1 to MONOCHROME2 interpretation for file: {path}. Can be avoided by setting `fix_monochrome=False`")
        data = data.max() - data

    # normalize data to [-1024, 1024]
    data = normalize(data, data.max())
    return data


def convert_numpy(obj):
    if isinstance(obj, np.float32):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def add_to_dict(d, patient, study, series, image, res):
    if patient not in d:
        d[patient] = {}
    
    if study not in d[patient]:
        d[patient][study] = {}

    if series not in d[patient][study]:
        d[patient][study][series] = {}

    d[patient][study][series][image] = res