
# 小数点的经纬度转成度分秒
def decimal_to_dms(decimal, format=False):
    # return decimal
    d = int(decimal)
    m = int((decimal - d) * 60)
    s = int(((decimal - d) * 60 - m) * 60)
    if(format):        
        return f"{d}°{m}′{s}″"
    else:
        return d, m, s