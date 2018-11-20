# -*- coding:utf-8 -*-

import base64
import cStringIO
import random
import string

from PIL import Image,ImageDraw,ImageFont,ImageFilter

class CodeGenerator(object):

    def __init__(self, size=(100,30), len=4, lines=5, source=string.letters + string.digits):
        self.size = size
        self.codeLen = len
        self.lines = lines
        self.source = source
        self.buffer = cStringIO.StringIO()

    def _randColor(self, min=0, max=255):
        return tuple([random.randint(min,max)] * 3)

    def _generateText(self):
        return ''.join(random.sample(self.source, self.codeLen))

    def _drawLine(self, draw, width, height):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([start,end], fill=self._randColor())

    def _imageAffine(self, image, *args):
        width, height, offsetX, offsetY = args
        return image.transform((width+offsetX, height+offsetY), Image.AFFINE,
                               (1, random.uniform(-0.1, 0.1), 0, random.uniform(-0.1,0.1), 1, 0), Image.LINEAR)

    def generateCode(self):
        width, height = self.size
        image = Image.new('RGB', self.size, self._randColor(min=150))
        font = ImageFont.truetype('arial.ttf', 28)
        draw = ImageDraw.Draw(image)
        self.text = self._generateText()
        fontWidth, fontHeight = font.getsize(self.text)
        draw.text(
            ((width - fontWidth) / self.codeLen ,(height - fontHeight) / self.codeLen),
            self.text,font=font, fill=self._randColor(max=150)
        )
        for i in range(self.lines):
            self._drawLine(draw, width, height)

        image = self._imageAffine(image,width, height, random.randint(-2,3), random.randint(-2,3))
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        image.save(self.buffer, format='JPEG')
        return base64.b64encode(self.buffer.getvalue())

    def getText(self):
        return self.text


