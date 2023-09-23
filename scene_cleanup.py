import maya.cmds as cmds

# Gets a list of all the camera names in the scene
def list_all_cameras():
    # List all camera nodes in the scene and store their long names (|camera|cameraShape1)
    all_camera_details = cmds.ls(type='camera', long=True)
    camera_names = []

    # Extract just the camera name and add it to the camera_names list
    for cam in all_camera_details:
        camera = cam.split('|')[1]
        camera_names.append(camera)

    return camera_names

# Gets a list of everything in the scene
def list_everything():
    # List everything in the scene in long name format (|group1|pSphere1)
    all_objects = cmds.ls(dag=True, long=True)
    group_names = []

    # Extract just the group names and add it to the group_names list
    for name in all_objects:
        group = name.split('|')[1]
        group_names.append(group)

    return group_names

# Filters the everything list so that it doesn't contain cameras and only shows the first appearance of each group name
def filtered_list():
    all_cameras = list_all_cameras()
    group_names = list_everything()

    # Filters the group names by excluding the cameras with list comprehension
    # To get unique names, first convert the list into a dictionary to remove duplicate items and convert it back into a list
    filtered_groups = list(dict.fromkeys([group for group in group_names if group not in all_cameras]))

    return filtered_groups

# Deletes empty groups from the scene
def delete_empty_groups():
    groups = filtered_list()

    # Generates a list of groups in the scene that have no children (are empty)
    empty_groups = [group for group in groups if not cmds.listRelatives(group, children=True)]

    # Delete the empty groups
    cmds.delete(empty_groups)