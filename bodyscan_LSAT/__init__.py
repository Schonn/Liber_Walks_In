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
    "author": "Ivan Prga, Annette Nguyen, Abdullah Albeladi, Jaspreet Kaur., Michael Stagg, Maxwell Heaysman, Schonn-Pierre Hirst",
    "version": (1, 0, 0),
    "blender": (2, 7, 4),
    "description": "A toolset for importing, aligning and analysing 3D scans of lymphoedema patients.",
    "category": "Mesh"
    }

#import blender python IDE libraries
import bpy
#use the following format to import other .py files from the local folder to make use of the contained classes/definitions
#from . import (
#        import_PLY_3DScan,
#        register_landmark,
#     align_scans,
#     extract_volume,
#     generate_heatmap
#        )

class ImportModelOperator(bpy.types.Operator):
    bl_idname = "wm.import_model"
    bl_label = "Import Model"

    def execute(self, context):
        print("Import Model")
        return {'FINISHED'}
		
class DetectLandMarksOperator(bpy.types.Operator):
    bl_idname = "wm.detect_landmarks"
    bl_label = "Autodetect Landmarks"

    def execute(self, context):
        print("Autodetect Landmarks")
        return {'FINISHED'}
		
        row.operator( "wm.select_area" )
        row.operator( "wm.gen_heatmap" )
class PlaceNoseOperator(bpy.types.Operator):
    bl_idname = "wm.place_nose_lm"
    bl_label = "Place Nose"

    def execute(self, context):
        print("Place Nose")
        return {'FINISHED'}

		
class PlaceLeftEarOperator(bpy.types.Operator):
    bl_idname = "wm.place_lear_lm"
    bl_label = "Place Left Ear"

    def execute(self, context):
        print("Place Left Ear")
        return {'FINISHED'}

		
class PlaceRightEarOperator(bpy.types.Operator):
    bl_idname = "wm.place_rear_lm"
    bl_label = "Place Right Ear"

    def execute(self, context):
        print("Place Right Ear")
        return {'FINISHED'}
		
class AutomaticalignmentOperator(bpy.types.Operator):
    bl_idname = "wm.auto_align"
    bl_label = "Automatic alignment"

    def execute(self, context):
        print("Auto matic alignment")
        return {'FINISHED'}

class SelectAreaOperator(bpy.types.Operator):
    bl_idname = "wm.select_area"
    bl_label = "Select Area (Vol. Extraction)"

    def execute(self, context):
        print("Select Area ")
        return {'FINISHED'}

		

class GenHeatmapOperator(bpy.types.Operator):
    bl_idname = "wm.gen_heatmap"
    bl_label = "Generate Heatmap"

    def execute(self, context):
        print("Generate heatmap")
        return {'FINISHED'}

		
class LymphodemaToolPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Lymphodema Tool Panel"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")

        row = layout.row()
        row.operator( "wm.import_model" )
		
        row = layout.row()
        row.operator( "wm.detect_landmarks" )
		
		
        row = layout.row()
        row.operator( "wm.place_nose_lm" )
        row.operator( "wm.place_lear_lm" )
        row.operator( "wm.place_rear_lm" )
		
        row = layout.row()
        row.operator( "wm.auto_align" )
		
        row = layout.row()
        row.operator( "wm.select_area" )
		
		
        row = layout.row()
        row.operator( "wm.gen_heatmap" )
        
#this function is called when the addon is loaded into Blender
def register():
    print("LSAT loaded")
    bpy.utils.register_class(LymphodemaToolPanel)
    bpy.utils.register_class(ImportModelOperator)
    bpy.utils.register_class(DetectLandMarksOperator)
    bpy.utils.register_class(PlaceNoseOperator)
    bpy.utils.register_class(PlaceLeftEarOperator)
    bpy.utils.register_class(PlaceRightEarOperator)
    bpy.utils.register_class(SelectAreaOperator)
    bpy.utils.register_class(GenHeatmapOperator)
    bpy.utils.register_class(AutomaticalignmentOperator)

#this function is called when the addon is unloaded from Blender 
def unregister():
    print("LSAT unloaded")
    bpy.utils.unregister_class(LymphodemaToolPanel)
    bpy.utils.unregister_class(ImportModelOperator)
    bpy.utils.unregister_class(DetectLandMarksOperator)
    bpy.utils.unregister_class(PlaceNoseOperator)
    bpy.utils.unregister_class(PlaceLeftEarOperator)
    bpy.utils.unregister_class(PlaceRightEarOperator)
    bpy.utils.unregister_class(SelectAreaOperator)
    bpy.utils.unregister_class(GenHeatmapOperator)
    bpy.utils.unregister_class(AutomaticalignmentOperator)


#for the purpose of testing, the following lines will allow the addon to be registered 
#when this script is run in the Blender python IDE, without having to register the addon in 
if __name__ == '__main__':
    register()
