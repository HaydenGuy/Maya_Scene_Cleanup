import maya.cmds as cmds

# Gets a list of all the camera names in the scene
def list_all_cameras():
    all_camera_details = cmds.ls(type='camera', long=True)
    camera_names = []

    for cam in all_camera_details:
        camera = cam.split('|')[1]
        camera_names.append(camera)

    return camera_names

# Gets a list of everything in the scene
def list_everything():
    all_objects = cmds.ls(dag=True, long=True)
    group_names = []

    for name in all_objects:
        group = name.split('|')[1]
        group_names.append(group)

    return group_names

# Filters the everything list so that it doesn't contain cameras and only shows the first appearance of each group name
def filtered_list():
    all_cameras = list_all_cameras()
    group_names = list_everything()

    filtered_groups = list(dict.fromkeys([group for group in group_names if group not in all_cameras]))

    return filtered_groups

groups = filtered_list()

print(groups)
# print(cmds.ls(dag=True, long=True))