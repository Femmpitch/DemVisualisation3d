 # -*- coding: utf-8 -*-
import gdal, osr
import numpy as np
import visvis
# Важно: для работы visvis нужен установленный PyQt4-5 или PySide

def importDemAsArray(path, xsize=None, ysize=None, xoff=0, yoff=0):
    """
    Программа открывает файл DEM формата GeoTIFF и считывает с него геоинформацию и матрицу высот.
    Входной файл должен быть записан в системе координат WGS-84 (самы распространенный формат,
    позже реализуем для любого).
    Входной dataset преобразуется в систему координат EPSG:3395 - Pseudo Mercator (прямоугольная система с учетом
    кривизны Земли в метрах)
    xoff, yoff - начальные индексы среза массива, xsize, ysize - размеры массива
    Осторожнее с большими файлами - может зависнуть. Для подобных файлов используйте дополнительные входные параметры
    (пример 2).
    """

    dataset = gdal.Open(path)

    # Задаем старую и новую системы координат
    inputEPSG = 4326  # WGS-84
    outputEPSG = 3395  # World Mercator (units meters)
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(inputEPSG)
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outputEPSG)
    newProjection = outSpatialRef.ExportToWkt()

    # Задаем новый объект на базе dataset с новой системой координат
    warped = gdal.AutoCreateWarpedVRT(dataset, dataset.GetProjection(), newProjection)
    gt = warped.GetGeoTransform()

    # Чтение высот как матрицы
    Z = dataset.ReadAsArray(xoff, yoff, xsize, ysize)
    #  определяем массивы координат x и y
    x = np.linspace(0, Z.shape[1]-1, Z.shape[1])
    y = np.linspace(0, Z.shape[0]-1, Z.shape[0])
    # Делаем meshgrid: X,Y
    X, Y = np.meshgrid(x, y )
    # Приведение Z к нулю в центре
    Z = Z - Z[Z.shape[0] / 2, Z.shape[1] / 2]
    # Преобразование X и Y с помощью geotransform
    X, Y = gt[0] + gt[1]*X + gt[2] * Y, gt[3] + gt[4] * X + gt[5]*Y
    # Центрирование координат X и Y
    # X, Y = X - X[X.shape[0] / 2, X.shape[1] / 2], Y - Y[Y.shape[0] / 2, Y.shape[1] / 2]
    return X, Y, Z

def visualizeDEM(X, Y, Z, scale=1.0):
    """Создание 3D-модели из вычисленных ранее массивов"""
    m = visvis.surf(X, Y, scale*Z)
    m.colormap = visvis.CM_JET
    app = visvis.use()
    app.Run()

def visualizeDEM_direct(path, scale=1.0):
    """Создание 3D-модели без сохранения массивов в памяти"""
    X, Y, Z = importDemAsArray(path)
    visualizeDEM(X, Y, Z, scale)


if __name__ == "__main__":
    #1. Пример 1
    path = 'n55_e037_3arc_v1.tif'
    X, Y, Z = importDemAsArray(path)
    visualizeDEM(X, Y, Z, 20)

    #2. Пример 2
    # path = 'srtm_germany_dsm.tif'
    # X, Y, Z = importDemAsArray(path, xoff=8000, yoff=7000, xsize=2000, ysize=2000)
    # visualizeDEM(X, Y, Z)