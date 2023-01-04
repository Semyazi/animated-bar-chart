from colorthief import ColorThief

_id_to_col = {"4e3w46z5":{"dark_col":"#EE4444","light_col":"#EE2222"},"9j3po614":{"dark_col":"#EF8241","light_col":"#EF8239"},"gy3l7n4l":{"dark_col":"#F0C03E","light_col":"#DAA520"},"w461onv1":{"dark_col":"#8AC951","light_col":"#7AB941"},"rq69m391":{"dark_col":"#09B876","light_col":"#009856"},"gw3r7nq7":{"dark_col":"#44BBEE","light_col":"#249BCE"},"1x3216j7":{"dark_col":"#6666EE","light_col":"#4646CE"},"pw37o6d7":{"dark_col":"#C279E5","light_col":"#A259C5"},"ryndx3gd":{"dark_col":"#F772C5","light_col":"#E762B5"},"kr3q9nwx":{"dark_col":"#FFFFFF","light_col":"#000000"},"qr3jl64g":{"dark_col":"#FF3091","light_col":"#EF2081"},"1y6emnpv":{"dark_col":"#A010A0","light_col":"#900090"},"296vz3ve":{"dark_col":"#B8B8B8","light_col":"#808080"},"ew6x2n47":{"dark_col":"#E77471","light_col":"#E77471"},"e7nmx3ym":{"dark_col":"#FFB3F3","light_col":"#FFB3F3"}}

def id_to_col(src_id, col_type="dark_col"):
	return hex_to_rgb(_id_to_col[src_id][col_type])

def hex_to_rgb(hex):
	hex = hex[1:]
	channels = [hex[:2], hex[2:4], hex[4:]]

	return [int(x, 16) for x in channels]

def get_image_col(filepath):
	color_thief = ColorThief(filepath)
	return color_thief.get_color(quality=1)