# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#addon info read by Blender
bl_info = {
    "name": "Lymphoedema 3D Scan Analysis Toolset",
    "author": "Ivan Prga, Annette Nguyen, Jaspreet Kaur., Abdullah Albeladi, Michael Stagg, Maxwell Heaysman, Schonn-Pierre Hirst",
    "version": (1, 0, 0),
    "blender": (2, 7, 4),
    "description": "A toolset for importing, aligning and analysing 3D scans of lymphoedema patients.",
    "category": "Mesh"
    }

#import blender python libraries
import bpy
#import python random for colour generation
import random
import math
import bmesh
from mathutils import Matrix, Vector
#use the following format to import other .py files from the local folder to make use of the contained classes/definitions
#from . import (
#        import_PLY_3DScan,
#        register_landmark,
#	 align_scans,
#	 extract_volume,
#	 generate_heatmap
#        )



#setup panel class
class LSAT_SetupPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Import'
    bl_context = 'objectmode'
    bl_category = 'Scan'
    def draw(self, context):
        self.layout.operator('lsat.importsetup', text ='Import PLY')
        
#Point placement panel class
class LSAT_PointPlacementPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Point Placement'
    bl_context = 'objectmode'
    bl_category = 'Scan'
    
    def draw(self, context):
        self.layout.operator('lsat.nose_place_landmark', text ='Place Nose Landmark')
        self.layout.operator('lsat.l_ear_place_landmark', text ='Place Left Ear Landmark')
        self.layout.operator('lsat.r_ear_place_landmark', text ='Place Right Ear Landmark')
        self.layout.operator('lsat.auto_place_landmark', text ='Autodetect Landmark Placement')

#Scan Alignment panel class
class LSAT_ScanAlignmentPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Scan Alignment'
    bl_context = 'objectmode'
    bl_category = 'Scan'
    def draw(self, context):
        self.layout.operator('lsat.alignscans', text ='Auto Align')
        
#Volume panel class
class LSAT_VolumePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Volume'
    bl_context = 'objectmode'
    bl_category = 'Scan'
    def draw(self, context):
        self.layout.operator('lsat.vol_select_area', text ='Selection')
        self.layout.operator('lsat.vol_extract_area', text ='Extraction')
        self.layout.operator('lsat.vol_measure_diff', text ='Measure Total Difference')
        
#Map panel class
class LSAT_MapPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Map'
    bl_context = 'objectmode'
    bl_category = 'Scan'
    def draw(self, context):
        self.layout.operator('lsat.importsetup', text ='Radial Difference Map')
        self.layout.operator('lsat.gen_heatmap', text ='Generate HeatMap')

class LSATVolSelectionOperator(bpy.types.Operator):
    bl_idname = "lsat.vol_select_area"
    bl_label = "Area Selection"

    def execute(self, context):
        print("Select Area")
        return {'FINISHED'}
    
class LSATVolExtractionOperator(bpy.types.Operator):
    bl_idname = "lsat.vol_extract_area"
    bl_label = "Volume Extraction"

    def execute(self, context):
        print("Volume Extraction")
        return {'FINISHED'}
    
class LSATVolMeasureDiffOperator(bpy.types.Operator):
    bl_idname = "lsat.vol_measure_diff"
    bl_label = "Measure Total Difference"

    def execute(self, context):
        print("Measure Total Difference")
        
        objects = bpy.context.scene.objects
        origin_mesh = objects['LSAT_ScanMesh0']
        plane_x = (objects['LSAT_ScanMesh0_LandmarkLeftEar'].location[0] + objects['LSAT_ScanMesh0_LandmarkRightEar'].location[0] ) / 2
        plane_y = (objects['LSAT_ScanMesh0_LandmarkLeftEar'].location[1] + objects['LSAT_ScanMesh0_LandmarkRightEar'].location[1] ) / 2
        plane_z = (objects['LSAT_ScanMesh0_LandmarkLeftEar'].location[2] + objects['LSAT_ScanMesh0_LandmarkRightEar'].location[2] ) / 2
        plane = bpy.ops.mesh.primitive_plane_add(radius=1.2, view_align=False, enter_editmode=False, location=(plane_x, plane_y, plane_z), rotation=(0,math.pi/2,0) )
        
        verts = [ objects['LSAT_ScanMesh0_LandmarkLeftEar'].location,
        objects['LSAT_ScanMesh0_LandmarkNose'].location,
        objects['LSAT_ScanMesh0_LandmarkRightEar'].location ]
        
        faces = [ (0,1,2) ]
        HeadTiltmesh = bpy.data.meshes.new('HeadTilt')
        HeadTiltmesh.from_pydata(verts, [], faces)
        
        HeadTiltmesh.update()
        HeadTilt = bpy.data.objects.new('HeadTiltPlane', HeadTiltmesh)
        
        bpy.context.scene.objects.link(HeadTilt )
        tilt_correction = HeadTiltmesh.polygons[0].normal 
        print( tilt_correction )
        plane = objects['Plane']
        plane.name = 'FlipPlane'
        
        earlobes_dist = abs(objects['LSAT_ScanMesh0_LandmarkLeftEar'].location[0] - objects['LSAT_ScanMesh0_LandmarkRightEar'].location[0] )
        print( earlobes_dist )
        chopboard_plane_z = plane_z - 3.9*earlobes_dist 
        #chopboard_plane_y = (objects['LSAT_ScanMesh0_LandmarkLeftEar'].location[1] + objects['LSAT_ScanMesh0_LandmarkRightEar'].location[1] ) / 2
        #chopboard_plane_z = (objects['LSAT_ScanMesh0_LandmarkLeftEar'].location[2] + objects['LSAT_ScanMesh0_LandmarkRightEar'].location[2] ) / 2
      
        chopboard_cube = bpy.ops.mesh.primitive_cube_add( view_align=False, enter_editmode=False, location=(plane_x, plane_y, chopboard_plane_z) )

        chopboard_cube = objects['Cube']
        chopboard_cube.name = 'ChoppingBoardCube'
        chopboard_cube.scale = (0.02, .02,0.0057)
        
        
        bpy.context.scene.cursor_location = (plane_x, plane_y, plane_z)
        #duplicate the mesh, along the plane
        #the ear. nose landmarks must already set.
        #build the plane. flip it along the plane.
        dupflip_mesh = objects['LSAT_ScanMesh0'].copy()
        dupflip_mesh.name = 'LSAT_ScanMesh0_flip'
        #bpy.context.scene.objects.link(dupflip_mesh )
        #origin_mesh
        
        #rot_mat = Matrix.Rotation( 50, 4, tilt_correction )   # you can also use as axis Y,Z or a custom vector like (x,y,z)

        # decompose world_matrix's components, and from them assemble 4x4 matrices
        orig_loc, orig_rot, orig_scale = dupflip_mesh.matrix_world.decompose()
        #orig_loc.x = plane_x + 0.071
        #orig_loc.y -= plane_y
        #orig_loc.z -= plane_z
        orig_loc_mat = Matrix.Translation( orig_loc )
        #orig_loc_mat = Matrix.Translation( (plane_x,plane_y,plane_z) )
        orig_rot_mat = orig_rot.to_matrix().to_4x4()
        orig_scale_mat = Matrix.Scale(orig_scale[0],4,(1,0,0)) * Matrix.Scale(orig_scale[1],4,(0,1,0)) * Matrix.Scale(orig_scale[2],4,(0,0,1))
        scale_mat = Matrix.Scale(-orig_scale[0],4,(-1,0,0)) * Matrix.Scale(orig_scale[1],4,(0,1,0)) * Matrix.Scale(orig_scale[2],4,(0,0,1))
        
        plane.hide = True
        
        #create & apply boolean operator
        bool_one = origin_mesh.modifiers.new(type="BOOLEAN", name="bool 1")
        bool_one.object = chopboard_cube
        bool_one.operation = 'DIFFERENCE'
        
        #bpy.ops.object.modifier_apply(apply_as='DATA', modifier=bool_one.name)
        
        #calculate volume
        
        bm = bmesh.new()
        bm.from_object(bpy.context.object, bpy.context.scene) # could also use from_mesh() if you don't care about deformation etc.

        print(bm.calc_volume())
        
        plane.hide = True
        return {'FINISHED'}

class LSATGenHeatmapOperator(bpy.types.Operator):
    bl_idname = "lsat.gen_heatmap"
    bl_label = "Generate Heatmap"

    def execute(self, context):
        print("Generate heatmap")
        return {'FINISHED'}    
    
#class to perform additional actions while importing ply
class LSATImportOperator(bpy.types.Operator):
    bl_idname = "lsat.importsetup"
    bl_label = "Import .PLY"
    LSAT_Firstrun = bpy.props.BoolProperty(name="LSATFirstRun",default=True) #for clearing scene
    #filepath is an attribute of the operator type so this name must be used
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    
    #count the number of imported LSAT meshes in the scene
    def countImportedMeshes(self):
        MeshCount = 0
        for PotentialMesh in bpy.context.scene.objects:
            if PotentialMesh.type == 'MESH' and PotentialMesh.name.find("LSAT_ScanMesh") > -1:
                MeshCount += 1
        return MeshCount
    
    #call the operator and open the file selector, the operator only moves into execute once
    #a file has been selected. TODO: add a ply filter
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    #once the file path is chosen, the operator moves to execute mode
    def execute(self, context):
        if self.filepath.split('.')[-1] != 'ply':
            self.report({'INFO'},'Please select a PLY file.')
        else:
            #deselect all objects so we end up only selecting the newly imported object
            bpy.ops.object.select_all(action='DESELECT')
            #change measurements to centimetres
            context.scene.unit_settings.system = 'METRIC'
            context.scene.unit_settings.scale_length = 0.01
            #if this is the first import, clear the scene and set shading to solid
            if(self.LSAT_Firstrun == True):
                context.space_data.viewport_shade = 'SOLID'
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete(use_global=False)
                self.LSAT_Firstrun = False
            #import the ply from the file that was selected in invoke
            bpy.ops.import_mesh.ply(filepath=self.filepath)
            #change the imported object's name and offset location
            bpy.context.object.name = "LSAT_ScanMesh" + str(self.countImportedMeshes())
            bpy.ops.transform.resize(value=(100,100,100))
            bpy.ops.transform.translate(value=(80 * (self.countImportedMeshes() - 1),0,0))
            #assign a new pseudo random color to the object
            LSATNewColor = bpy.data.materials.new(name="LSATMaterial_" + str(self.countImportedMeshes()))
            LSATNewColor.darkness = 0.5
            LSATNewColor.diffuse_color = (random.randint(0,10)/10,random.randint(0,10)/10,random.randint(0,10)/10)
            bpy.context.active_object.data.materials.append(LSATNewColor)
            #zoom the camera into the newly imported object
            bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
        return {'FINISHED'}


class LSATLEarPlaceLandmarkOperator(bpy.types.Operator):
    bl_idname = "lsat.l_ear_place_landmark"
    bl_label = "Place Left Ear Landmark for Alignment in LSAT"

    def execute(self, context):
        if(bpy.context.object == None):
            self.report({'INFO'},'Please select an object.')
            return {'CANCELLED'}
        #first get the name of the currently selected mesh to assign landmarks to
        designatedObjectForLandmark = bpy.context.object.name
        #if it is a landmark we have selected, get the original object from the landmark name
        landmarkOwnerNameEnd = designatedObjectForLandmark.find("_Landmark")
        if(landmarkOwnerNameEnd > -1):
            designatedObjectForLandmark = designatedObjectForLandmark[:landmarkOwnerNameEnd] #chop off the characters which follow the owner name
        print("got designated object for landmark: " + str(designatedObjectForLandmark))
        #if the landmark already exists, remove it
        if(designatedObjectForLandmark + "_LandmarkLeftEar" in bpy.context.scene.objects):
            bpy.context.scene.objects.active = bpy.data.objects[ designatedObjectForLandmark + "_LandmarkLeftEar" ]
            bpy.ops.object.delete(use_global=False)
        #deselect all objects so we end up only selecting the newly created landmark
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1000,1000,1000),radius=2)
        bpy.context.object.name = designatedObjectForLandmark + "_LandmarkLeftEar" 
        if(designatedObjectForLandmark + "_LandmarkNose" in bpy.context.scene.objects):
            LSATTrackToConstraint = bpy.data.objects[designatedObjectForLandmark + "_LandmarkNose"].constraints.new('TRACK_TO')
            LSATTrackToConstraint.target = bpy.data.objects[designatedObjectForLandmark + "_LandmarkLeftEar"]
            if(self.countImportedLandmarks(designatedObjectForLandmark)-1 > 1):
                LSATTrackToConstraint.influence = 0.5
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Left Ear Landmark Placement" )
        bpy.context.scene.objects.active = bpy.data.objects[ designatedObjectForLandmark ]
        																				  
        return {'FINISHED'}


class LSATREarPlaceLandmarkOperator(bpy.types.Operator):
    bl_idname = "lsat.r_ear_place_landmark"
    bl_label = "Place Right Ear Landmark for Alignment in LSAT"

    def execute(self, context):
        if(bpy.context.object == None):
            self.report({'INFO'},'Please select an object.')
            return {'CANCELLED'}
        #first get the name of the currently selected mesh to assign landmarks to
        designatedObjectForLandmark = bpy.context.object.name
        #if it is a landmark we have selected, get the original object from the landmark name
        landmarkOwnerNameEnd = designatedObjectForLandmark.find("_Landmark")
        if(landmarkOwnerNameEnd > -1):
            designatedObjectForLandmark = designatedObjectForLandmark[:landmarkOwnerNameEnd] #chop off the characters which follow the owner name
        print("got designated object for landmark: " + str(designatedObjectForLandmark))
        #if the landmark already exists, remove it
        if(designatedObjectForLandmark + "_LandmarkRightEar" in bpy.context.scene.objects):
            bpy.context.scene.objects.active = bpy.data.objects[ designatedObjectForLandmark + "_LandmarkRightEar" ]
            bpy.ops.object.delete(use_global=False)
        #deselect all objects so we end up only selecting the newly created landmark
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1000,1000,1000),radius=2)
        bpy.context.object.name = designatedObjectForLandmark + "_LandmarkRightEar"
        if(designatedObjectForLandmark + "_LandmarkNose" in bpy.context.scene.objects):
            LSATTrackToConstraint = bpy.data.objects[designatedObjectForLandmark + "_LandmarkNose"].constraints.new('TRACK_TO')
            LSATTrackToConstraint.target = bpy.data.objects[designatedObjectForLandmark + "_LandmarkRightEar"]
            if(self.countImportedLandmarks(designatedObjectForLandmark)-1 > 1):
                LSATTrackToConstraint.influence = 0.5
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Right Ear Landmark Placement" )
        bpy.context.scene.objects.active = bpy.data.objects[ designatedObjectForLandmark ]
        																				  
        return {'FINISHED'}
       
class LSATAutoPlaceLandmarkOperator(bpy.types.Operator):
    bl_idname = "lsat.auto_place_landmark"
    bl_label = "Place Landmark Automatically for Alignment in LSAT"

    #count the number of created landmarks in the scene
    def countImportedLandmarks(self, designatedObject):
        LandmarkCount = 0
        for PotentialLandmark in bpy.context.scene.objects:
            if PotentialLandmark.type == 'EMPTY' and PotentialLandmark.name.find(designatedObject + "_Landmark") > -1:
                LandmarkCount += 1
        return LandmarkCount

    def execute(self, context):
        if(bpy.context.object == None):
            self.report({'INFO'},'Please select an object.')
            return {'CANCELLED'}
        #first get the name of the currently selected mesh to assign landmarks to
        designatedObjectForLandmark = bpy.context.object.name
         #if it is a landmark we have selected, get the original object from the landmark name
        landmarkOwnerNameEnd = designatedObjectForLandmark.find("_Landmark")
        if(landmarkOwnerNameEnd > -1):
            designatedObjectForLandmark = designatedObjectForLandmark[:landmarkOwnerNameEnd] #chop off the characters which follow the owner name
        print("got designated object for landmark: " + str(designatedObjectForLandmark))

        #deselect all objects so we end up only selecting the newly created landmark
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1000,1000,1000),radius=2)
        bpy.context.object.name = designatedObjectForLandmark + "_Landmark" + str(self.countImportedLandmarks(designatedObjectForLandmark))
        if(self.countImportedLandmarks(designatedObjectForLandmark)-1 > 0):
            LSATTrackToConstraint = bpy.data.objects[designatedObjectForLandmark + "_LandmarkNose"].constraints.new('TRACK_TO')
            LSATTrackToConstraint.target = bpy.data.objects[designatedObjectForLandmark + "_Landmark" + str(self.countImportedLandmarks(designatedObjectForLandmark)-1)]
            if(self.countImportedLandmarks(designatedObjectForLandmark)-1 > 1):
                LSATTrackToConstraint.influence = 0.5
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Automatic Landmark Placement" )
        return {'FINISHED'}
            
class LSATNosePlaceLandmarkOperator(bpy.types.Operator):
    bl_idname = "lsat.nose_place_landmark"
    bl_label = "Place Nose Landmark for Alignment in LSAT"

    def execute(self, context):
        if(bpy.context.object == None):
            self.report({'INFO'},'Please select an object.')
            return {'CANCELLED'}
        #first get the name of the currently selected mesh to assign landmarks to
        designatedObjectForLandmark = bpy.context.object.name
        #if the landmark already exists, remove it
        if(designatedObjectForLandmark + "_LandmarkNose" in bpy.context.scene.objects):
            bpy.context.scene.objects.active = bpy.data.objects[ designatedObjectForLandmark + "_LandmarkNose" ]
            bpy.ops.object.delete(use_global=False)
        #deselect all objects so we end up only selecting the newly created landmark
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1000,1000,1000),radius=2)
        bpy.context.object.name = designatedObjectForLandmark + "_LandmarkNose" 
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Nose Landmark Placement" )
        bpy.context.scene.objects.active = bpy.data.objects[ designatedObjectForLandmark ]
        																				  
        return {'FINISHED'}
    
       
#class to place landmarks on the object surface
class LSATPlaceLandmarkOperator(bpy.types.Operator):
    bl_idname = "lsat.placelandmark"
    bl_label = "Place Landmark for Alignment in LSAT"

    #count the number of created landmarks in the scene
    def countImportedLandmarks(self, designatedObject):
        LandmarkCount = 0
        for PotentialLandmark in bpy.context.scene.objects:
            if PotentialLandmark.type == 'EMPTY' and PotentialLandmark.name.find(designatedObject + "_Landmark") > -1:
                LandmarkCount += 1
        return LandmarkCount

    def execute(self, context):
        if(bpy.context.object == None):
            self.report({'INFO'},'Please select an object.')
            return {'CANCELLED'}
        #first get the name of the currently selected mesh to assign landmarks to
        designatedObjectForLandmark = bpy.context.object.name
        #if it is a landmark we have selected, get the original object from the landmark name
        if(designatedObjectForLandmark.find("_Landmark") > -1):
            designatedObjectForLandmark = designatedObjectForLandmark[:-10] #chop off the 9 characters that are _Landmark at the end

        
        #deselect all objects so we end up only selecting the newly created landmark
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1000,1000,1000),radius=2)
        bpy.context.object.name = designatedObjectForLandmark + "_Landmark" + str(self.countImportedLandmarks(designatedObjectForLandmark))
        if(self.countImportedLandmarks(designatedObjectForLandmark)-1 > 0):
            LSATTrackToConstraint = bpy.data.objects[designatedObjectForLandmark + "_Landmark0"].constraints.new('TRACK_TO')
            LSATTrackToConstraint.target = bpy.data.objects[designatedObjectForLandmark + "_Landmark" + str(self.countImportedLandmarks(designatedObjectForLandmark)-1)]
            if(self.countImportedLandmarks(designatedObjectForLandmark)-1 > 1):
                LSATTrackToConstraint.influence = 0.5
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        return {'FINISHED'}
    
#class to align the 3d scans using the landmarks
class LSATAlignScansOperator(bpy.types.Operator):
    bl_idname = "lsat.alignscans"
    bl_label = "Align 3D Scans for LSAT"

    #count the number of imported LSAT meshes in the scene
    def countImportedMeshes(self):
        MeshCount = 0
        for PotentialMesh in bpy.context.scene.objects:
            if PotentialMesh.type == 'MESH' and PotentialMesh.name.find("LSAT_ScanMesh") > -1:
                MeshCount += 1
        return MeshCount

    #count the maximum number of landmarks that is associated to any one mesh
    def countImportedLandmarks(self):
        MaximumLandmarkCount = -1
        for PotentialLandmark in bpy.context.scene.objects:
            LocationPotentialLandmarkName = PotentialLandmark.name.find("_Landmark")
            if(PotentialLandmark.type == 'EMPTY' and LocationPotentialLandmarkName > -1):
                if(int(PotentialLandmark.name[LocationPotentialLandmarkName + 9:]) > MaximumLandmarkCount):
                    MaximumLandmarkCount = int(PotentialLandmark.name[LocationPotentialLandmarkName + 9:])
        return MaximumLandmarkCount
													
    def execute(self, context):
        #get the maximum count of any landmark collection
        LSATLandmarkCount = self.countImportedLandmarks()
        if(LSATLandmarkCount < 0):
            return {'CANCELLED'}
        #create a dictionary of landmark sets
        LSATValidLandmarkSets = {}
        #iterate through only the number of possible landmark sets that there are
        for LSATPotentialLandmarkSet in range(0,LSATLandmarkCount+1):
            LSATMeshCount = self.countImportedMeshes()
            #each set must have 2 points in it, this counts those two points
            LSATSetCounter = 0
            #iterate through all meshes in the context of the current potential landmark pair
            for LSATMeshNumber in range(0,LSATMeshCount):
                LSATMeshName = "LSAT_ScanMesh" + str(LSATMeshNumber)
                if(LSATMeshName + "_Landmark" + str(LSATPotentialLandmarkSet) in bpy.context.scene.objects):
                    LSATSetCounter += 1
                if(LSATSetCounter == 2): #if a pair is found, add a landmark set to the dictionary
                    LSATValidLandmarkSets["LandmarkSet" + str(len(LSATValidLandmarkSets))] = LSATMeshCount - 1
        
        #iterate through all meshes that have landmarks and parent the mesh to the first landmark
        for LSATScanMesh in range(0,LSATValidLandmarkSets['LandmarkSet0']+1):
            LSATMeshName = "LSAT_ScanMesh" + str(LSATScanMesh)
            LSATLandmarkName = LSATMeshName + "_Landmark0"
            bpy.context.scene.objects.active = bpy.data.objects[LSATLandmarkName]
            bpy.ops.nla.bake(frame_start=1,frame_end=1,step=1,only_selected=True,visual_keying=True,clear_constraints=True,use_current_action=True,bake_types={'OBJECT'})
            bpy.data.objects[LSATMeshName].parent = bpy.data.objects[LSATLandmarkName]
            bpy.data.objects[LSATMeshName].matrix_parent_inverse = bpy.data.objects[LSATLandmarkName].matrix_world.inverted()
            #bpy.data.objects[LSATLandmarkName].
            
        for LSATScanMesh in range(1,LSATValidLandmarkSets['LandmarkSet0']+1):
            LSATCopyLocationConstraint = bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_Landmark0'].constraints.new('COPY_LOCATION')
            LSATCopyLocationConstraint.target = bpy.data.objects['LSAT_ScanMesh0_Landmark0']
            LSATCopyRotationConstraint = bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_Landmark0'].constraints.new('COPY_ROTATION')
            LSATCopyRotationConstraint.target = bpy.data.objects['LSAT_ScanMesh0_Landmark0']
            bpy.context.scene.objects.active = bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_Landmark0']
            bpy.ops.nla.bake(frame_start=1,frame_end=1,step=1,only_selected=True,visual_keying=True,clear_constraints=True,use_current_action=True,bake_types={'OBJECT'})
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_Landmark0'].select = True

										
														 
												   
															
												   
															 
												   
        #zoom the camera into the manual alignment landmark and activate manual rotation tweak
        bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
        context.scene.tool_settings.use_snap = False
        #use trackball for manual alignment, but running it straight after auto align breaks the result!
        #bpy.ops.transform.trackball('INVOKE_DEFAULT') 
        print( "Auto Alignment")    
        return {'FINISHED'}

#this function is called when the addon is loaded into Blender
def register():
    bpy.utils.register_class(LSAT_SetupPanel)
    bpy.utils.register_class(LSAT_PointPlacementPanel)
    bpy.utils.register_class(LSAT_ScanAlignmentPanel)
    bpy.utils.register_class(LSAT_VolumePanel)
    bpy.utils.register_class(LSAT_MapPanel)
    bpy.utils.register_class(LSATImportOperator)
    bpy.utils.register_class(LSATNosePlaceLandmarkOperator)
    bpy.utils.register_class(LSATLEarPlaceLandmarkOperator)
    bpy.utils.register_class(LSATREarPlaceLandmarkOperator)
    bpy.utils.register_class(LSATAutoPlaceLandmarkOperator)
    bpy.utils.register_class(LSATPlaceLandmarkOperator)
    bpy.utils.register_class(LSATAlignScansOperator)
    bpy.utils.register_class(LSATVolSelectionOperator)
    bpy.utils.register_class(LSATVolExtractionOperator)
    bpy.utils.register_class(LSATVolMeasureDiffOperator)
    bpy.utils.register_class(LSATGenHeatmapOperator)
    
    print("LSAT loaded")
#this function is called when the addon is unloaded from Blender 
def unregister():
    bpy.utils.unregister_class(LSAT_SetupPanel)
    bpy.utils.unregister_class(LSAT_PointPlacementPanel)
    bpy.utils.unregister_class(LSAT_ScanAlignmentPanel)
    bpy.utils.unregister_class(LSAT_VolumePanel)
    bpy.utils.unregister_class(LSAT_MapPanel)
    bpy.utils.unregister_class(LSATImportOperator)
    bpy.utils.unregister_class(LSATNosePlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATLEarPlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATREarPlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATAutoPlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATPlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATAlignScansOperator)
    bpy.utils.unregister_class(LSATVolSelectionOperator)
    bpy.utils.unregister_class(LSATVolExtractionOperator)
    bpy.utils.unregister_class(LSATVolMeasureDiffOperator)
    bpy.utils.unregister_class(LSATGenHeatmapOperator)
    print("LSAT unloaded")

#for the purpose of testing, the following lines will allow the addon to be registered 
#when this script is run in the Blender python IDE, without having to register the addon in 
if __name__ == '__main__':
    register()
