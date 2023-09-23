import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

# Camera frustum checking from: https://gist.github.com/Kif11/247f6b05e8d3a6c3ffb193b8c6f4dec7
class Plane(object):
    def __init__(self, normalisedVector):
        # OpenMaya.MVector.__init__()
        self.vector= normalisedVector
        self.distance= 0.0

    def relativeToPlane(self, point):
        # Converting the point as a vector from the origin to its position
        pointVec= OpenMaya.MVector( point.x, point.y, point.z )
        val= (self.vector * pointVec) + self.distance

        if (val > 0.0):
            return 1  # In front
        elif (val < 0.0):
            return -1  # Behind

        return 0  # On the plane

class Frustum(object):
    def __init__(self, cameraName):
        # Initialising selected transforms into its associated dagPaths
        selectionList= OpenMaya.MSelectionList()
        objDagPath= OpenMaya.MDagPath()
        selectionList.add( cameraName )
        selectionList.getDagPath(0, objDagPath)
        self.camera= OpenMaya.MFnCamera(objDagPath)

        self.nearClip = self.camera.nearClippingPlane()
        self.farClip =  self.camera.farClippingPlane()
        self.aspectRatio= self.camera.aspectRatio()

        left_util= OpenMaya.MScriptUtil()
        left_util.createFromDouble( 0.0 )
        ptr0= left_util.asDoublePtr()

        right_util= OpenMaya.MScriptUtil()
        right_util.createFromDouble( 0.0 )
        ptr1= right_util.asDoublePtr()

        bot_util= OpenMaya.MScriptUtil()
        bot_util.createFromDouble( 0.0 )
        ptr2= bot_util.asDoublePtr()

        top_util= OpenMaya.MScriptUtil()
        top_util.createFromDouble( 0.0 )
        ptr3= top_util.asDoublePtr()

        stat= self.camera.getViewingFrustum(self.aspectRatio, ptr0, ptr1, ptr2, ptr3, False, True)

        planes= []

        left= left_util.getDoubleArrayItem(ptr0, 0)
        right= right_util.getDoubleArrayItem(ptr1, 0)
        bottom= bot_util.getDoubleArrayItem(ptr2, 0)
        top = top_util.getDoubleArrayItem(ptr3, 0)

        ## planeA = right plane
        a= OpenMaya.MVector(right, top, -self.nearClip)
        b= OpenMaya.MVector(right, bottom, -self.nearClip)
        c= (a ^ b).normal() ## normal of plane = cross product of vectors a and b
        planeA = Plane(c)
        planes.append(planeA)

        ## planeB = left plane
        a = OpenMaya.MVector(left, bottom, -self.nearClip)
        b = OpenMaya.MVector(left, top, -self.nearClip)
        c= (a ^ b).normal()
        planeB= Plane( c )
        planes.append( planeB )

        ##planeC = bottom plane
        a = OpenMaya.MVector(right, bottom, -self.nearClip)
        b = OpenMaya.MVector(left, bottom, -self.nearClip)
        c= (a ^ b).normal()
        planeC= Plane( c )
        planes.append( planeC )

        ##planeD = top plane
        a = OpenMaya.MVector(left, top, -self.nearClip)
        b = OpenMaya.MVector(right, top, -self.nearClip)
        c= (a ^ b).normal()
        planeD= Plane( c )
        planes.append( planeD )

        # planeE = far plane
        c = OpenMaya.MVector(0, 0, 1)
        planeE= Plane( c )
        planeE.distance= self.farClip
        planes.append( planeE )

        # planeF = near plane
        c = OpenMaya.MVector(0, 0, -1)
        planeF= Plane( c )
        planeF.distance= self.nearClip
        planes.append( planeF )

        self.planes = planes
        self.numPlanes = 6

    def relativeToFrustum(self, pointsArray):
        numInside= 0
        numPoints= len( pointsArray )

        for j in range( 0, 6 ):
          numBehindThisPlane= 0

          for i in range( 0, numPoints ):
            if (self.planes[j].relativeToPlane(pointsArray[i]) == -1):  # Behind
                numBehindThisPlane += 1
            if numBehindThisPlane == numPoints:
                ##all points were behind the same plane
                return False
            elif (numBehindThisPlane==0):
                numInside += 1

        if (numInside == self.numPlanes):
            return True  # Inside
        return True  # Intersect

# Returns true if an object is inside the cameras frustum
def in_frustum(cameraName, objectName):
    """
    returns: True if within the frustum of False if not
    """
    selectionList = OpenMaya.MSelectionList()
    camDagPath = OpenMaya.MDagPath()
    selectionList.add( cameraName )
    selectionList.getDagPath(0, camDagPath)

    cameraDagPath = OpenMaya.MFnCamera( camDagPath )

    camInvWorldMtx = camDagPath.inclusiveMatrixInverse()

    fnCam = Frustum(cameraName)
    points = []

    # For node inobjectList
    selectionList = OpenMaya.MSelectionList()
    objDagPath = OpenMaya.MDagPath()
    selectionList.add(objectName)
    selectionList.getDagPath( 0, objDagPath )

    fnDag = OpenMaya.MFnDagNode(objDagPath)
    obj = objDagPath.node()

    dWorldMtx = objDagPath.exclusiveMatrix()
    bbox = fnDag.boundingBox()

    minx = bbox.min().x
    miny = bbox.min().y
    minz = bbox.min().z
    maxx = bbox.max().x
    maxy = bbox.max().y
    maxz = bbox.max().z

    # Getting points relative to the cameras transmformation matrix
    points.append( bbox.min() * dWorldMtx * camInvWorldMtx )
    points.append( OpenMaya.MPoint(maxx, miny, minz) * dWorldMtx * camInvWorldMtx )
    points.append( OpenMaya.MPoint(maxx, miny, maxz) * dWorldMtx * camInvWorldMtx )
    points.append( OpenMaya.MPoint(minx, miny, maxz) * dWorldMtx * camInvWorldMtx )
    points.append( OpenMaya.MPoint(minx, maxy, minz) * dWorldMtx * camInvWorldMtx )
    points.append( OpenMaya.MPoint(maxx, maxy, minz) * dWorldMtx * camInvWorldMtx )
    points.append( bbox.max() * dWorldMtx * camInvWorldMtx )
    points.append( OpenMaya.MPoint(minx, maxy, maxz) * dWorldMtx * camInvWorldMtx )

    return fnCam.relativeToFrustum(points)

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

# Get a list of all objects in the scene that are inside a cameras view (except the defaults)
def select_objects_inside_camera_view():
    default_cameras = ['front', 'persp', 'top', 'side']
    cameras = list_all_cameras()
    user_cameras = [cam for cam in cameras if cam not in default_cameras]
    objects = filtered_list()

    inside_camera_objs = []

    for cam in user_cameras:
        for obj in objects:
            if in_frustum(cam, obj):
                    inside_camera_objs.append(obj)
        
    return inside_camera_objs

# Delete objects in the scene that are outside of any camera views
def delete_objects_not_in_any_camera_view():
    objects = filtered_list()
    camera_view_objects = select_objects_inside_camera_view()

    outside_of_camera_objs = [obj for obj in objects if obj not in camera_view_objects]

    for obj in outside_of_camera_objs:
        cmds.delete(obj)

# Runs the delete functions
def scene_cleanup():
    delete_empty_groups()
    delete_objects_not_in_any_camera_view()
    delete_unused_materials()

scene_cleanup()