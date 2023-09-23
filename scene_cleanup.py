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
def list_objects():
    # List everything in the scene in long name format (|group1|pSphere1)
    all_objects = cmds.ls(dag=True, long=True)
    group_names = []

    # Extract just the group names and add it to the group_names list
    for name in all_objects:
        group = name.split('|')[1]
        group_names.append(group)

    return group_names

# Filters the object list so that it doesn't contain cameras and only shows the first appearance of each group name
def filtered_list():
    all_cameras = list_all_cameras()
    group_names = list_objects()

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

# Gets a list of all materials in the scene, filters and returns them if they aren't the default materials
def list_all_materials():
    default_materials = ['lambert1', 'particleCloud1', 'shaderGlow1', 'standardSurface1']
    all_materials = cmds.ls(materials=True)

    filtered_materials = [mat for mat in all_materials if mat not in default_materials]

    return  filtered_materials

# Check if a shading engine has connected objects
def has_connect_objects(shading_engine):
    return cmds.sets(shading_engine, q=True)

# Creates a set of used materials in the scene
def list_used_materials():
    used_materials = set()
    
    # Iterate through all shading engines in the scene
    for shading_engine in cmds.ls(type='shadingEngine'):
        # Check if the shading engine is connected to any objects
        if has_connect_objects(shading_engine):
            # List all materials connect to the shading engine
            connected_objects =  cmds.ls(cmds.listConnections(shading_engine), materials=True)
            used_materials.update(connected_objects) # Update the set of used materials

    return used_materials

# If the material appears in the material list and not in the used material list it is deleted
def delete_unused_materials():
    material_list = list_all_materials()
    used_materials = list_used_materials()
    
    for material in material_list:
        if material not in used_materials:
            cmds.delete(material)