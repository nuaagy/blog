from random import randint, choice
import string
import os
from functools import partial
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from BBS import settings
path = os.path.join(settings.BASE_DIR, 'static', 'font', 'kumo.ttf')
def check(width=120, height=30, length=4, font_file=path, font_size=28):
	code = []
	img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
	draw = ImageDraw.Draw(img, mode='RGB')
	font = ImageFont.truetype(font_file, font_size)
	x = partial(randint, 0, width)
	y = partial(randint, 0, height)
	def char():
		return choice(string.ascii_letters + string.digits)
	def color():
		return (randint(0, 255), randint(0, 255), randint(0, 255))

	for i in range(length):
		ch = char()
		co = color()
		code.append(ch)
		h = randint(0, 4)
		draw.text([i * width / length, h], ch, font=font, fill=co)

	# 噪点
	for i in range(25):
		draw.point([x(), y()], fill=color())

	# 画圆
	for i in range(25):

		draw.arc((x(), y(), x()+4, y()+4), 0, 90, fill=color())

	# 画线
	for i in range(3):
		draw.line((x(), y(), x(), y()), fill=color())

	img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
	return img, ''.join(code)


if __name__ == '__main__':
	img, code = check()
	# img.show()

	# 写入文件
	with open('code.png', 'wb') as f:
		img.save(f, 'png')

	# 写入内存 PY3
	# from io import BytesIO
	# stream = BytesIO()
	# img.save(stream, 'png')
	# stream.getvalue()

