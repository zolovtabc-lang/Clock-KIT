import bpy
import os
from datetime import datetime

bl_info = {
    "name": "Clock-in's Shot Manager",
    "author": "Andi",
    "version": (1,5),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Clock-in",
    "description": "Centralized Previews for Clock-KIT",
    "category": "Interface",
}

# CENTRAL PATH
PREVIEW_ROOT = r"D:\Master\Andi\File sekolah\File Project\Preview"

class CLOCKIN_OT_CapturePreview(bpy.types.Operator):
    bl_idname = "clockin.capture_preview"
    bl_label = "Capture Preview"
    
    def execute(self, context):
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Save your blend file first!")
            return {'CANCELLED'}
        
        # 1. Get current blend name
        filename = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        
        # 2. Setup central folder for THIS specific shot
        shot_folder = os.path.join(PREVIEW_ROOT, filename)
        
        if not os.path.exists(shot_folder):
            os.makedirs(shot_folder)
            
        # 3. Create unique filename with Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(shot_folder, f"{filename}_{timestamp}.jpg")
        
        # 4. Capture Viewport
        scene = context.scene
        original_format = scene.render.image_settings.file_format
        scene.render.image_settings.file_format = 'JPEG'
        
        bpy.ops.render.opengl(write_still=True)
        bpy.data.images['Render Result'].save_render(filepath=image_path)
        
        # Restore Settings
        scene.render.image_settings.file_format = original_format
        
        self.report({'INFO'}, f"Saved to Central Preview: {filename}")
        return {'FINISHED'}

class CLOCKIN_PT_ShotManager(bpy.types.Panel):
    bl_label = "Capture Preview"
    bl_idname = "CLOCKIN_PT_shot_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Clock-in'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("clockin.capture_preview", icon='CAMERA_DATA', text="Capture Preview")
        
        if bpy.data.filepath:
            layout.label(text=f"Active: {os.path.basename(bpy.data.filepath)}")
        else:
            layout.label(text="Save file to enable", icon='ERROR')

def register():
    bpy.utils.register_class(CLOCKIN_OT_CapturePreview)
    bpy.utils.register_class(CLOCKIN_PT_ShotManager)

def unregister():
    bpy.utils.unregister_class(CLOCKIN_OT_CapturePreview)
    bpy.utils.unregister_class(CLOCKIN_PT_ShotManager)

if __name__ == "__main__":
    register()