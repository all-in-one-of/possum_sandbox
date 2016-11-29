# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import maya.cmds as cmds

import tank
from tank import Hook
from tank import TankError

class ScanSceneHook(Hook):
    """
    Hook to scan scene for items to publish
    """
    
    def execute(self, **kwargs):
        """
        Main hook entry point
        :returns:       A list of any items that were found to be published.  
                        Each item in the list should be a dictionary containing 
                        the following keys:
                        {
                            type:   String
                                    This should match a scene_item_type defined in
                                    one of the outputs in the configuration and is 
                                    used to determine the outputs that should be 
                                    published for the item
                                    
                            name:   String
                                    Name to use for the item in the UI
                            
                            description:    String
                                            Description of the item to use in the UI
                                            
                            selected:       Bool
                                            Initial selected state of item in the UI.  
                                            Items are selected by default.
                                            
                            required:       Bool
                                            Required state of item in the UI.  If True then
                                            item will not be deselectable.  Items are not
                                            required by default.
                                            
                            other_params:   Dictionary
                                            Optional dictionary that will be passed to the
                                            pre-publish and publish hooks
                        }
        """   
                
        items = []
        
        # get the main scene:
        scene_name = cmds.file(query=True, sn=True)
        if not scene_name:
            raise TankError("Please Save your file before Publishing")
        
        scene_path = os.path.abspath(scene_name)
        name = os.path.basename(scene_path)

        # create the primary item - this will match the primary output 'scene_item_type':            
        items.append({"type": "work_file", "name": name})

        # Revilo - look for cameras to publish based on MDS metadata:
        for camera in cmds.listCameras(perspective=True):
            if cmds.attributeQuery('mdsMetadata', n=camera, exists=True):

                # Evaluate shutterAngle Settings
                subFrame = cmds.getAttr(camera + ".subframe")

                if subFrame == 0:
                    shutterAngle = 0.25
                if subFrame == 1:
                    shutterAngle = 0.2
                if subFrame == 2:
                    shutterAngle = 0.125

                items.append({"type": "camera", "name": camera, "shutterAngle": shutterAngle})

        # Revilo - look for geo to publish based on MDS metadata:
        for geo in cmds.ls( transforms=True, long=True):
            #makes a list of shapes with children
            children = cmds.listRelatives(geo,type="shape")
            # if the items have children run the mds meta data check
            if children == None:
                if cmds.attributeQuery('mdsMetadata', n=geo, exists=True):
                    
                    # Tag found - Let's define a name for geo called <Asset/Shot>_<Step>
                    
                    # added line to clean out path to name
                    geopathClean = geo.split("|")[-1].strip("|")
                    
                    #then removing _group from end
                    geoName = geopathClean.split("_group")[0]
                       
                    # Evaluate shutterAngle attributes
                    subFrame = cmds.getAttr(geo + ".subframe")

                    if subFrame == 0:
                        shutterAngle = 0.25
                    if subFrame == 1:
                        shutterAngle = 0.2
                    if subFrame == 2:
                        shutterAngle = 0.125

                    # include this group as a 'mesh_group', record the selection, the name and the shutterAngle
                    items.append({"type": "mesh_group", "selection" : geo, "name": geoName, "shutterAngle": shutterAngle})




        return items
