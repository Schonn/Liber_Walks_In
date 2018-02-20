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
    "version": (1, 0, 2),
    "blender": (2, 7, 4),
    "description": "A toolset for importing, aligning and analysing 3D body scans.",
    "category": "Mesh"
    }

#import blender python libraries
import bpy
#import python random for colour generation
import random
import math
import bmesh
import mathutils
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
        self.layout.operator('lsat.importsetup', text ='Import PLY or OBJ')
        self.layout.operator('lsat.correct_rotation', text ='Flip Selected Scan')
        
#Point placement panel class
class LSAT_PointPlacementPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Point Placement'
    bl_context = 'objectmode'
    bl_category = 'Scan'
    
    def draw(self, context):
        self.layout.operator('lsat.sagittal_plane', text ='Create Sagittal Plane')
        self.layout.operator('lsat.transverse_axial_plane', text ='Create Transverse Axial Plane')
        self.layout.operator('lsat.coronal_plane', text ='Create Coronal Plane')
        self.layout.operator('lsat.nose_place_landmark', text ='Place Nose Landmark')
        self.layout.operator('lsat.l_ear_place_landmark', text ='Place Left Ear Landmark')
        self.layout.operator('lsat.r_ear_place_landmark', text ='Place Right Ear Landmark')
        self.layout.operator('lsat.placelandmark', text ='Place Generic Landmark')
        #self.layout.operator('lsat.auto_place_landmark', text ='Autodetect Landmark Placement')

#Scan Alignment panel class
class LSAT_ScanAlignmentPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Scan Alignment'
    bl_context = 'objectmode'
    bl_category = 'Scan'
    def draw(self, context):
        self.layout.operator('lsat.alignscans', text ='Auto Align Using Landmarks')
        
#Volume panel class
class LSAT_VolumePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Volume'
    bl_context = 'objectmode'
    bl_category = 'Scan'
    def draw(self, context):
        self.layout.operator('lsat.vol_select_area_y', text ='Select Coronal')
        self.layout.operator('lsat.vol_select_area_x', text ='Select Sagittal')
        self.layout.operator('lsat.vol_measure_diff', text ='Measure Volume Of Selected')
        
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

class LSATSagittalPlaneOperator(bpy.types.Operator):
    bl_idname = "lsat.sagittal_plane"
    bl_label = "Place Sagittal Plane"

    def execute(self, context):
        context.scene.tool_settings.use_snap = False
        bpy.ops.mesh.primitive_plane_add(radius=100, view_align=False, enter_editmode=False, location=(0,0,0))
        bpy.ops.transform.rotate(value=1.5708,axis=(1,0,0))
        bpy.ops.transform.rotate(value=1.5708,axis=(0,0,1))
        bpy.ops.transform.translate('INVOKE_DEFAULT',constraint_axis=(True,False,False),constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')
        print("Sagittal Plane Placed")
        return {'FINISHED'}    

class LSATCoronalPlaneOperator(bpy.types.Operator):
    bl_idname = "lsat.coronal_plane"
    bl_label = "Place Coronal Plane"

    def execute(self, context):
        context.scene.tool_settings.use_snap = False
        bpy.ops.mesh.primitive_plane_add(radius=100, view_align=False, enter_editmode=False, location=(0,0,0))
        bpy.ops.transform.rotate(value=1.5708,axis=(1,0,0))
        bpy.ops.transform.translate('INVOKE_DEFAULT',constraint_axis=(False,True,False),constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')
        print("Coronal Plane Placed")
        return {'FINISHED'}  
    
class LSATTransverseAxialPlaneOperator(bpy.types.Operator):
    bl_idname = "lsat.transverse_axial_plane"
    bl_label = "Place Transverse Axial Plane"

    def execute(self, context):
        context.scene.tool_settings.use_snap = False
        bpy.ops.mesh.primitive_plane_add(radius=100, view_align=False, enter_editmode=False, location=(0,0,0))
        bpy.ops.transform.translate('INVOKE_DEFAULT',constraint_axis=(False,False,True),constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')
        print("Transverse Axial Plane Placed")
        return {'FINISHED'}

class LSATVolSelectionOperatorY(bpy.types.Operator):
    bl_idname = "lsat.vol_select_area_y"
    bl_label = "Coronal Area Selection"

    def execute(self, context):
        if(not "LSAT_ScanMeshCombined" in bpy.data.objects):
            #deselect everything so only the desired meshes are selected
            bpy.ops.object.select_all(action='DESELECT')
            #TODO: add a for loop here to flip all meshes and combine them all
            bpy.data.objects["LSAT_ScanMesh1"].select = True
            bpy.context.scene.objects.active = bpy.data.objects["LSAT_ScanMesh1"]
            #quickly go into edit mode and flip the normals
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.flip_normals()
            #return to object mode
            bpy.ops.object.mode_set()
            #add the first mesh to the selection and join all meshes
            bpy.data.objects["LSAT_ScanMesh0"].select = True
            bpy.ops.object.join()
            bpy.context.object.name = "LSAT_ScanMeshCombined" 
            bpy.ops.object.select_all(action='DESELECT')
        
        #make sphere and add shrinkwrap
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5,size=3,location=(1000,1000,1000))
        bpy.context.object.name = "LSAT_VolumeSelectSphere" 
        volumeSelectShrinkWrap = bpy.context.object.modifiers.new(type='SHRINKWRAP', name="shrinkWrap1")
        volumeSelectShrinkWrap.target = bpy.data.objects["LSAT_ScanMeshCombined"]
        volumeSelectShrinkWrap.wrap_method = 'PROJECT'
        volumeSelectShrinkWrap.use_negative_direction = True
        volumeSelectShrinkWrap.use_positive_direction = True
        volumeSelectShrinkWrap.use_project_y = True
        volumeSelectShrinkWrap.use_project_x = False
        volumeSelectShrinkWrap.use_project_z = False
        volumeSelectShrinkWrap.cull_face = 'OFF'
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Select Area")
        return {'FINISHED'}
    
class LSATVolSelectionOperatorX(bpy.types.Operator):
    bl_idname = "lsat.vol_select_area_x"
    bl_label = "Sagittal Area Selection"

    def execute(self, context):
        if(not "LSAT_ScanMeshCombined" in bpy.data.objects):
            #deselect everything so only the desired meshes are selected
            bpy.ops.object.select_all(action='DESELECT')
            #TODO: add a for loop here to flip all meshes and combine them all
            bpy.data.objects["LSAT_ScanMesh1"].select = True
            bpy.context.scene.objects.active = bpy.data.objects["LSAT_ScanMesh1"]
            #quickly go into edit mode and flip the normals
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.flip_normals()
            #return to object mode
            bpy.ops.object.mode_set()
            #add the first mesh to the selection and join all meshes
            bpy.data.objects["LSAT_ScanMesh0"].select = True
            bpy.ops.object.join()
            bpy.context.object.name = "LSAT_ScanMeshCombined" 
            bpy.ops.object.select_all(action='DESELECT')
        
        #make sphere and add shrinkwrap
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5,size=3,location=(1000,1000,1000))
        bpy.context.object.name = "LSAT_VolumeSelectSphere" 
        volumeSelectShrinkWrap = bpy.context.object.modifiers.new(type='SHRINKWRAP', name="shrinkWrap1")
        volumeSelectShrinkWrap.target = bpy.data.objects["LSAT_ScanMeshCombined"]
        volumeSelectShrinkWrap.wrap_method = 'PROJECT'
        volumeSelectShrinkWrap.use_negative_direction = True
        volumeSelectShrinkWrap.use_positive_direction = True
        volumeSelectShrinkWrap.use_project_y = False
        volumeSelectShrinkWrap.use_project_x = True
        volumeSelectShrinkWrap.use_project_z = False
        volumeSelectShrinkWrap.cull_face = 'OFF'
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Select Area")
        return {'FINISHED'}
    
class LSATVolMeasureDiffOperator(bpy.types.Operator):
    bl_idname = "lsat.vol_measure_diff"
    bl_label = "Measure Total Difference"

    #derived from object_print3d_utils.py from the print 3d plugin
    def clean_float(self,text):
        # strip trailing zeros: 0.000 -> 0.0
        index = text.rfind(".")
        if index != -1:
            index += 2
            head, tail = text[:index], text[index:]
            tail = tail.rstrip("0")
            text = head + tail
        return text

    def execute(self, context):
        print("Measure Total Difference")
        contextSelectionSphere = context.active_object.to_mesh(bpy.context.scene, True, 'PREVIEW', calc_tessface=False)
        volumeMeshHelper = bmesh.new()
        volumeMeshHelper.from_mesh(contextSelectionSphere)
        bpy.data.meshes.remove(contextSelectionSphere)
        bmesh.ops.triangulate(volumeMeshHelper, faces=volumeMeshHelper.faces)

        volume = volumeMeshHelper.calc_volume()
        volumeMeshHelper.free()
        print("Volume: %s cm³" % self.clean_float("%.4f" % ((volume * (context.scene.unit_settings.scale_length ** 3.0)) / (0.01 ** 3.0))))
        
        LSATSelectedVolume = context.active_object
        bpy.ops.view3d.snap_cursor_to_selected()
        LSATTextObject = bpy.ops.object.text_add(radius=1,view_align=True)
        bpy.data.objects["Text"].data.body = "Volume: %s cm³" % self.clean_float("%.4f" % ((volume * (context.scene.unit_settings.scale_length ** 3.0)) / (0.01 ** 3.0)))
        bpy.data.objects["Text"].show_x_ray = True
        bpy.data.objects["Text"].name = "LSAT_MeasurementText"
        LSATNewColor = bpy.data.materials.new(name="LSATTextBlack")
        LSATNewColor.darkness = 0
        LSATNewColor.diffuse_color = (0,0,0)
        LSATNewColor.use_shadeless = True
        bpy.context.active_object.data.materials.append(LSATNewColor)
        bpy.context.scene.objects.active = LSATSelectedVolume
        return {'FINISHED'}

class LSATGenHeatmapOperator(bpy.types.Operator):
    bl_idname = "lsat.gen_heatmap"
    bl_label = "Generate Heatmap"

    def execute(self, context):
        print("Generate heatmap")
        return {'FINISHED'}    
    
#class to correct upside down rotation
class LSATCorrectRotationOperator(bpy.types.Operator):
    bl_idname = "lsat.correct_rotation"
    bl_label = "Correct Rotation of a Structure Scan"
    
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.transform.rotate(value=3.14159,axis=(1,0,0))
        print("Corrected rotation")
        return {'FINISHED'} 

#class to perform additional actions while importing ply or obj
class LSATImportOperator(bpy.types.Operator):
    bl_idname = "lsat.importsetup"
    bl_label = "Import .PLY or .OBJ"
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
    #a file has been selected.
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    #once the file path is chosen, the operator moves to execute mode
    def execute(self, context):
        importType = None
        if self.filepath.split('.')[-1] != 'ply' and self.filepath.split('.')[-1] != 'obj':
            self.report({'INFO'},'Please select a PLY or OBJ file.')
        else:
            importType = self.filepath.split('.')[-1]
            #deselect all objects so we end up only selecting the newly imported object
            bpy.ops.object.select_all(action='DESELECT')
            #change measurements to centimetres
            context.scene.unit_settings.system = 'METRIC'
            context.scene.unit_settings.scale_length = 0.01
            #if this is the first import, clear the scene and set shading to Texture
            if(self.LSAT_Firstrun == True):
                context.space_data.viewport_shade = 'TEXTURED'
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete(use_global=False)
                self.LSAT_Firstrun = False
            #import the ply or obj from the file that was selected in invoke
            if(importType == 'ply'):
                bpy.ops.import_mesh.ply(filepath=self.filepath)
            elif(importType == 'obj'):
                bpy.ops.import_scene.obj(filepath=self.filepath)
            bpy.context.scene.objects.active = bpy.context.selected_objects[0]
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
  
        #deselect all objects so we end up only selecting the newly created landmark
        bpy.ops.object.select_all(action='DESELECT')
        #if the landmark already exists, remove it
        if(designatedObjectForLandmark + "_LandmarkLeftEar" in bpy.context.scene.objects):
            bpy.data.objects[designatedObjectForLandmark + "_LandmarkLeftEar"].select = True
            bpy.ops.object.delete(use_global=False)
            
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1000,1000,1000),radius=2)
        bpy.context.object.name = designatedObjectForLandmark + "_LandmarkLeftEar" 
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Left Ear Landmark Placement" )
        bpy.context.scene.objects.active = bpy.data.objects[designatedObjectForLandmark]
        																				  
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

        #deselect all objects so we end up only selecting the newly created landmark
        bpy.ops.object.select_all(action='DESELECT')
        #if the landmark already exists, remove it
        if(designatedObjectForLandmark + "_LandmarkRightEar" in bpy.context.scene.objects):
            bpy.data.objects[designatedObjectForLandmark + "_LandmarkRightEar"].select = True
            bpy.ops.object.delete(use_global=False)
            
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1000,1000,1000),radius=2)
        bpy.context.object.name = designatedObjectForLandmark + "_LandmarkRightEar"
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Right Ear Landmark Placement" )
        bpy.context.scene.objects.active = bpy.data.objects[ designatedObjectForLandmark ]
        																				  
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
        bpy.ops.object.select_all(action='DESELECT')
        if(designatedObjectForLandmark + "_LandmarkNose" in bpy.context.scene.objects):
            bpy.data.objects[designatedObjectForLandmark + "_LandmarkNose"].select = True
            bpy.ops.object.delete(use_global=False)
        #deselect all objects so we end up only selecting the newly created landmark
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1000,1000,1000),radius=2)
        bpy.context.object.name = designatedObjectForLandmark + "_LandmarkNose" 
        context.scene.tool_settings.use_snap = True
        context.scene.tool_settings.snap_element = 'FACE'
        context.scene.tool_settings.use_snap_align_rotation = False
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        print("Nose Landmark Placement" )
        bpy.context.scene.objects.active = bpy.data.objects[ designatedObjectForLandmark ]
        																				  
        return {'FINISHED'}
    
       
#class to place generic landmarks on the object surface
class LSATPlaceLandmarkOperator(bpy.types.Operator):
    bl_idname = "lsat.placelandmark"
    bl_label = "Place Generic Landmark"

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
    
#class to align the 3d meshes, this class chooses head landmarks over generic, but it will work out which one is in use
class LSATAlignScansOperator(bpy.types.Operator):
    bl_idname = "lsat.alignscans"
    bl_label = "Align Meshes using Landmarks"

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
    
    #check to see if the landmark mode is nose, leftear, rightear or if it's iterated instead
    def checkUniqueLandmarkUse(self):
        UsingUniqueLandmarks = False
        NamedLandmarks = {'Nose': False, 'LeftEar': False, 'RightEar': False}
        for MeshNumber in range(self.countImportedMeshes()):
            if("LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkNose" in bpy.context.scene.objects):
                NamedLandmarks['Nose'] = True
            else:
                NamedLandmarks['Nose'] = False
            if("LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkLeftEar" in bpy.context.scene.objects):
                NamedLandmarks['LeftEar'] = True
            else:
                NamedLandmarks['LeftEar'] = False
            if("LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkRightEar" in bpy.context.scene.objects):
                NamedLandmarks['RightEar'] = True
            else:
                NamedLandmarks['RightEar'] = False
        if(NamedLandmarks['Nose'] == True and NamedLandmarks['LeftEar'] == True and NamedLandmarks['RightEar'] == True):
            UsingUniqueLandmarks = True
        return UsingUniqueLandmarks
	
    #perform head rotation correction at the same time as the scans are aligned
    def correctHeadRotation(self):
        originMesh = bpy.context.scene.objects['LSAT_ScanMesh0']
        sceneObjects = bpy.context.scene.objects
        #create a triangle connecting the left ear, right ear and nose landmarks
        HeadTiltPlaneVertices = [sceneObjects[originMesh.name + "_LandmarkLeftEar"].location, sceneObjects[originMesh.name + "_LandmarkNose"].location,sceneObjects[originMesh.name + "_LandmarkRightEar"].location]
        HeadTiltPlaneFace = [(0,2,1)] #order to get normal facing upwards
        HeadTiltPlaneMesh = bpy.data.meshes.new('HeadTiltPlane')
        HeadTiltPlaneMesh.from_pydata(HeadTiltPlaneVertices, [], HeadTiltPlaneFace)     
        HeadTiltPlaneMesh.update()
        HeadTiltPlaneObject = bpy.data.objects.new('HeadTiltPlane', HeadTiltPlaneMesh)
        sceneObjects.link(HeadTiltPlaneObject)
        #apply the origin point of the triangle
        bpy.ops.object.select_all(action='DESELECT')
        HeadTiltPlaneObject.select = True
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        #add an empty to copy the normal rotation of the triangle mesh
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0),radius=2)
        bpy.context.object.name = originMesh.name + "_HeadTiltOrientation"
        bpy.context.object.parent = HeadTiltPlaneObject
        HeadTiltPlaneObject.dupli_type = 'FACES'
        HeadTiltPlaneObject.select = True
        bpy.ops.object.duplicates_make_real()
        #delete the template empty and rename the empty with the correct rotations
        bpy.ops.object.select_all(action='DESELECT')
        sceneObjects[originMesh.name + "_HeadTiltOrientation"].select = True
        bpy.ops.object.delete(use_global=False)
        bpy.ops.object.select_all(action='DESELECT')
        sceneObjects[originMesh.name + "_HeadTiltOrientation.001"].name = originMesh.name + "_HeadTiltOrientation"
        #parent the target mesh to the nose landmark in case the alignment step has not been run
        originMesh.parent = sceneObjects[originMesh.name + "_LandmarkNose"]
        originMesh.matrix_parent_inverse = sceneObjects[originMesh.name + "_LandmarkNose"].matrix_world.inverted()
        #parent the nose landmark to the rotation correction empty, keeping parent offset
        sceneObjects[originMesh.name + "_LandmarkNose"].parent = sceneObjects[originMesh.name + "_HeadTiltOrientation"]
        sceneObjects[originMesh.name + "_LandmarkNose"].matrix_parent_inverse = sceneObjects[originMesh.name + "_HeadTiltOrientation"].matrix_world.inverted()
        #reset the rotation of the rotation correction empty to remove head offset
        bpy.ops.object.select_all(action='DESELECT')
        sceneObjects[originMesh.name + "_HeadTiltOrientation"].select = True
        bpy.context.scene.objects.active = sceneObjects[originMesh.name + "_HeadTiltOrientation"]
        bpy.context.object.rotation_euler[0] = 0
        bpy.context.object.rotation_euler[1] = 0

    def execute(self, context):
        #are the landmarks labeled nose, left ear, right ear
        LSATUsingUniqueLandmarks = self.checkUniqueLandmarkUse()
        #if the landmarks are nose, left ear and right ear
        if(LSATUsingUniqueLandmarks == True):
            print( "Unique Landmark Alignment") 
            #iterate through all LSAT scans in the scene and set up the nose constraints so the nose landmark points between the ear landmarks
            for MeshNumber in range(self.countImportedMeshes()):
                LSATLeftEarTrackToConstraint = bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkNose"].constraints.new('TRACK_TO')
                LSATLeftEarTrackToConstraint.target = bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkLeftEar"]
                LSATLeftEarTrackToConstraint.influence = 1 #first influence must be maximum
                LSATRightEarTrackToConstraint = bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkNose"].constraints.new('TRACK_TO')
                LSATRightEarTrackToConstraint.target = bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkRightEar"]
                LSATRightEarTrackToConstraint.influence = 0.5 #second influence is half so that the landmark points to the middle of both ears
                #bake the location and rotation of the nose landmark and parent the current iterated mesh to its nose landmark
                bpy.context.scene.objects.active = bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkNose"]
                bpy.ops.nla.bake(frame_start=1,frame_end=1,step=1,only_selected=True,visual_keying=True,clear_constraints=True,use_current_action=True,bake_types={'OBJECT'})
                bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber)].parent = bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkNose"]
                bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber)].matrix_parent_inverse = bpy.data.objects["LSAT_ScanMesh" + str(MeshNumber) + "_LandmarkNose"].matrix_world.inverted()
            #iterate through all LSAT scans in the scene and snap the nose landmarks to the nose landmark of the first scan
            for LSATScanMesh in range(1,self.countImportedMeshes()):
                LSATCopyLocationConstraint = bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_LandmarkNose'].constraints.new('COPY_LOCATION')
                LSATCopyLocationConstraint.target = bpy.data.objects['LSAT_ScanMesh0_LandmarkNose']
                LSATCopyRotationConstraint = bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_LandmarkNose'].constraints.new('COPY_ROTATION')
                LSATCopyRotationConstraint.target = bpy.data.objects['LSAT_ScanMesh0_LandmarkNose']
                bpy.context.scene.objects.active = bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_LandmarkNose']
                bpy.ops.nla.bake(frame_start=1,frame_end=1,step=1,only_selected=True,visual_keying=True,clear_constraints=True,use_current_action=True,bake_types={'OBJECT'})
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_LandmarkNose'].select = True
                #zoom the camera into the manual alignment landmark
                bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
                #as long as the iterated mesh is not the first, parent subsequent nose landmarks to the first scan's nose landmark so that head rotation correction corrects all heads
                if(LSATScanMesh != 0):
                    bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_LandmarkNose'].parent = bpy.data.objects['LSAT_ScanMesh0_LandmarkNose']
                    bpy.data.objects['LSAT_ScanMesh' + str(LSATScanMesh) + '_LandmarkNose'].matrix_parent_inverse = bpy.data.objects['LSAT_ScanMesh0_LandmarkNose'].matrix_world.inverted()
                    self.correctHeadRotation()
        elif(LSATUsingUniqueLandmarks == False): #not using nose and ear labeled landmarks
            #get the maximum count of any numeric landmark collection
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
                #zoom the camera into the manual alignment landmark
                bpy.ops.view3d.view_selected('INVOKE_DEFAULT')			 										   
        context.scene.tool_settings.use_snap = False
        print( "Auto Alignment")    
        return {'FINISHED'}

#this function is called when the addon is loaded into Blender
def register():
    bpy.utils.register_class(LSAT_SetupPanel)
    bpy.utils.register_class(LSAT_PointPlacementPanel)
    bpy.utils.register_class(LSAT_ScanAlignmentPanel)
    bpy.utils.register_class(LSAT_VolumePanel)
    #bpy.utils.register_class(LSAT_MapPanel)
    bpy.utils.register_class(LSATImportOperator)
    bpy.utils.register_class(LSATNosePlaceLandmarkOperator)
    bpy.utils.register_class(LSATLEarPlaceLandmarkOperator)
    bpy.utils.register_class(LSATREarPlaceLandmarkOperator)
    #bpy.utils.register_class(LSATAutoPlaceLandmarkOperator)
    bpy.utils.register_class(LSATCorrectRotationOperator)
    bpy.utils.register_class(LSATPlaceLandmarkOperator)
    bpy.utils.register_class(LSATAlignScansOperator)
    bpy.utils.register_class(LSATVolSelectionOperatorY)
    bpy.utils.register_class(LSATVolSelectionOperatorX)
    bpy.utils.register_class(LSATVolMeasureDiffOperator)
    bpy.utils.register_class(LSATGenHeatmapOperator)
    bpy.utils.register_class(LSATSagittalPlaneOperator)
    bpy.utils.register_class(LSATCoronalPlaneOperator)
    bpy.utils.register_class(LSATTransverseAxialPlaneOperator)
    
    print("LSAT loaded")
#this function is called when the addon is unloaded from Blender 
def unregister():
    bpy.utils.unregister_class(LSAT_SetupPanel)
    bpy.utils.unregister_class(LSAT_PointPlacementPanel)
    bpy.utils.unregister_class(LSAT_ScanAlignmentPanel)
    bpy.utils.unregister_class(LSAT_VolumePanel)
    #bpy.utils.unregister_class(LSAT_MapPanel)
    bpy.utils.unregister_class(LSATImportOperator)
    bpy.utils.unregister_class(LSATNosePlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATLEarPlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATREarPlaceLandmarkOperator)
    #bpy.utils.unregister_class(LSATAutoPlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATCorrectRotationOperator)
    bpy.utils.unregister_class(LSATPlaceLandmarkOperator)
    bpy.utils.unregister_class(LSATAlignScansOperator)
    bpy.utils.unregister_class(LSATVolSelectionOperatorY)
    bpy.utils.unregister_class(LSATVolSelectionOperatorX)
    bpy.utils.unregister_class(LSATVolMeasureDiffOperator)
    bpy.utils.unregister_class(LSATGenHeatmapOperator)
    bpy.utils.unregister_class(LSATSagittalPlaneOperator)
    bpy.utils.unregister_class(LSATCoronalPlaneOperator)
    bpy.utils.unregister_class(LSATTransverseAxialPlaneOperator)
    print("LSAT unloaded")

#for the purpose of testing, the following lines will allow the addon to be registered 
#when this script is run in the Blender python IDE, without having to register the addon in 
if __name__ == '__main__':
    register()
    print("start")
