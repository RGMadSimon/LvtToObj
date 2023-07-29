# LvtToObj
This python script converts .lvt files (Lucasarts Outlaws maps) into .obj files (modern 3d mesh file)

input: mapname.lvt # Outlaws map, must be extracted from the .lab container file (use conman.exe from LawMaker suite)

output: mapname.obj # obj mesh of the map (3d model)
        mapname.mtl # materials file (tells the 3d software or game engine which textures to use)
                    # textures paths are absolute, might have to modify that with a text editor
                    
also needed: The necessary textures (already converted into .png) must be extracted somewhere (see oltex.rar). 

The following variables:
  >mapname
  >map_path
  >textures_path
must be changed so the script can find your map and textures.

The resulting .obj file can be viewed with any 3d software, for example Blender (freeware) and can be imported into any game engine (Unity, Unreal, Godot, etc)

*****
Version 0.5 - There are artifacts / texture errors that need some 3d software to be fixed.
              Also, doors / moving sectors are one solid piece with the rest of the map (for now)
