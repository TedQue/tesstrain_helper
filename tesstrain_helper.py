#!/usr/bin/env python3
import sys
import argparse
import os
import os.path
from PIL import Image

APP_NAME = 'Tesstrain Helper'
VERSION = '0.0.1'

# 读入输入目录的图片,经过灰度,二值化后以 tif 格式写入输出目录
# 输入图片的文件名为图片内容,同时生成图片内容 .gt.txt 文件也写入输出目录

# 转灰度
def image_grayscale(im):
	return im.convert("L")

# 二值化并反转(白底黑字)
def image_binarization(im, threshold=127):
	im2 = im.copy()
	pixdata = im2.load()
	w, h = im2.size
	for y in range(h):
		for x in range(w):
			if pixdata[x, y] < threshold:
				pixdata[x, y] = 0
			else:
				pixdata[x, y] = 255
	return im2

def get_vertial_pixel_count(pixdata, x, h):
	c = 0
	for y in range(h):
		if pixdata[x, y] == 0:
			c += 1
	return c

def image_split(im, blank_line_max_pixel=1, end_line_width=2):
	sub_ims = []
	pixdata = im.load()
	w, h = im.size
	x0 = 0
	st_find_start = 0
	st_find_end = 1
	st = st_find_start
	end_line_count = 0
	for x in range(w):
		if st == st_find_start:
			# 找到字符的开始的 x 坐标(在此 x 坐标下 h 个像素至少有 1 个点有效)
			if get_vertial_pixel_count(pixdata, x, h) >= blank_line_max_pixel:
				st = st_find_end
				end_line_count = 0
		elif st == st_find_end:
			# 找到字符的结束的 x 坐标(连续 N 个像素宽度的竖线都没有有效点)
			if get_vertial_pixel_count(pixdata, x, h) >= blank_line_max_pixel:
				end_line_count = 0
			else:
				end_line_count += 1
				if end_line_count >= end_line_width:
					st = st_find_start
					sub_ims.append(im.crop((x0, 0, x, h)))
					x0 = x
		else:
			assert 0, f'unexepct state: {st}'
	
	# 最后一个字符
	if st == st_find_end:
		sub_ims.append(im.crop((x0, 0, w, h)))

	return sub_ims

if __name__ == "__main__":
	# commander line args
	arg_parser = argparse.ArgumentParser(
		prog='tesstrain_helper.py',
		description='generate .tif and .gt.txt from input images',
		epilog=f'{APP_NAME} v{VERSION} (C) powered by Que\'s C++ Studio'
	)
	arg_parser.add_argument("input_dir", help=".jpg or .png images input directory")
	arg_parser.add_argument("output_dir", help=".tif and .gt.txt output directory")
	arg_parser.add_argument("-n", "--dry-run", help="do not generate output file", action="store_true")
	arg_parser.add_argument("-s", "--split", help="split image into single characters", action="store_true")
	args = arg_parser.parse_args()

	print(f'Welcome to {APP_NAME} v{VERSION} by Que\'s C++ Studio')
	print(f'generation begin, {args.input_dir} -> {args.output_dir} ...')

	input_files = os.listdir(args.input_dir)
	output_file_count = 0
	for ifn in input_files:
		with Image.open(os.path.join(args.input_dir, ifn)) as im:
			# 根据文件名提取图片内容,格式为 <content>_xxx.jpeg
			nm, ext = os.path.splitext(ifn)
			content = nm.partition('_')[0]

			# 灰度二值化
			im_gray = image_grayscale(im)
			im_bin = image_binarization(im_gray)

			if args.split:
				for i, sub_im in enumerate(image_split(im_bin)):
					ofn_tif = f'{nm}_{i}.tif'
					if not args.dry_run:
						sub_im.save(os.path.join(args.output_dir, ofn_tif))

					ofn_gt_txt = f'{nm}_{i}.gt.txt'
					if not args.dry_run:
						with open(os.path.join(args.output_dir, ofn_gt_txt), "w", encoding='utf-8') as f:
							f.write(content[i])

					output_file_count += 1
					print(f'{ifn} -> {ofn_tif}, {ofn_gt_txt}("{content[i]}")')
			else:
				# 存为 tif 格式
				ofn_tif = f'{nm}.tif'
				if not args.dry_run:
					im_bin.save(os.path.join(args.output_dir, ofn_tif))

				# 生成 utf-8 编码的内容 .gt.txt 文件
				ofn_gt_txt = f'{nm}.gt.txt'
				ofn_tif = f'{nm}.tif'
				if not args.dry_run:
					with open(os.path.join(args.output_dir, ofn_gt_txt), "w", encoding='utf-8') as f:
						f.write(content)
				
				output_file_count += 1
				print(f'{ifn} -> {ofn_tif}, {ofn_gt_txt}("{content}")')

	print(f'done, {len(input_files)} input images parsed, {output_file_count} output images generated')
	print('Bye')
