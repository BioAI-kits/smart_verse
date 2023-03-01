import os, sys
import pydicom

for fp, dirs, fs in os.walk(sys.argv[1]):
    outdir = os.path.join('DICOM', fp)
    if len(fs) > 0:
        for f in fs:
            os.makedirs(outdir, exist_ok=True)
            if f.endswith('IMA'):
                img = pydicom.read_file(os.path.join(fp, f))
                dicom_name = f.replace('IMA', 'dicom')
                img.save_as(os.path.join(outdir, dicom_name))