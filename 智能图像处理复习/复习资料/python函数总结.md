# Python图像处理函数

> ```python
> import cv2
> ```

## 读取图像

```python
# 灰度图
image = cv2.imread('n.png', cv2.IMREAD_GRAYSCALE)
# 彩色图
image = cv2.imread('n.png', cv2.IMREAD_COLOR)
```

## 显示图像

```python
cv2.imshow('window_name', image)
cv2.waitKey(0)	# 等待用户按键关闭窗口
```

## 显示分辨率

```python
# 灰度图
height, width = image.shape
print(f"图像分辨率：{width} x {height}")
# 彩色图
height, width, channels = image.shape
print(f"图像分辨率：{width} x {height}")
```

## 滤波

> 滤波器大小：k_size

```python
k_size = 5

# 边缘补0
# opencv2的medianBlur默认为镜像填充
pad = k_size // 2
padded_image = cv2.copyMakeBorder(image, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)

# 中值滤波
filtered_image = cv2.medianBlur(padded_image, k_size)		# 这里必须是一个奇数！
# 均值滤波
filtered_image = cv2.blur(padded_image, (k_size, k_size))	# 这里必须是数对！

# 去除填充的边缘部分
filtered_image = filtered_image[pad:-pad, pad:-pad]
```

## 分割

```python
# 应用最大类间方差算法（Otsu's method）进行图像二值化
# 第一个返回值 threshold_value 是阈值（在 Otsu 方法中自动计算），第二个返回值 binary_image 是二值化后的图像
# 阈值设置为 0（或任意值），因为 Otsu 方法会自动计算最佳的阈值
# 最大值为255，表示在二值化后，大于阈值的像素将被设置为这个值（白色）
threshold_value, binary_image = cv2.threshold(filtered_image, 0, 255, cv2.THRESH_OTSU)
```

## 保存

```python
# 保存处理后的图像
cv2.imwrite('save_name.png', binary_image)
```



## 图像变换

> ```python
> import matplotlib.pyplot as plt
> import numpy as np
> ```

### FFT（快速傅里叶）

```python
# 二维傅里叶正变换
f_transform = np.fft.fft2(image)
f_transform_shifted = np.fft.fftshift(f_transform)

# 显示变换后的系数矩阵的幅度谱
magnitude_spectrum = 20 * np.log(np.abs(f_transform_shifted))
plt.imshow(magnitude_spectrum, cmap='jet')
plt.title('FFT Magnitude Spectrum')
plt.show()

# 二维傅里叶逆变换
f_inverse_shifted = np.fft.ifftshift(f_transform_shifted)
image_restored = np.fft.ifft2(f_inverse_shifted).real
```

### DCT（离散余弦）

```python
# 二维离散余弦正变换
dct_transform = cv2.dct(np.float32(image))

# 显示变换后的系数
dct_transform_scaled = np.log(np.abs(dct_transform) + 1)  # 对变换后的系数取对数以增强可视化效果
plt.imshow(dct_transform_scaled, cmap='jet')
plt.title('DCT Coefficients')
plt.show()

# 二维离散余弦逆变换
image_restored = cv2.idct(dct_transform).astype(np.uint8)
```

### DHT（离散哈达玛）

```python
# 递归构建Hadamard矩阵
def hadamard(n):
    if n == 1:
        return np.array([[1]])
    else:
        H = hadamard(n // 2)
        H_n = np.block([[H, H], [H, -H]])
        return H_n
        
# 哈达玛正变换函数
def hadamard_transform(image):
    # 获取图像的行数和列数
    rows, cols = image.shape
    # 确保图像的行数和列数是2的幂次方
    assert rows == cols and (rows & (rows - 1)) == 0, "行数和列数必须是2的幂次方"
    # 计算哈达玛矩阵
    hadamard_matrix = hadamard(rows)
    # 执行二维哈达玛变换
    transformed_image = np.dot(hadamard_matrix, np.dot(image, hadamard_matrix)) / (rows * cols)
    # 将像素值重新缩放到[0, 255]范围内并取整
    # 我也不知道为什么要(transformed_image + 1.0) / 2.0 * 255.0再缩放
    transformed_image = np.clip((transformed_image + 1.0) / 2.0 * 255.0, 0, 255).astype(np.uint8)
    return transformed_image

# 哈达玛逆变换函数
def inverse_hadamard_transform(transformed_image):
    # 获取图像的行数和列数
    rows, cols = transformed_image.shape
    # 确保图像的行数和列数是2的幂次方
    assert rows == cols and (rows & (rows - 1)) == 0, "行数和列数必须是2的幂次方"
    # 计算哈达玛矩阵
    hadamard_matrix = hadamard(rows)
    # 执行逆二维哈达玛变换
    original_image = np.dot(hadamard_matrix, np.dot(transformed_image, hadamard_matrix))
    # 将像素值重新缩放到[0, 255]范围内并取整
    original_image = np.clip(original_image, 0, 255).astype(np.uint8)
    return original_image
    

# 进行二维哈达玛正变换
dht_transform = hadamard_transform(np.float32(image))

# 显示变换后的系数
magnitude_spectrum = dht_transform
plt.imshow(magnitude_spectrum, cmap='jet')
plt.title('DHT Coefficients')
    

# 进行二维哈达玛逆变换
image_restored = inverse_hadamard_transform(dht_transform)
    
```



## 加噪

> ```python
> from skimage.util import random_noise
> ```

### 高斯噪声

```python
# 添加高斯随机噪声
image_noise = random_noise(image, mode='gaussian', mean=mean, var=var)
# 将噪声图像缩放回0-255的范围，并转换为无符号8位整数
image_noise_uint8 = ((image_noise - image_noise.min()) * (255.0 / (image_noise.max() - image_noise.min()))).astype(np.uint8)
```

### 椒盐噪声

```python
# 添加椒盐随机噪声
image_noise = random_noise(image, mode='s&p', amount=amount, salt_vs_pepper=salt_vs_pepper)
# 将噪声图像缩放回0-255的范围，并转换为无符号8位整数
image_noise_uint8 = ((image_noise - image_noise.min()) * (255.0 / (image_noise.max() - image_noise.min()))).astype(np.uint8)
```

### 计算PSNR

```python
# 计算PSNR的函数
def psnr(img1, img2):
    mse = np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr_val = -20 * np.log10(np.sqrt(mse) / max_pixel)
    return psnr_val
```



## 形态学运算

### 定义kernel

```python
# 以圆形kernel为例
def create_circular_kernel(r):
    # 计算圆形结构的大小，确保它是奇数
    ksize = 2 * r + 1
    # 初始化结构元素数组
    kernel = np.zeros((ksize, ksize), dtype=np.uint8)
    # 计算中心点的坐标
    center = (r, r)
    # 填充结构元素数组，创建圆形
    for i in range(ksize):
        for j in range(ksize):
            if math.sqrt((i - center[0]) ** 2 + (j - center[1]) ** 2) <= r:
                kernel[i, j] = 1
            else:
                kernel[i, j] = 0
    return kernel
```

### 腐蚀

```python
image_erosion = cv2.erode(image, kernel, iterations=1)
```

### 膨胀

```python
image_dilation = cv2.dilate(image, kernel, iterations=1)
```



## 边缘检测

### canny算法

```python
# 边缘像素被分为三类：
# 强边缘像素：具有高于 threshold2 的梯度值
# 弱边缘像素：具有介于 threshold1 和 threshold2 之间的梯度值
# 非边缘像素：具有低于 threshold1 的梯度值
# 如果一个像素的梯度值超过 threshold2，它被视为强边缘像素，直接被接受为边缘像素
# 如果一个像素的梯度值在 threshold1 和 threshold2 之间，它被视为弱边缘像素。弱边缘像素只有在与强边缘像素相邻时才被接受为边缘像素
# 如果一个像素的梯度值低于 threshold1，它被丢弃，被视为非边缘像素

edges = cv2.Canny(image, threshold1, threshold2)
# apertureSize即sobel算子的尺寸，默认为3
edges = cv2.Canny(image, 50, 150, apertureSize=5)
```

### 使用robert算子

#### 自定义矩阵

```python
def canny_detect_robert(img):
    # Robert算子
    kernelx = np.array([[-1, 0], [0, 1]], dtype=int)
    kernely = np.array([[0, -1], [1, 0]], dtype=int)
    x = cv2.filter2D(img, cv2.CV_16S, kernelx)
    y = cv2.filter2D(img, cv2.CV_16S, kernely)
    # 转uint8
    absX = cv2.convertScaleAbs(x)
    absY = cv2.convertScaleAbs(y)
    Robert = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
    # 显示图形
    plt.imshow(Robert, cmap=plt.cm.gray), plt.title('Robert'), plt.axis('off')
    plt.show()
    return Robert
```

### 使用sobel算子

#### 内置函数

```python
# 使用 Sobel 算子计算图像梯度
grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)  # x 方向梯度
grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)  # y 方向梯度

# 可选：转换为绝对值，并将结果转换为图像格式 uint8
grad_x = cv2.convertScaleAbs(grad_x)
grad_y = cv2.convertScaleAbs(grad_y)

# 可选：合并梯度图像
gradient_image = cv2.addWeighted(grad_x, 0.5, grad_y, 0.5, 0)
```

#### 自定义矩阵

```python
def canny_detect_sobel(img):
    # Sobel算子
    kernelx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=int)
    kernely = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=int)
    x = cv2.filter2D(img, cv2.CV_16S, kernelx)
    y = cv2.filter2D(img, cv2.CV_16S, kernely)
    # 转uint8
    absX = cv2.convertScaleAbs(x)
    absY = cv2.convertScaleAbs(y)
    Sobel = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
    # 显示图形
    plt.imshow(Sobel, cmap=plt.cm.gray), plt.title('Sobel'), plt.axis('off')
    plt.show()
    return Sobel
```

### 使用laplacian算子

#### 内置函数

```python
# 使用 Laplacian 算子进行边缘检测
laplacian = cv2.Laplacian(image, cv2.CV_64F)

# 可选：转换为绝对值，并将结果转换为图像格式 uint8
laplacian = cv2.convertScaleAbs(laplacian)
```

#### 自定义矩阵

```python
def canny_detect_laplacian(img):
    # Laplacian算子
    kernelxy = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=int)
    xy = cv2.filter2D(img, cv2.CV_16S, kernelxy)
    # 转uint8
    Laplacian = cv2.convertScaleAbs(xy)
    # 显示图形
    plt.imshow(Laplacian, cmap=plt.cm.gray), plt.title('Laplacian'), plt.axis('off')
    plt.show()
    return Laplacian
```



## 霍夫变换

### 直线检测

```python
# 边缘检测（使用 Canny 边缘检测算法）
edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)

# 霍夫直线检测
lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=100)

# 绘制检测到的直线
if lines is not None:
    for line in lines:
        rho, theta = line[0]
        # 计算直线的端点坐标
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        # 直线参数
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        # 在原始灰度图像上绘制直线
        cv2.line(gray_image, (x1, y1), (x2, y2), 255, 2)  # 注意颜色参数为灰度图像中的灰度值

# 显示灰度图像和检测到的直线
cv2.imshow('Original Gray Image', gray_image)
cv2.waitKey(0)
```

### 圆检测

#### 内置函数

```python
# 参数解释：
# edge_image：这是输入的边缘检测图像，通常是通过 Canny 边缘检测算法得到的二值图像或者其他能够凸显圆形轮廓的图像。
# cv2.HOUGH_GRADIENT：表示使用霍夫圆变换的方法，这里是基于梯度的方法。
# dp：这是霍夫圆变换中的累加器分辨率与图像分辨率的倒数比。默认值为 1，表示与图像分辨率相同。较小的值会增加累加器数组的大小，从而减少检测到的圆的数量。
# minDist：这是检测到的圆心之间的最小距离。如果设置得太小，可能会导致重叠圆被检测多次；设置得太大，可能会导致某些圆被忽略。
# param1：是用于边缘检测的阈值参数 param1。它用来控制边缘检测的灵敏度。较小的值会导致更多的边缘被检测到，从而可能检测到更多的圆。较大的值会过滤掉较少的边缘。
# param2：是用于圆检测的阈值参数 param2。它表示在霍夫空间中圆心累加器的阈值。较小的值会导致更多的假阳性圆被检测到，较大的值会过滤掉较少的圆。
# minRadius：检测的圆的最小半径。
# maxRadius：检测的圆的最大半径。
# 返回值解释：
# circle 是一个包含检测到的圆的信息的 Numpy 数组。每个检测到的圆由一个三元组 (x, y, r) 表示，其中 (x, y) 是圆心的坐标，r 是圆的半径。

circle = cv2.HoughCircles(edge_image, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=0, maxRadius=0)
```

#### 自编函数

```python
def hough_circle_detection(edge_image):
    # 二值化
    _, image = cv2.threshold(edge_image, 10, 255, cv2.THRESH_BINARY)

    # 应用Sobel算子计算梯度
    # 第一个参数是图像，第二个参数是图像的深度（-1表示自动检测），第三个参数是x方向的阶数，第四个参数是y方向的阶数
    sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=11)  # ksize大一点好，梯度更精确
    sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=11)

    # 计算梯度幅度和方向
    abs_sobel_x = abs(sobel_x)  # 转换为绝对值
    abs_sobel_y = abs(sobel_y)

    sobel_mag = cv2.magnitude(abs_sobel_x, abs_sobel_y)  # 梯度幅度

    # 得到边缘点的法线方向
    # 考虑梯度幅度为0时的情况，避免除以0
    dir_dx = np.divide(sobel_x, sobel_mag, out=np.zeros_like(sobel_x), where=sobel_mag != 0)
    dir_dy = np.divide(sobel_y, sobel_mag, out=np.zeros_like(sobel_y), where=sobel_mag != 0)

    # 图像的尺寸
    height, width = image.shape

    # 创建一个三维累加器：图片长度*宽度*半径范围，半径范围为（0到"图像宽度/2"）
    radius_range = height // 2
    accumulator = np.zeros((height, width, radius_range), dtype=np.uint8)

    # 遍历image中所有值为255的点（边缘点），对每一个点，在它对应的法线方向上：
    for y in range(height):
        for x in range(width):
            if image[y, x] == 255:  # 边缘点
                for r in range(radius_range):
                    # 计算圆心坐标，理论上来说，-号也可以
                    # 写+号时，“外圈”点：向圆内搜索；“内圈”点：向圆外搜索
                    center_x = int(x + r * dir_dx[y, x])
                    center_y = int(y + r * dir_dy[y, x])
                    # 检查圆心是否在图像范围内
                    if 0 <= center_x < width and 0 <= center_y < height:
                        # 在累加器相应位置投票
                        accumulator[center_y, center_x, r] += 1

    # 找出累加器中最大值所在的位置，得到圆心所在坐标和圆的半径
    # 使用 np.argmax 来找到最大值的索引
    max_index = np.argmax(accumulator.ravel())  # 将累加器展平成一维数组并找到最大值的索引
    max_votes = accumulator.ravel()[max_index]  # 获取最大值
    # 使用 np.unravel_index 来将一维索引转换回三维索引
    center_y, center_x, radius = np.unravel_index(max_index, accumulator.shape)
    circle = [center_x, center_y, radius]
    print(circle)
    return circle
```





