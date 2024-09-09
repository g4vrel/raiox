import os
import json

import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid, ImplicitVRLittleEndian

from script import send_dicom


def create_sr_from_classification(dcm_path, classification_results):
    original_dcm = pydicom.dcmread(dcm_path)

    sr = Dataset()

    # Create file meta information
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.88.22'  # Comprehensive SR
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()
    file_meta.TransferSyntaxUID = ImplicitVRLittleEndian  # You can change this if needed

    # Set the file meta information
    sr.file_meta = file_meta
    sr.is_little_endian = True
    sr.is_implicit_VR = True

    # Copy relevant attributes from the original DICOM
    # Use a list of attributes to copy, and only copy if they exist
    attributes_to_copy = [
        'PatientName', 'PatientID', 'StudyInstanceUID', 'StudyDate', 'StudyTime',
        'AccessionNumber', 'ReferringPhysicianName', 'PatientSex', 'PatientBirthDate'
    ]
    
    for attr in attributes_to_copy:
        if hasattr(original_dcm, attr):
            setattr(sr, attr, getattr(original_dcm, attr))

    # Set SR-specific attributes
    sr.SOPClassUID = '1.2.840.10008.5.1.4.1.1.88.33'  # Comprehensive SR
    sr.SeriesInstanceUID = generate_uid()
    sr.SOPInstanceUID = generate_uid()
    sr.Modality = 'SR'
    sr.SeriesDescription = 'XRay Classification Results'

    # If StudyDate is missing, use current date
    if not hasattr(sr, 'StudyDate'):
        from datetime import date
        sr.StudyDate = date.today().strftime('%Y%m%d')

    # Create the content sequence
    content_seq = Sequence()

    # Add classification results
    for pathology, score in classification_results.items():
        item = Dataset()
        item.RelationshipType = 'CONTAINS'
        item.ValueType = 'NUM'
        item.ConceptNameCodeSequence = Sequence([Dataset()])
        item.ConceptNameCodeSequence[0].CodeValue = pathology
        item.ConceptNameCodeSequence[0].CodingSchemeDesignator = 'LN'  # LOINC
        item.ConceptNameCodeSequence[0].CodeMeaning = f'{pathology} Score'
        item.MeasuredValueSequence = Sequence([Dataset()])
        item.MeasuredValueSequence[0].NumericValue = str(score)
        item.MeasuredValueSequence[0].MeasurementUnitsCodeSequence = Sequence([Dataset()])
        item.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodeValue = '{score}'
        item.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodingSchemeDesignator = 'UCUM'
        item.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodeMeaning = 'Score'
        content_seq.append(item)

    sr.ContentSequence = content_seq

    return sr

if __name__ == '__main__':
    with open('results.json', 'r') as file:
        results = json.load(file)
    
    k = 0
    for (file, res) in results.items():
        sr = create_sr_from_classification(file, res)
        sr.save_as(f'dicom_results/{k}.dcm')
        send_dicom([f'dicom_results/{k}.dcm'])
        k += 1