import FreeCAD as App
import FreeCADGui as Gui
import Part
from .FilterCalculator import calculate

COMMAND = "InterdigitalFilter_New"

def make_shape(obj):
    p=obj.PropertiesList
    d=calculate(obj.CenterFrequencyMHz,obj.BandwidthMHz,obj.Resonators,
                 obj.RippleDB,obj.ImpedanceOhm,obj.CavityDepth,
                 obj.RodDiameter,obj.EndClearance)
    obj.CalculatedQuarterWave=d["quarter_wave_mm"]
    obj.CalculatedInnerLength=d["inner_rod_length_mm"]
    obj.CalculatedEndLength=d["end_rod_length_mm"]
    obj.CalculatedTap=d["tap_mm"]
    obj.CalculatedBoxLength=d["box_length_mm"]
    obj.CalculatedBoxHeight=d["box_height_mm"]
    obj.SpacingText=", ".join("%.3f"%x for x in d["spacings_mm"])

    wall=obj.WallThickness
    bottom=obj.BottomThickness
    lid=obj.LidThickness
    screw=obj.ScrewClearance
    overlap=obj.LidOverlap

    L=d["box_length_mm"]; H=d["box_height_mm"]; D=d["box_depth_mm"]
    r=d["rod_dia_mm"]/2

    outerL=L+2*wall
    outerH=H+bottom+lid
    outerD=D+2*wall

    outer=Part.makeBox(outerL,outerH,outerD)
    cavity=Part.makeBox(L,H,D,App.Vector(wall,bottom,wall))
    housing=outer.cut(cavity)

    # Lid is a separate editable feature, positioned above the housing.
    lidshape=Part.makeBox(outerL, lid, outerD, App.Vector(0,bottom+H,0))

    # Four screw holes through lid and housing corners.
    margin=max(2*wall, 6.0)
    screwx=[margin,outerL-margin]
    screwz=[margin,outerD-margin]
    for x in screwx:
        for z in screwz:
            hole=Part.makeCylinder(screw/2,lid+1,App.Vector(x,bottom+H-.5,z),App.Vector(0,1,0))
            lidshape=lidshape.cut(hole)
            shole=Part.makeCylinder(screw/2,bottom+H+1,App.Vector(x,-.5,z),App.Vector(0,1,0))
            housing=housing.cut(shole)

    obj.HousingShape=housing
    obj.LidShape=lidshape
    obj.ResonatorShapes=Part.makeCompound([])

    rods=[]
    for i,x in enumerate(d["x_positions_mm"]):
        length=d["end_rod_length_mm"] if i in (0,obj.Resonators-1) else d["inner_rod_length_mm"]
        if i%2==0:
            rod=Part.makeCylinder(r,length,App.Vector(wall+x,bottom,wall+D/2),App.Vector(0,1,0))
        else:
            rod=Part.makeCylinder(r,length,App.Vector(wall+x,bottom+H,wall+D/2),App.Vector(0,-1,0))
        rods.append(rod)
    obj.ResonatorShapes=Part.makeCompound(rods)

class FilterFeature:
    def __init__(self,obj):
        self.TypeId="InterdigitalFilter::Filter"
        obj.addProperty("App::PropertyString","DesignSection","Design").DesignSection="RF design"
        obj.addProperty("App::PropertyLength","CenterFrequencyMHz","Design"); obj.CenterFrequencyMHz=869
        obj.setEditorMode("CenterFrequencyMHz",0)
        obj.addProperty("App::PropertyFloat","BandwidthMHz","Design"); obj.BandwidthMHz=10
        obj.addProperty("App::PropertyInteger","Resonators","Design"); obj.Resonators=3
        obj.addProperty("App::PropertyFloat","RippleDB","Design"); obj.RippleDB=0
        obj.addProperty("App::PropertyFloat","ImpedanceOhm","Design"); obj.ImpedanceOhm=50
        obj.addProperty("App::PropertyString","MechanicalSection","Design").MechanicalSection="3D printed enclosure"
        for name,val in [("CavityDepth",30),("RodDiameter",8),("EndClearance",15),
                         ("WallThickness",3),("BottomThickness",3),("LidThickness",3),
                         ("LidOverlap",5),("ScrewClearance",3.4)]:
            obj.addProperty("App::PropertyLength",name,"Mechanical"); setattr(obj,name,val)
        obj.addProperty("App::PropertyLength","CalculatedQuarterWave","Calculated"); obj.CalculatedQuarterWave=0
        obj.addProperty("App::PropertyLength","CalculatedInnerLength","Calculated"); obj.CalculatedInnerLength=0
        obj.addProperty("App::PropertyLength","CalculatedEndLength","Calculated"); obj.CalculatedEndLength=0
        obj.addProperty("App::PropertyLength","CalculatedTap","Calculated"); obj.CalculatedTap=0
        obj.addProperty("App::PropertyLength","CalculatedBoxLength","Calculated"); obj.CalculatedBoxLength=0
        obj.addProperty("App::PropertyLength","CalculatedBoxHeight","Calculated"); obj.CalculatedBoxHeight=0
        obj.addProperty("App::PropertyString","SpacingText","Calculated")
        obj.addProperty("Part::PropertyPartShape","HousingShape","Geometry")
        obj.addProperty("Part::PropertyPartShape","LidShape","Geometry")
        obj.addProperty("Part::PropertyPartShape","ResonatorShapes","Geometry")
        make_shape(obj)
        obj.Proxy=self
    def execute(self,obj):
        make_shape(obj)

class Command:
    def GetResources(self):
        return {"MenuText":"New Interdigital Filter","ToolTip":"Create a parametric interdigital band-pass filter","Pixmap":"InterdigitalFilter.svg"}
    def Activated(self):
        Gui.Control.showDialog(FilterTaskPanel())
    def IsActive(self): return True

class FilterTaskPanel:
    def __init__(self):
        from .FilterDialog import FilterDialog
        self.dialog=FilterDialog()
        self.dialog.show()
    def accept(self):
        return True

Gui.addCommand(COMMAND,Command())
