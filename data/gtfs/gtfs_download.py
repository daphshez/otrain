import urllib.request, sys, os, time

folders = ['2014_07_07_17_58_16', '2014_07_08_22_00_01', '2014_07_16_22_00_01', '2014_07_24_22_00_02',
           '2014_07_29_22_00_01', '2014_07_31_23_00_01', '2014_08_07_23_00_02', '2014_08_11_17_22_48',
           '2014_08_11_17_48_36', '2014_08_11_18_12_28', '2014_08_18_06_00_01', '2014_08_19_06_00_01',
           '2014_08_20_06_00_01', '2014_08_21_06_00_01', '2014_08_22_06_00_02', '2014_08_23_06_00_02',
           '2014_08_24_06_00_02', '2014_08_25_06_00_02', '2014_08_26_06_00_01', '2014_08_27_06_00_02',
           '2014_08_28_06_00_01', '2014_08_29_06_00_02', '2014_08_30_06_00_02', '2014_08_31_06_00_02',
           '2014_09_01_06_00_02', '2014_09_01_18_19_01', '2014_09_04_06_00_02', '2014_09_05_06_00_02',
           '2014_09_06_06_00_01', '2014_09_07_06_00_02', '2014_09_08_06_00_02', '2014_09_09_06_00_02',
           '2014_09_10_06_00_02', '2014_09_11_06_00_02', '2014_09_12_06_00_01', '2014_09_13_06_00_01',
           '2014_09_14_06_00_02', '2014_09_15_06_00_02', '2014_09_16_06_00_02', '2014_09_17_06_00_02',
           '2014_09_18_06_00_02', '2014_09_19_06_00_02', '2014_09_20_06_00_02', '2014_09_21_06_00_01',
           '2014_10_07_06_00_02', '2014_10_08_06_00_02', '2014_10_22_06_00_02', '2014_10_23_06_00_01',
           '2014_11_04_07_00_01', '2014_11_19_07_00_02', '2014_11_20_07_00_02', '2014_11_21_07_00_02',
           '2014_11_25_07_00_02', '2014_12_09_07_00_01', '2015_01_19_07_00_01', '2015_01_23_07_00_02',
           '2015_02_05_07_00_02', '2015_02_12_07_00_02', '2015_02_24_07_00_02', '2015_03_11_06_00_02',
           '2015_03_19_06_00_01', '2015_03_20_06_00_02', '2015_03_27_06_00_02', '2015_04_01_06_00_02',
           '2015_04_02_06_00_02', '2015_04_14_06_00_02', '2015_04_20_06_00_02', '2015_04_29_06_00_02',
           '2015_05_01_06_00_02', '2015_05_08_06_00_01', '2015_05_12_06_00_02', '2015_05_13_06_00_02',
           '2015_05_14_06_00_01', '2015_05_15_06_00_02', '2015_05_16_06_00_01', '2015_05_17_06_00_01',
           '2015_05_18_06_00_01', '2015_05_19_06_00_02', '2015_05_20_06_00_02', '2015_05_21_06_00_01',
           '2015_05_22_06_00_02', '2015_05_23_06_00_02', '2015_05_24_06_00_02', '2015_05_25_06_00_02',
           '2015_05_26_06_00_02', '2015_05_27_06_00_02', '2015_05_28_06_00_02', '2015_05_29_06_00_02',
           '2015_05_30_06_00_02', '2015_05_31_06_00_02', '2015_06_01_06_00_02', '2015_06_02_06_00_02',
           '2015_06_03_06_00_01', '2015_06_04_06_00_01', '2015_06_05_06_00_02', '2015_06_08_06_00_01',
           '2015_06_09_06_00_02', '2015_06_10_06_00_01', '2015_06_11_06_00_02', '2015_06_12_06_00_02',
           '2015_06_13_06_00_02', '2015_06_14_06_00_02', '2015_06_15_06_00_02', '2015_06_16_06_00_02',
           '2015_06_17_06_00_02', '2015_06_18_06_00_02', '2015_06_19_06_00_02', '2015_06_20_06_00_02',
           '2015_06_21_06_00_02', '2015_06_22_06_00_02', '2015_06_23_06_00_02', '2015_06_24_06_00_02',
           '2015_06_25_06_00_02', '2015_06_26_06_00_02', '2015_06_27_06_00_02', '2015_06_28_06_00_02',
           '2015_06_29_06_00_02', '2015_06_30_06_00_02', '2015_07_01_06_00_01', '2015_07_02_06_00_01',
           '2015_07_03_06_00_02', '2015_07_04_06_00_01', '2015_07_05_06_00_02', '2015_07_06_06_00_02',
           '2015_07_07_06_00_02', '2015_07_08_06_00_02', '2015_07_09_06_00_02', '2015_07_10_06_00_02',
           '2015_07_11_06_00_02', '2015_07_12_06_00_03', '2015_07_13_06_00_02', '2015_07_14_06_00_02',
           '2015_07_15_06_00_02']

td = r"http://192.241.154.128/gtfs-data/%s/irw_gtfs.zip"


# http://stackoverflow.com/questions/13881092/download-progressbar-for-python-3
def reporthook(blocknum, blocksize, totalsize):
    read_so_far = blocknum * blocksize
    if totalsize > 0:
        percent = read_so_far * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), read_so_far, totalsize)
        sys.stderr.write(s)
        if read_so_far >= totalsize:  # near the end
            sys.stderr.write("\n")
    else:  # total size is unknown
        sys.stderr.write("read %d\n" % (read_so_far,))


for folder in reversed(folders):
    print(folder)
    fn = folder + ".zip"
    if not os.path.exists(fn):
        urllib.request.urlretrieve(td % folder, fn, reporthook)
        time.sleep(1)