import sys
import numpy as np
import math
from scipy.spatial.transform import Rotation as R
from PIL import Image


# map name, no extension. This is the input .lvt file
mapname = 'town'
# folder must contain all outlaws textures converted to .png or other usable format
textures_path = "D:\\oltex\\"
# location of .lvt input file
map_path = 'C:\\Program Files (x86)\\GOG Galaxy\\Games\\Outlaws\\'


class Sector:
    def __init__(self, hex, num, name, floor_y, ceiling_y, vertices, walls, faces, flags, slopeWall, slopeAngle, cslopeWall, cslopeAngle, slopeSector, cslopeSector, polygons, floorTilingX, floorTilingZ, ceilingTilingX, ceilingTilingZ, floorTilingAngle, ceilingTilingAngle, floorTexture, ceilingTexture):
        self.hex = hex
        self.num = num
        self.name = name
        self.floor_y = floor_y
        self.ceiling_y = ceiling_y
        self.vertices = vertices
        self.walls = walls
        self.faces = faces
        self.flags = flags
        self.slopeWall = slopeWall
        self.slopeAngle = slopeAngle
        self.cslopeWall = cslopeWall
        self.cslopeAngle = cslopeAngle
        self.slopeSector = slopeSector
        self.cslopeSector = cslopeSector
        self.polygons = polygons
        self.floorTilingX = floorTilingX
        self.floorTilingZ = floorTilingZ
        self.ceilingTilingX = ceilingTilingX
        self.ceilingTilingZ = ceilingTilingZ
        self.floorTilingAngle = floorTilingAngle
        self.ceilingTilingAngle = ceilingTilingAngle
        self.floorTexture = floorTexture
        self.ceilingTexture = ceilingTexture


class SectorVertex:
    def __init__(self, x, z, num, objIndex, yFloor, yCeiling):
        self.x = x
        self.z = z
        self.num = num
        self.objIndex = objIndex
        self.yFloor = yFloor
        self.yCeiling = yCeiling


class SectorWall:
    def __init__(self, num, v1, v2, id, adjoin, mirror, dadjoin, dmirror, singleAdjoinMade, doubleAdjoinMade, mid_texture, top_texture, bot_texture):
        self.num = num
        self.v1 = v1
        self.v2 = v2
        self.id = id
        self.adjoin = adjoin
        self.mirror = mirror
        self.dadjoin = dadjoin
        self.dmirror = dmirror
        self.singleAdjoinMade = singleAdjoinMade
        self.doubleAdjoinMade = doubleAdjoinMade
        self.obj_v1_floor = None
        self.obj_v2_floor = None
        self.obj_v1_ceiling = None
        self.obj_v2_ceiling = None
        self.mid_texture = mid_texture
        self.bot_texture = bot_texture
        self.top_texture = top_texture
        self.polygons = []
        self.mid_UV_X = 0
        self.mid_UV_Y = 0
        self.top_UV_X = 0
        self.top_UV_Y = 0
        self.bot_UV_X = 0
        self.bot_UV_Y = 0


class ObjVertex:
    def __init__(self, x, y, z, num):
        self.x = x
        self.y = y
        self.z = z
        self.num = num


class UvVertex:
    def __init__(self, uvX, uvZ, num):
        self.uvX = uvX
        self.uvZ = uvZ
        self.num = num


class Texture:
    def __init__(self, name, num, resX, resY):
        self.name = name
        self.num = num
        self.resX = resX
        self.resY = resY


class Polygon:
    def __init__(self, vertices, material, tvertices):
        self.vertices = vertices
        self.material = material
        self.tvertices = tvertices
        self.solid = True


def getObjIndex(sectorList, sector, vnum):
    objIndex = 1
    for s in sectorList:
        if s != sector:
            objIndex = objIndex + 2*len(s.vertices)
        else:
            for v in s.vertices:
                if v.num != vnum:
                    objIndex = objIndex + 1
                else:
                    return objIndex +1
    return objIndex

def slopePoint(point, axis, angle):
    radianAngle = angle #(angle/180.0) * np.pi
    r = R.from_rotvec(radianAngle * np.array([axis[0], axis[1], axis[2]]))
    rpoint = r.apply(point)
    rpoint = rpoint / math.cos(radianAngle)
    return rpoint


def rotatePoint(point, axis, angle):
    radianAngle = angle #(angle/180.0) * np.pi
    r = R.from_rotvec(radianAngle * np.array([axis[0], axis[1], axis[2]]))
    rpoint = r.apply(point)
    return rpoint

def normalizeVector(v_in):
    mag = math.sqrt(math.pow(v_in[0], 2) + math.pow(v_in[1], 2)  + math.pow(v_in[2], 2) )
    return [v_in[0]/mag, v_in[1]/mag, v_in[2]/mag]

def getTextureName(num, texarray):
    for t in texarray:
        if t.num == num:
            return t.name
    return "_"

def getTexture(num, texarray):
    for t in texarray:
        if t.num == num:
            return t
    return None

def getTextureByName(name, texarray):
    for t in texarray:
        if t.name == name:
            return t
    return None

def createWallPolygon(obj_v1_floor, obj_v1_ceiling, obj_v2_floor, obj_v2_ceiling, ratio, invert_Vertices, invert_TVertices, pol_texture, uvX, uvY):
    ratioY = getTextureByName(pol_texture, textures).resX / getTextureByName(pol_texture, textures).resY
    # create vertices list
    empty_vertices_list = []
    empty_vertices_list.append(obj_v1_floor)
    empty_vertices_list.append(obj_v2_floor)
    empty_vertices_list.append(obj_v2_ceiling)
    empty_vertices_list.append(obj_v1_ceiling)
    if invert_Vertices:
        empty_vertices_list.reverse()
    # create UV vertices list
    empty_tvertices_list = []
    wall_length = math.sqrt(math.pow(obj_v1_floor.x - obj_v2_floor.x, 2) + math.pow(obj_v1_floor.z - obj_v2_floor.z, 2)) * ratio + uvX * ratio
    v1_height_top = ((obj_v1_ceiling.y - obj_v1_floor.y) + uvY) * ratio * ratioY
    v2_height_bot = ((obj_v2_floor.y - obj_v1_floor.y) + uvY) * ratio * ratioY
    v2_height_top = ((obj_v2_ceiling.y - obj_v1_floor.y) + uvY) * ratio * ratioY
    empty_tvertices_list.append(UvVertex(uvX * ratio, uvY * ratio * ratioY, 0))
    empty_tvertices_list.append(UvVertex(wall_length, v2_height_bot, 0))
    empty_tvertices_list.append(UvVertex(wall_length, v2_height_top, 0))
    empty_tvertices_list.append(UvVertex(uvX * ratio, v1_height_top, 0))
    if invert_TVertices:
        empty_tvertices_list.reverse()
    empty_polygon = Polygon(empty_vertices_list, pol_texture, empty_tvertices_list)
    return empty_polygon


print("Lvt-to-3d operational")
sectors = []
textures = []


with open(map_path + mapname + '.lvt') as f:
    content = f.readlines()
    m_sector = None
    total_vertices = 1
    last_sector_vertices = 0
    wnum = 0
    texture_count = 0
    while len(content) > 0:
        l = content.pop(0)
        # record new sector
        if l.startswith('SECTOR'):
            parts = l.split()
            empty_list_vertices = []
            empty_list_walls = []
            empty_list_faces = []
            if parts[3] == "ORD:":
                parts[3] = parts[4]
            m_sector = Sector(parts[1], int(parts[3]), 'NAME', 0.0, 0.0, empty_list_vertices, empty_list_walls, empty_list_faces, 0, 0, 0, 0, 0, 0, 0, None, 0, 0, 0, 0, 0, 0, None, None)
            sectors.append(m_sector)
            wnum = 0
            total_vertices = total_vertices + last_sector_vertices
        if l.strip(' ').startswith('FLOOR Y'):
            parts = l.split()
            m_sector.floor_y = float(parts[2])
            m_sector.floorTexture = int(parts[3])
            m_sector.floorTilingX = float(parts[4])
            m_sector.floorTilingZ = float(parts[5])
            m_sector.floorTilingAngle = float(parts[6])
        if l.strip(' ').startswith('CEILING Y'):
            parts = l.split()
            m_sector.ceiling_y = float(parts[2])
            m_sector.ceilingTexture = int(parts[3])
            m_sector.ceilingTilingX = float(parts[4])
            m_sector.ceilingTilingZ = float(parts[5])
            m_sector.ceilingTilingAngle = float(parts[6])
        if l.strip(' ').startswith('WALL:'):
            parts = l.split()
            #two empty vertices
            r_v1 = None
            r_v2 = None
            for v in m_sector.vertices:
                if m_sector.vertices.index(v) == int(parts[3]):
                    r_v1 = v
                if m_sector.vertices.index(v) == int(parts[5]):
                    r_v2 = v
            m_wall = SectorWall(wnum, r_v1, r_v2, int("0x"+parts[1], 0), int(parts[23]), int(parts[25]), int(parts[27]), int(parts[29]), False, False, int(parts[7]), int(parts[11]), int(parts[15]))
            m_wall.mid_UV_X = float(parts[8])
            m_wall.mid_UV_Y = float(parts[9])
            m_wall.top_UV_X = float(parts[12])
            m_wall.top_UV_Y = float(parts[13])
            m_wall.bot_UV_X = float(parts[16])
            m_wall.bot_UV_Y = float(parts[17])
            m_sector.walls.append(m_wall)
            wnum = wnum + 1
        if l.strip(' ').startswith('X:'):
            parts = l.split()
            m_vertex = SectorVertex(float(parts[1]), -float(parts[3]), len(m_sector.vertices), total_vertices, m_sector.floor_y, m_sector.ceiling_y)
            m_sector.vertices.append(m_vertex)
            total_vertices = total_vertices + 1
            last_sector_vertices = len(m_sector.vertices)
        if l.strip(' ').startswith('FLAGS'):
            parts = l.split()
            m_sector.flags = int(parts[1])
        if l.strip(' ').startswith('SLOPEDFLOOR'):
            parts = l.split()
            m_sector.slopeSector = int(parts[1])
            m_sector.slopeWall = int(parts[2])
            m_sector.slopeAngle = float(parts[3])
        if l.strip(' ').startswith('SLOPEDCEILING'):
            parts = l.split()
            m_sector.cslopeSector = int(parts[1])
            m_sector.cslopeWall = int(parts[2])
            m_sector.cslopeAngle = float(parts[3])
        if l.strip(' ').startswith('TEXTURE:'):
            parts = l.split()
            wid = 1
            hgt = 1
            # loading the image
            name_no_extension = parts[1].lower().split('.')
            if name_no_extension[1].lower() == 'pcx':
                try:
                    img = Image.open(textures_path + name_no_extension[0].upper() + ".png")
                    # fetching the dimensions
                    wid, hgt = img.size
                    print("VALID texture found:" + parts[1])
                except:
                    print("custom texture found:" + parts[1])
                # displaying the dimensions
                print(str(wid) + "x" + str(hgt))
            new_texture = Texture(parts[1].lower(), texture_count, wid, hgt)
            textures.append(new_texture)
            texture_count = texture_count + 1


#print sectors out
for s in sectors:
    print("\nSector number: " + str(s.num) + "   hex:" + s.hex)
    for v in s.vertices:
        print("V: " + str(v.num) + "    X: "+str(v.x) + "   Z: " + str(v.z))
    print("\n")
    for w in s.walls:
        print("W: " + str(w.num) + "   " + hex(w.id) + "    V1: " + str(w.v1.num) + "   V2: " + str(w.v2.num) + "   ADJOIN:" + str(w.adjoin) + "   MIRROR:" + str(w.mirror))
    print("flags: " + str(s.flags))


#apply slopes
for s in sectors:
    # floor slope
    rotateAxis = [0, 0, 0]
    isSloped = False
    slopeSectorId = None
    slopeWallId = None
    # check sector flags to know if floor slope is present
    if s.flags & 0x40000000 == 0x40000000:
        # find slope sector
        for ss in sectors:
            if ss.num == s.slopeSector:
                slopeSectorId = ss
        # isSloped = True
        if slopeSectorId != None:
            for w in slopeSectorId.walls:
                # find wall that has slope
                if w.num == s.slopeWall:
                    isSloped = True
                    slopeWallId = w
                    rotateAxis = [w.v2.x - w.v1.x, 0, w.v2.z - w.v1.z]
                    rotateAxis = normalizeVector(rotateAxis)
                    # print("rotateAxis:" + str(rotateAxis))
    # slope floor vertices
    for v in s.vertices:
        postSlopeCoords = [v.x, v.yFloor, v.z]
        if isSloped:
            # find vector that goes from slope wall (vertex 1) to vertex we're rotating
            wallToVertexVector = [v.x - slopeWallId.v1.x, v.yFloor - slopeWallId.v1.yFloor, v.z - slopeWallId.v1.z]
            # project wallToVertexVector on wall segment
            projDot = np.dot(rotateAxis, wallToVertexVector)
            projectedVertex = [rotateAxis[0] * projDot, rotateAxis[1] * projDot, rotateAxis[2] * projDot]
            # rotation axis-to-vertex vector (perpendicular to axis)
            perpVertexVector = [wallToVertexVector[0] - projectedVertex[0], wallToVertexVector[1] - projectedVertex[1],
                                wallToVertexVector[2] - projectedVertex[2]]
            # rotate vector around slope wall axis
            postSlopeCoords = slopePoint([perpVertexVector[0], perpVertexVector[1], perpVertexVector[2]],
                                          rotateAxis, -(np.pi * s.slopeAngle / 8192))
            # add back the slope wall coords
            postSlopeCoords = [v.x,
                               postSlopeCoords[1] + projectedVertex[1] + slopeWallId.v1.yFloor,
                               v.z]
        v.yFloor = postSlopeCoords[1]

    # ceiling slope
    rotateAxis = [0, 0, 0]
    isSloped = False
    slopeWallId = None
    # check sector flags to know if floor slope is present
    if s.flags & 0x80000000 == 0x80000000:
        # find slope sector
        for ss in sectors:
            if ss.num == s.cslopeSector:
                slopeSectorId = ss
        # isSloped = True
        if slopeSectorId != None:
            for w in slopeSectorId.walls:
                # find wall that has slope
                if w.num == s.cslopeWall:
                    isSloped = True
                    #print("CEILING SLOPE being applied to sector:" + str(s.num) + "    wall:" + str(w.num))
                    slopeWallId = w
                    rotateAxis = [w.v2.x - w.v1.x, 0, w.v2.z - w.v1.z]
                    rotateAxis = normalizeVector(rotateAxis)
    # slope ceiling vertices
    for v in s.vertices:
        postSlopeCoords = [v.x, v.yCeiling, v.z]
        if isSloped:
            # find vector that goes from slope wall (vertex 1) to vertex we're rotating
            wallToVertexVector = [v.x - slopeWallId.v1.x, v.yCeiling - slopeWallId.v1.yCeiling, v.z - slopeWallId.v1.z]
            # project wallToVertexVector on wall segment
            projDot = np.dot(rotateAxis, wallToVertexVector)
            projectedVertex = [rotateAxis[0] * projDot, rotateAxis[1] * projDot, rotateAxis[2] * projDot]
            # rotation axis-to-vertex vector (perpendicular to axis)
            perpVertexVector = [wallToVertexVector[0] - projectedVertex[0],
                                wallToVertexVector[1] - projectedVertex[1],
                                wallToVertexVector[2] - projectedVertex[2]]
            # rotate vector around slope wall axis
            postSlopeCoords = slopePoint([perpVertexVector[0], perpVertexVector[1], perpVertexVector[2]],
                                          rotateAxis, -(np.pi * s.cslopeAngle / 8192))
            # add back the slope wall coords
            postSlopeCoords = [v.x,
                               postSlopeCoords[1] + projectedVertex[1] + slopeWallId.v1.yCeiling,
                               v.z]
        v.yCeiling = postSlopeCoords[1]

#convert floors and ceiling to polygons
for s in sectors:
    firstVertex = None
    empty_polygon_list = []
    s.polygons = empty_polygon_list
    #print("Polygons for sector:" + s.hex)
    empty_vertices_list = []
    empty_tvertices_list = []
    empty_polygon = Polygon(empty_vertices_list, None, empty_tvertices_list)
    #record floor as polygon(s)
    ratio = 8.0 / getTexture(s.floorTexture, textures).resX
    prev_wall = None
    for w in s.walls:
        if firstVertex is None:
            firstVertex = w.v1
        #create UV vertex and rotate it
        uv_v = UvVertex(0, 0, 0)
        uv_v.uvX = (w.v1.x - s.floorTilingX) * ratio * -1.0
        uv_v.uvZ = (w.v1.z + s.floorTilingZ) * ratio * -1.0
        uv_angle = -(s.floorTilingAngle / 360) * 2 * math.pi
        post_rot = rotatePoint([uv_v.uvX, 0, uv_v.uvZ], [0, 1, 0], uv_angle)
        uv_v.uvX = post_rot[0]
        uv_v.uvZ = post_rot[2]
        if abs(uv_v.uvX) > 10000.0:
            print("uv_v.uvX " + str(uv_v.uvX) + "     s.floorTilingAngle "+str(s.floorTilingAngle))
        #create 3d vertex
        obj_v = ObjVertex(w.v1.x, w.v1.yFloor, w.v1.z, 0)
        #record vertices in wall data
        w.obj_v1_floor = obj_v
        if not prev_wall is None:
            prev_wall.obj_v2_floor = obj_v
        prev_wall = w
        #add vertex to polygon
        empty_polygon.vertices.append(obj_v)
        empty_polygon.tvertices.append(uv_v)
        if w.v2 == firstVertex:
            w.obj_v2_floor = empty_polygon.vertices[0]
            empty_polygon.material = getTextureName(s.floorTexture, textures)
            s.polygons.append(empty_polygon)
            firstVertex = None
            #reset polygon to empty
            empty_vertices_list = []
            empty_tvertices_list = []
            empty_polygon = Polygon(empty_vertices_list, None, empty_tvertices_list)
            prev_wall = None
    # record ceiling as polygon(s)
    ratio = 8.0 / getTexture(s.ceilingTexture, textures).resX
    prev_wall = None
    for w in s.walls:
        if firstVertex is None:
            firstVertex = w.v1
        # create UV vertex and rotate it
        uv_v = UvVertex(0, 0, 0)
        uv_v.uvX = (w.v1.x + s.ceilingTilingX) * ratio * -1.0
        uv_v.uvZ = (w.v1.z + s.ceilingTilingZ) * ratio * -1.0
        uv_angle = -(s.ceilingTilingAngle / 360) * 2 * math.pi
        post_rot = rotatePoint([uv_v.uvX, 0, uv_v.uvZ], [0, 1, 0], uv_angle)
        uv_v.uvX = post_rot[0]
        uv_v.uvZ = post_rot[2]
        # create 3d vertex
        obj_v = ObjVertex(w.v1.x, w.v1.yCeiling, w.v1.z, 0)
        # record vertices in wall data
        w.obj_v1_ceiling = obj_v
        if not prev_wall is None:
            prev_wall.obj_v2_ceiling = obj_v
        prev_wall = w
        # add vertex to polygon
        empty_polygon.vertices.append(obj_v)
        empty_polygon.tvertices.append(uv_v)
        if w.v2 == firstVertex:
            w.obj_v2_ceiling = empty_polygon.vertices[0]
            empty_polygon.vertices.reverse()
            empty_polygon.tvertices.reverse()

            empty_polygon.material = getTextureName(s.ceilingTexture, textures)
            if s.flags & 0x01 == 1:
                empty_polygon.solid = False
            s.polygons.append(empty_polygon)
            firstVertex = None
            # reset polygon to empty
            empty_vertices_list = []
            empty_tvertices_list = []
            empty_polygon = Polygon(empty_vertices_list, None, empty_tvertices_list)
            prev_wall = None


#RECORD WALLS AS POLYGONS
for s in sectors:
    for w in s.walls:
        if w.adjoin == -1:
            ratio = 8.0 / getTexture(w.mid_texture, textures).resX
            ratioY = getTexture(w.mid_texture, textures).resX / getTexture(w.mid_texture, textures).resY
            # create vertices list
            empty_vertices_list = []
            empty_vertices_list.append(w.obj_v1_floor)
            empty_vertices_list.append(w.obj_v2_floor)
            empty_vertices_list.append(w.obj_v2_ceiling)
            empty_vertices_list.append(w.obj_v1_ceiling)
            # create UV vertices list
            empty_tvertices_list = []
            wall_length = (math.sqrt(math.pow(w.v1.x - w.v2.x, 2) + math.pow(w.v1.z - w.v2.z, 2)) + w.mid_UV_X) * ratio
            v1_height_top = (w.v1.yCeiling - w.v1.yFloor + w.mid_UV_Y) * ratio * ratioY
            v2_height_bot = (w.v2.yFloor - w.v1.yFloor + w.mid_UV_Y) * ratio * ratioY
            v2_height_top = (w.v2.yCeiling - w.v1.yFloor + w.mid_UV_Y) * ratio * ratioY
            empty_tvertices_list.append(UvVertex(w.mid_UV_X * ratio, w.mid_UV_Y * ratio * ratioY, 0))
            empty_tvertices_list.append(UvVertex(wall_length, v2_height_bot, 0))
            empty_tvertices_list.append(UvVertex(wall_length, v2_height_top, 0))
            empty_tvertices_list.append(UvVertex(w.mid_UV_X * ratio, v1_height_top, 0))
            empty_polygon = Polygon(empty_vertices_list, getTextureName(w.mid_texture, textures), empty_tvertices_list)
            w.polygons.append(empty_polygon)
        # record top and bottom adjoin walls for double ajoin
        topwall = None
        lowerwall = None
        topwallSector = None
        lowerwallSector = None
        # if wall is adjoined
        if w.adjoin > -1:
            for searchSector in sectors:
                if searchSector.num == w.adjoin:
                    # search other sectors
                    for searchWall in searchSector.walls:
                        # single adjoin, we do this on the spot
                        if w.dadjoin == -1:
                            if searchWall.num == w.mirror:
                                if not (searchWall.singleAdjoinMade and searchWall.mirror == w.num) and searchWall.dadjoin == -1:
                                    # POLYGON CONNECTING FLOORS
                                    if s.floor_y > searchSector.floor_y:
                                        use_texture = getTextureName(searchWall.bot_texture, textures)
                                        use_uvx = searchWall.bot_UV_X
                                        use_uvy = searchWall.bot_UV_Y
                                        wall_B = w
                                        wall_A = searchWall
                                    else:
                                        use_texture = getTextureName(w.bot_texture, textures)
                                        use_uvx = w.bot_UV_X
                                        use_uvy = w.bot_UV_Y
                                        wall_B = searchWall
                                        wall_A = w
                                    ratio = 8.0 / getTexture(wall_A.bot_texture, textures).resX
                                    ratioY = getTexture(wall_A.mid_texture, textures).resX / getTexture(wall_A.mid_texture,textures).resY
                                    try:
                                        w.polygons.append(createWallPolygon(wall_A.obj_v1_floor, wall_B.obj_v2_floor, wall_A.obj_v2_floor, wall_B.obj_v1_floor, ratio, False, False, use_texture, use_uvx, use_uvy))
                                    except:
                                        print("FAILED TO CREATE WALL POLYGON")
                                    #  POLYGON CONNECTING CEILINGS
                                    if s.flags & 0x01 != 1 or searchSector.flags & 0x01 != 1:
                                        if s.ceiling_y < searchSector.ceiling_y:
                                            use_texture = getTextureName(searchWall.top_texture, textures)
                                            use_uvx = searchWall.top_UV_X
                                            use_uvy = searchWall.top_UV_Y
                                            wall_B = w
                                            wall_A = searchWall
                                        else:
                                            use_texture = getTextureName(w.top_texture, textures)
                                            use_uvx = w.top_UV_X
                                            use_uvy = w.top_UV_Y
                                            wall_B = searchWall
                                            wall_A = w
                                        ratio = 8.0 / getTexture(wall_A.top_texture, textures).resX
                                        ratioY = getTexture(wall_A.top_texture, textures).resX / getTexture(wall_A.top_texture,textures).resY
                                        try:
                                            w.polygons.append(createWallPolygon(wall_B.obj_v2_ceiling, wall_A.obj_v1_ceiling, wall_B.obj_v1_ceiling, wall_A.obj_v2_ceiling, ratio, False, False, use_texture, use_uvx, use_uvy))
                                        except:
                                            print("FAILED TO CREATE WALL POLYGON")
                                    w.singleAdjoinMade = True
                        # double adjoin
                        else:
                            if searchWall.num == w.mirror:
                                topwall = searchWall
                                topwallSector = searchSector

                if searchSector.num == w.dadjoin:
                    # search other sectors
                    for searchWall in searchSector.walls:
                        # single adjoin, we do this on the spot
                        if searchWall.num == w.dmirror:  # and not searchWall.singleAdjoinMade:
                            lowerwall = searchWall
                            lowerwallSector = searchSector
                            # print("***DOUBLE AJOIN: LOWER WALL FOUND")

            # double adjoin
            if w.dadjoin != -1:
                # after searching in all sectors, we now have the two walls to adjoin to (topwall and lowerwall)
                if topwallSector == None:
                    print("topwallSector ID MISSING s:" + s.hex + "   w:" + str(w.num) + "   dadjoin:" + str(w.dadjoin) + "    dmirror:" + str(w.dmirror))
                if lowerwallSector == None:
                    print("lowerwallSector ID MISSING ")
                # polygon connecting floor of single adjoined wall (top one) to ceiling of double adjoined wall (lower one)
                use_texture = getTextureName(w.mid_texture, textures)
                use_uvx = w.mid_UV_X
                use_uvy = w.mid_UV_Y
                ratio = 8.0 / getTexture(w.mid_texture, textures).resX
                ratioY = getTexture(w.mid_texture, textures).resX / getTexture(w.mid_texture, textures).resY
                try:
                    w.polygons.append(createWallPolygon(lowerwall.obj_v2_ceiling, topwall.obj_v2_floor, lowerwall.obj_v1_ceiling,
                                                        topwall.obj_v1_floor, ratio, False, False, use_texture, use_uvx,
                                                        use_uvy))
                except:
                    print("FAILED TO CREATE WALL POLYGON")
                # polygon connecting ceilings of this wall and its single adjoined wall (the top one)
                if s.flags & 0x01 != 1 or topwallSector.flags & 0x01 != 1:
                    if s.ceiling_y < topwallSector.ceiling_y:
                        use_texture = getTextureName(topwall.top_texture, textures)
                        use_uvx = topwall.top_UV_X
                        use_uvy = topwall.top_UV_Y
                        wall_B = w
                        wall_A = topwall
                    else:
                        use_texture = getTextureName(w.top_texture, textures)
                        use_uvx = w.top_UV_X
                        use_uvy = w.top_UV_Y
                        wall_B = topwall
                        wall_A = w
                    ratio = 8.0 / getTexture(wall_A.top_texture, textures).resX
                    ratioY = getTexture(wall_A.top_texture, textures).resX / getTexture(wall_A.top_texture,textures).resY
                    try:
                        w.polygons.append(
                            createWallPolygon(wall_B.obj_v2_ceiling, wall_A.obj_v1_ceiling, wall_B.obj_v1_ceiling,
                                              wall_A.obj_v2_ceiling, ratio, False, False, use_texture, use_uvx,
                                              use_uvy))
                    except:
                        print("FAILED TO CREATE WALL POLYGON")
                # polygon connecting floor of this sector to floor of of double adjoined wall (lower one)
                if s.floor_y > lowerwallSector.floor_y:
                    use_texture = getTextureName(lowerwall.bot_texture, textures)
                    use_uvx = lowerwall.bot_UV_X
                    use_uvy = lowerwall.bot_UV_Y
                    wall_B = w
                    wall_A = lowerwall
                else:
                    use_texture = getTextureName(w.bot_texture, textures)
                    use_uvx = w.bot_UV_X
                    use_uvy = w.bot_UV_Y
                    wall_B = lowerwall
                    wall_A = w
                ratio = 8.0 / getTexture(wall_A.bot_texture, textures).resX
                ratioY = getTexture(wall_A.bot_texture, textures).resX / getTexture(wall_A.bot_texture, textures).resY
                try:
                    w.polygons.append(
                        createWallPolygon(wall_A.obj_v1_floor, wall_B.obj_v2_floor, wall_A.obj_v2_floor,
                                          wall_B.obj_v1_floor, ratio, False, False, use_texture, use_uvx,
                                          use_uvy))
                except:
                    print("FAILED TO CREATE WALL POLYGON")
                # w.singleAdjoinMade = True
                w.doubleAdjoinMade = True


#NUMBER ALL OBJ VERTICES for face reference
obj_num_counter = 1
for s in sectors:
    for p in s.polygons:
        for v in p.vertices:
            v.num = obj_num_counter
            obj_num_counter = obj_num_counter + 1

#NUMBER ALL UV VERTICES for face reference
uv_num_counter = 1
for s in sectors:
    for p in s.polygons:
        for tv in p.tvertices:
            tv.num = uv_num_counter
            uv_num_counter = uv_num_counter + 1
    for w in s.walls:
        for p in w.polygons:
            for vtp in p.tvertices:
                vtp.num = uv_num_counter
                uv_num_counter = uv_num_counter + 1


# write to file
with open(map_path + mapname + '.obj', 'w') as f:

    previous_sector_vertices = 0

    # OUTPUT VERTICES
    for s in sectors:

        # output sector as object
        s_line = "o Sector_" + str(s.hex)
        f.write("%s\n" % s_line)

        #output vertices
        for pr in s.polygons:
            for v in pr.vertices:
                v_line = "v " + str(v.x) + " " + str(v.y) + " " + str(v.z)
                f.write("%s\n" % v_line)
        #output uv coords
        for pr in s.polygons:
            for tv in pr.tvertices:
                vt_line = "vt " + '{0:.6f}'.format(tv.uvX) + " " + '{0:.6f}'.format(tv.uvZ)
                f.write("%s\n" % vt_line)
        for w in s.walls:
            for p in w.polygons:
                for vtp in p.tvertices:
                    vt_line = "vt " + '{0:.6f}'.format(vtp.uvX) + " " + '{0:.6f}'.format(vtp.uvZ)
                    f.write("%s\n" % vt_line)
        #output polygons
        for pr in s.polygons:
            if pr.solid:
                mat_line = "usemtl " + pr.material.strip('.pcx')
                f.write("%s\n" % mat_line)
                floor_line = "f "
                flippedVertices = pr.vertices
                flippedVertices.reverse()
                flippedTVertices = pr.tvertices
                for v in flippedVertices:
                    floor_line = floor_line + str(v.num) + '/' + str(flippedTVertices.pop().num) + ' '
                f.write("%s\n" % floor_line)
        for w in s.walls:
            for p in w.polygons:
                mat_line = "usemtl " + p.material.strip('.pcx')
                f.write("%s\n" % mat_line)
                wall_line = "f "
                flippedVertices = p.vertices
                flippedTVertices = p.tvertices
                flippedTVertices.reverse()
                for vp in flippedVertices:
                    try:
                        wall_line = wall_line + str(vp.num) + '/' + str(flippedTVertices.pop().num) + ' '
                    except:
                        print("FAILED TO WRITE WALL POLYGON")
                f.write("%s\n" % wall_line)



# write materials file
with open(map_path + mapname + '.mtl', 'w') as f:
    for t in textures:
        if t.name.endswith('.pcx'):
            mtl_line = "newmtl " + t.name.strip('.pcx')
        else:
            mtl_line = "newmtl " + t.name
        f.write("%s\n" % mtl_line)
        mtl_line = "Ns 94.117647\nKa 1.000000 1.000000 1.000000\nKd 1.000000 1.000000 1.000000\nKs 0.000000 0.000000 0.000000\nKe 0.000000 0.000000 0.000000\nNi 1.000000\nd 1.000000\nillum 2"
        f.write("%s\n" % mtl_line)
        if t.name.endswith('.pcx'):
            size = len(t.name)

            mtl_line = "map_Kd " + textures_path + t.name[:len(t.name) - 4] + ".png" + "\n"
            f.write("%s\n" % mtl_line)
        else:
            f.write("%s\n" % "\n")


for s in sectors:
    if s.hex == '9CB13421':
        print("offset x:" + str(s.floorTilingX) + "    offset y:" + str(s.floorTilingZ))