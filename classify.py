import json

import numpy as np

import torchxrayvision as xrv
import skimage, torch, torchvision

from utils import (read_xray_dcm, 
                   find_dcm_files,
                   convert_numpy,
                   add_to_dict)


transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),
                                            xrv.datasets.XRayResizer(224)])


def convert_dicom(file):
    img = read_xray_dcm(file)
    img = np.expand_dims(img, axis=0) # (1, 224, 224)
    img = transform(img)
    return torch.from_numpy(img)


if __name__ == '__main__':
    model = xrv.models.DenseNet(weights="densenet121-res224-all")

    batch = []

    files = find_dcm_files('data')
    for file in files:
        with open(file, 'rb') as f:
            dicom = f.read()
            img = convert_dicom(file)
            batch.append(img)
    
    batch = torch.stack(batch) # (B, 1, 224, 224) 

    assert len(files) == batch.shape[0], 'Batch dim should equal the number of files'
    assert batch.shape[1:] == (1, 224, 224), 'Wrong shape'

    with torch.inference_mode():
        outputs = model(batch)

    results = []
    for dim in range(len(files)):
        result = dict(zip(model.pathologies, outputs[dim].numpy()))
        results.append(result)

    results_dict = {}

    for path, res in zip(files, results):
        results_dict[path] = res

    with open('results.json', 'w') as json_file:
        json.dump(results_dict, json_file, indent=4, default=convert_numpy)