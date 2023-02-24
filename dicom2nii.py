import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import sys, os, argparse


def get_args():
    parser = argparse.ArgumentParser()
    # config
    parser.add_argument('-i', '--input', required=True, help='输入，DICOM文件目录', type=str)
    parser.add_argument('-o', '--output', required=True, help='输出NII文件名前缀，不要加nii.gz', type=str)
    parser.add_argument('-s', '--start_slice', default=150, help='切割slice的起点', type=int)
    parser.add_argument('-e', '--end_slice', default=350, help='切割slice的终点', type=int)
    args = parser.parse_args()
    return args


def get_sagittal_plane(input_dir, output, start_slice=150, end_slice=350):
    """
    input_dir： DICOMs保存的文件目录
    output：输出nii的文件名 
    series_ids_idx: 序列号
    """
    # 读取DICOMs
    reader = sitk.ImageSeriesReader()
    series_ids = reader.GetGDCMSeriesIDs(input_dir)
    assert len(series_ids) == 1, "Input DICOMs {} including multi series {}. Please check it!".format(input_dir, len(series_ids))
    fileNames = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(input_dir, 
                                                              series_ids[0])
    reader.SetFileNames(fileNames)
    image = reader.Execute()
    image_arr = sitk.GetArrayFromImage(image)
    spacing = image.GetSpacing()
    origin = image.GetOrigin()
    direction = image.GetDirection()
    x, y, z = direction[:3], direction[3:6], direction[6:]

    # 交换维度
    for swap in ['0-2', '0-1', '1-2']:
        if swap == '0-2':
            image_new = sitk.Image()
            image_arr_new = image_arr.swapaxes(0,2)  
            image_arr_new = image_arr_new[start_slice:end_slice, :,:] 
            image_new = sitk.GetImageFromArray(image_arr_new)
            image_new.SetDirection((*z, *y, *x))
            image_new.SetSpacing(spacing)
            image_new.SetOrigin(origin)
            sitk.WriteImage(image_new, output + '_swap02_0000.nii.gz')
        elif swap == '0-1':
            image_new = sitk.Image()
            image_arr_new = image_arr.swapaxes(0,1)  
            image_arr_new = image_arr_new[start_slice:end_slice, :,:] 
            image_new = sitk.GetImageFromArray(image_arr_new)
            image_new.SetDirection((*y, *x, *z))
            image_new.SetSpacing(spacing)
            image_new.SetOrigin(origin)
            sitk.WriteImage(image_new, output + '_swap01_0000.nii.gz')
        elif swap == '1-2':
            image_new = sitk.Image()
            image_arr_new = image_arr.swapaxes(0,1) 
            image_arr_new = image_arr_new[start_slice:end_slice, :,:] 
            image_new = sitk.GetImageFromArray(image_arr_new)
            image_new.SetDirection((*x, *z, *y))
            image_new.SetSpacing(spacing)
            image_new.SetOrigin(origin)
            sitk.WriteImage(image_new, output + '_swap12_0000.nii.gz')
    
    return image, image_new


if __name__ == '__main__':
    args = get_args()
    input_dir = args.input
    output = args.output
    start_slice = args.start_slice
    end_slice = args.end_slice

    get_sagittal_plane(input_dir=input_dir, output=output, start_slice=start_slice, end_slice=end_slice)
