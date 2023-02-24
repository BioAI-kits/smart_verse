import SimpleITK as sitk
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import os 


def get_contours(seg_img:str, photo_img:str, height:int, width:int, adjust=True):
    im = cv.imread(seg_img)
    im = cv.resize(im, (width, height))    
    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    # 选择面积最大的轮廓
    max_area, max_area_idx = 0, 0
    for i in range(len(contours)):
        area = cv.contourArea(contours[i], False)
        if area > max_area:
            max_area = area
            max_area_idx = i
    max_area, max_area_idx
    
    # 只保留轮廓图
    mask = np.zeros_like(imgray)
    img = cv.drawContours(mask, contours, max_area_idx, 255, 3)
    
    # 删除右侧、头部、腿部的轮廓，只保留背部（要求图片面朝右）
    if adjust == True:
        img[:img.shape[0] // 5,:] = 0
        img[img.shape[0] // 5 *4:,:] = 0
        img[:,img.shape[1] //2:] = 0
    
    # 轮廓映射回原始照片
    im_raw = cv.imread(photo_img)
    im_raw = cv.cvtColor(im_raw, cv.COLOR_BGR2GRAY)
    im_raw = cv.resize(im_raw, (width, height))    
    img_raw = cv.drawContours(im_raw, contours, max_area_idx, 255, 3)
    
    return img, img_raw


def merge_img(verse:str, photo_seg:str, photo:str, outdir:str):
    """ 
    verse: 脊柱CT分割后的图 nii.gz， 如 ./dataset/CHENGNAILONG_bend_CT1_swap01.nii.gz
    photo_seg: 人体抱膝照片分割的图片， png 格式
    photo： 人体抱膝照片 jpg 或png
    outdir: 融合人体抱膝分割轮廓和脊柱CT分割图的结果,保存的文件夹，nii.gz
    """
    
    img_itk = sitk.ReadImage(verse)
    
    img_arr = sitk.GetArrayFromImage(img_itk)
    slices, height, width = img_arr.shape[0], img_arr.shape[1], img_arr.shape[2]
    
    # 获取轮廓
    img, img_raw = get_contours(photo_seg, photo, height=height, width=width)
    
    # 我们把第一张slice替换为轮廓
    img_arr[0] = img
    
    # 创建新的图
    img_new = sitk.GetImageFromArray(img_arr)
    img_new.SetDirection(img_itk.GetDirection())
    img_new.SetSpacing(img_itk.GetSpacing())
    img_new.SetOrigin(img_itk.GetOrigin())
    
    # 保存新的图
    os.makedirs(outdir, exist_ok=True)
    figname = os.path.join(outdir, os.path.basename(verse).replace('.nii.gz', '_0000.nii.gz'))
    sitk.WriteImage(img_new,figname)


if __name__ == '__main__':

    merge_img(verse='./dataset/CHENGNAILONG_bend_CT1_swap01.nii.gz', photo='./dataset/bend(1).jpg', photo_seg='./dataset/bendcom.png', outdir='output')
    