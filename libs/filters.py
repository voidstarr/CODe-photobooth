from PIL import Image


class Filters():
    @staticmethod
    def rgb3(file):
        img = Image.open(file)
        pixels = img.load()
        w = 5
        h = 5
        for i in range(0,img.size[0],5):
            for j in range(0,img.size[1],5):
                r = pixels[i,j][0]*(1.5 if (i//w+j//h)%3 == 0 else 1.1)
                r = 255 if r > 255 else int(r)
                g = pixels[i,j][1]*(2.0 if (i//w+j//h)%3 == 1 else 0)
                g = 255 if g > 255 else int(g)
                b = pixels[i,j][2]*(1.5 if (i//w+j//h)%3 == 2 else 1.1)       
                b = 255 if b > 255 else int(b)
                pixels[i,j] = (r,g,b)
        img.save(file)
    
    @staticmethod
    def rps2(file):
        img = Image.open(file)
        pixels = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                pixels[i,j] = (pixels[i,j][2],pixels[i,j][0],pixels[i,j][1])
        img.save(file)

    @staticmethod
    def rps(file):
        img = Image.open(file)
        pixels = img.load()
        cpixels = img.load()
        w = img.size[1] / 6
        h = img.size[0] / 6

        something = 400
        for i in range(img.size[0]):
            img_reg_x = i % w + 1
            for j in range(img.size[1]):
                img_reg_y = (j+img_reg_x/(j+1)) % h + 1
                R = translate(pixels[(i+img_reg_x)%img.size[0],(j+img_reg_y)%img.size[1]][0] * (i//(j+10) + something / img_reg_y), 0, 1500, 0, 255)
                G = translate(pixels[(i+img_reg_x)%img.size[0],(j+img_reg_y)%img.size[1]][1] * (j//(i+2) + something / img_reg_y), 0, 1500, 0, 255)
                B = translate(pixels[(i+img_reg_x)%img.size[0],(j+img_reg_y)%img.size[1]][2] * ((j+i)//(2+j*i//100) + something / img_reg_y), 0, 1000, 0, 255)
                pixels[i, j] = (G, R, R)
        img.save(file)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))
