import sys
import glob
import math
import os
from xml.dom import minidom
import replayLogger
import configReader

config = configReader.read_config(".\\folderPath.ini")

if config is None:
	raise Exception("Cannot parse config file")

received_path = config["Path"]

appPath = ".\\"
logZ = replayLogger.Logger(appPath, "pcdMeta")

master_list = []
# received_path = "C:\Users\mikeyt\Desktop\ProjectMeta"
DYNAMIC_INIS_BACKUP_PATH = os.path.join(received_path, 'DynamicINIsBackup')
XGEN_MAIN_FILTERED_PCD_PATH = os.path.join(received_path, 'XGEN_MAIN_FILTERED_PCD')
XGEN_MAIN_PCD_PATH = os.path.join(received_path, 'XGEN_MAIN_PCD')
XGEN_OUTSIDE_FILTERED_PCD_PATH = os.path.join(received_path, 'XGEN_OUTSIDE_FILTERED_PCD')
XGEN_OUTSIDE_PCD_PATH = os.path.join(received_path, 'XGEN_OUTSIDE_PCD')
XGEN_SEED_ZONE_A_PATH = os.path.join(received_path, 'XGEN_SEED_ZONE_A')
XGEN_SEED_ZONE_B_PATH = os.path.join(received_path, 'XGEN_SEED_ZONE_B')
XGEN_SKY_CAM_FILTERED_PCD_PATH = os.path.join(received_path, 'XGEN_SKY_CAM_FILTERED_PCD')
XGEN_SKY_CAM_PCD_PATH = os.path.join(received_path, 'XGEN_SKY_CAM_PCD')

list_of_main_filtered = []
list_of_outside_filtered = []
list_of_skycam_filtered = []

list_of_INIs_main = []
list_of_INIs_middle = []
list_of_INIs_outside = []
list_of_INIs_lowerbody = []
list_of_INIs_skycam = []
list_of_INIs_goalkeeper = []

for file1 in os.listdir(XGEN_MAIN_FILTERED_PCD_PATH):
	if file1.endswith(".pcd"):
		list_of_main_filtered.append(file1)
for file1 in os.listdir(XGEN_OUTSIDE_FILTERED_PCD_PATH):
	if file1.endswith(".pcd"):
		list_of_outside_filtered.append(file1)
for file1 in os.listdir(XGEN_SKY_CAM_FILTERED_PCD_PATH):
	if file1.endswith(".pcd"):
		list_of_skycam_filtered.append(file1)

for file1 in os.listdir(DYNAMIC_INIS_BACKUP_PATH):
	if file1.endswith(".ini"):
		if file1.startswith("main0"):
			list_of_INIs_main.append(file1)
		elif file1.startswith("MiddleCloud"):
			list_of_INIs_middle.append(file1)
		elif file1.startswith("outside"):
			list_of_INIs_outside.append(file1)
		elif file1.startswith("lowerbody0"):
			list_of_INIs_lowerbody.append(file1)
		elif file1.startswith("skycam0"):
			list_of_INIs_skycam.append(file1)
		elif file1.startswith("GoalKeeper0"):
			list_of_INIs_goalkeeper.append(file1)

# ALL OF THESE PATHS SHOULD BE EVENTUALLY COMPATIBLE WITH THE SYSTEM ##########################
clip_parameters_xml = minidom.parse(os.path.join(received_path, 'ParametersBackup\ComputerParameters.xml'))
site_parameters = minidom.parse(os.path.join(received_path, 'ParametersBackup\SiteParameters.xml'))

site_parameter_list = site_parameters.getElementsByTagName('Parameter')
params_list = clip_parameters_xml.getElementsByTagName('Parameter')

for param in site_parameter_list:
	if param.attributes['ParameterName'].value == "VenueInformation":
		venue = param.attributes['ParameterValue'].value


# content must begin with '#'
def write_to_file(file_path, content):
	logZ.info("Creating the modified pcd file")
	tmp_file = file_path[:-4] + "N.pcd"
	new_path = os.path.join(os.path.split(file_path)[0], "backUpPCDz")
	new_file = os.path.join(new_path, os.path.split(file_path)[1])
	if not os.path.exists(new_path):
		os.makedirs(new_path)
	elif os.path.exists(new_file):
		logZ.warn(file_path + "  already contains metadata, this is the backup:  " + new_file)
		return
	with open(file_path, "rb") as old, open(tmp_file, "wb") as new:
		new.write(content + "\n")
		new.write(old.read())
	try:
		os.rename(file_path, new_file)
		os.rename(tmp_file, file_path)
	except OSError:
		logZ.warn(new_file + " already exists")

	logZ.info(file_path + " created, with metadata!")
	logZ.info(new_file + " original file backed up")


def read_from_ini(ini_file):
	path_to_ini = os.path.join(DYNAMIC_INIS_BACKUP_PATH, ini_file)
	f = open(path_to_ini, 'r')
	lst = []
	for line in f:
		if line.startswith("targetImages"):
			lst.append("#" + line)
		elif line.startswith("boxCorners"):
			lst.append("#" + line)
		elif line.startswith("render_cameras"):
			lst.append("#" + line)
		elif line.startswith("bounding_box"):
			lst.append("#" + line)
	f.close()
	return lst


def number_of_pcd(strz):
	count = 3
	num = 0
	while strz[0] != '.' and strz != "":
		if strz[0] < '0' or strz[0] > '9':
			strz = strz[1:]
		elif strz[0] == '0':
			count -= 1
			strz = strz[1:]
		else:
			break
	while strz[0] != '.' and strz != "":
		num = num + int(math.pow(10, count) * (ord(strz[0]) - 48))
		strz = strz[1:]
		count -= 1
	return num


def number_of_fgc(strz):
	count = 1
	num = 0
	while strz != "":
		if strz[0] < '0' or strz[0] > '9':
			strz = strz[1:]
		elif strz[0] == '0':
			count -= 1
			strz = strz[1:]
		else:
			break
	while strz != "":
		num = num + int(math.pow(10, count) * (ord(strz[0]) - 48))
		strz = strz[1:]
		count -= 1
	return num


def is_computer_in_group(computer, group):
	i = 0
	for compi in group:
		if compi == computer:
			return i
		i += 1
	return -1


def is_pcd_middle(strz):
	return "middle" == strz[0:6]


def get_computers(computer_group):
	list_string = ""
	for parami in params_list:
		if parami.attributes['ParameterName'].value == computer_group:
			list_string = parami.attributes['ParameterValue'].value
	computerz = []
	tmp = ""
	while list_string != "":
		if list_string[0] != ',':
			tmp += list_string[0]
			list_string = list_string[1:]
		elif list_string != "":
			computerz.append(tmp)
			tmp = ""
			list_string = list_string[1:]

	computerz.append(tmp)

	return computerz


renderZ = get_computers("RenderComputers")

mainZ = get_computers("XgenMainComputers")

lowerbodyZ = get_computers("XgenLowerBodyComputers")

middleZ = get_computers("MiddleComputers")

outsideZ = get_computers("XgenOutsideComputers")

skycamZ = get_computers("XgenSkyCamComputers")

goalZ = get_computers("XgenGoalKeeperComputers")

if lowerbodyZ.__len__() == 0:
	logZ.warn("There aren't any XgenLowerBodyComputers")
if middleZ.__len__() == 0:
	logZ.warn("There aren't any MiddleComputers")
if skycamZ.__len__() == 0:
	logZ.warn("There aren't any XgenSkyCamComputers")
if goalZ.__len__() == 0:
	logZ.warn("There aren't any XgenGoalKeeperComputers")

if list_of_main_filtered.__len__() == 0:
	logZ.warn("There aren't any main PCDs")
if list_of_outside_filtered.__len__() == 0:
	logZ.warn("There aren't any outside PCDs")
if list_of_skycam_filtered.__len__() == 0:
	logZ.warn("There aren't any skyCam PCDs")

def make_master_list():
	i = 1
	master_list1 = []
	for main in mainZ:
		master_list1.append((str(main), i))
		i += 1
	i = 1
	for lb in lowerbodyZ:
		master_list1.append((str(lb), i))
		i += 1
	i = 1
	for mid1 in middleZ:
		master_list1.append((str(mid1), i))
		i += 1
	i = 1
	for out in outsideZ:
		master_list1.append((str(out), i))
		i += 1
	for sky in skycamZ:
		master_list1.append((str(sky), i))
		i += 1
	return master_list1


master_list = make_master_list()

mid = 0
mainn = 0
lowern = 0
gkn = 0
outn = 0
skyn = 0
for pcd in list_of_main_filtered:
	if is_pcd_middle(pcd):
		t = read_from_ini(list_of_INIs_middle[mid])
		write_to_file(os.path.join(XGEN_MAIN_FILTERED_PCD_PATH, pcd), "#Arena: " + venue + "\n" + "#Path to frame: "
					  + received_path + "\n" + "#Created by computer: " + str(middleZ[mid]) +
					  "\n" + "#Created by INI file: " + str(list_of_INIs_middle[mid]) + "\n"
					  + t[0] + t[1])
		if mid < middleZ.__len__() - 1:
			mid += 1
	elif mainn < mainZ.__len__() and number_of_pcd(pcd) == number_of_fgc(mainZ[mainn]):
		t = read_from_ini(list_of_INIs_main[mainn])
		write_to_file(os.path.join(XGEN_MAIN_FILTERED_PCD_PATH, pcd), "#Arena: " + venue + "\n" + "#Path to frame: "
					  + received_path + "\n" + "#Created by computer: " + str(mainZ[mainn]) +
					  "\n" + "#Created by INI file: " + str(list_of_INIs_main[mainn]) + "\n"
					  + t[0] + t[1])
		mainn += 1
	elif lowern < lowerbodyZ.__len__() and number_of_pcd(pcd) == number_of_fgc(lowerbodyZ[lowern]):
		t = read_from_ini(list_of_INIs_lowerbody[lowern])
		write_to_file(os.path.join(XGEN_MAIN_FILTERED_PCD_PATH, pcd), "#Arena: " + venue + "\n" + "#Path to frame: "
					  + received_path + "\n" + "#Created by computer: " + str(lowerbodyZ[lowern]) +
					  "\n" + "#Created by INI file: " + str(list_of_INIs_lowerbody[lowern]) + "\n"
					  + t[0] + t[1])
		lowern += 1
	else:
		for gkn in range(0, goalZ.__len__()):
			if number_of_pcd(pcd) == number_of_fgc(goalZ[gkn]):
				t = read_from_ini(list_of_INIs_goalkeeper[gkn])
				write_to_file(os.path.join(XGEN_MAIN_FILTERED_PCD_PATH, pcd),
							  "#Arena: " + venue + "\n" + "#Path to frame: "
							  + received_path + "\n" + "#Created by computer: " + str(goalZ[gkn]) +
							  "\n" + "#Created by INI file: " + str(list_of_INIs_goalkeeper[gkn]) + "\n"
							  + t[0] + t[1])

for pcd in list_of_outside_filtered:
	if outn < outsideZ.__len__() and number_of_pcd(pcd) == number_of_fgc(outsideZ[outn]):
		t = read_from_ini(list_of_INIs_outside[outn])
		write_to_file(os.path.join(XGEN_OUTSIDE_FILTERED_PCD_PATH, pcd), "#Arena: " + venue + "\n" + "#Path to frame: "
					  + received_path + "\n" + "#Created by computer: " + str(outsideZ[outn]) +
					  "\n" + "#Created by INI file: " + str(list_of_INIs_outside[outn]) + "\n"
					  + t[0] + t[1])
		outn += 1

for pcd in list_of_skycam_filtered:
	for skyn in range(0, skycamZ.__len__()):
		if skyn < skycamZ.__len__() and number_of_pcd(pcd) == number_of_fgc(skycamZ[skyn]):
			t = read_from_ini(list_of_INIs_skycam[skyn])
			write_to_file(os.path.join(XGEN_SKY_CAM_FILTERED_PCD_PATH, pcd),
						  "#Arena: " + venue + "\n" + "#Path to frame: "
						  + received_path + "\n" + "#Created by computer: " + str(skycamZ[skyn]) +
						  "\n" + "#Created by INI file: " + str(list_of_INIs_skycam[skyn]) + "\n"
						  + t[0] + t[1])
