import FreeCADGui

class InterdigitalFilterWorkbench(FreeCADGui.Workbench):
    MenuText = "Interdigital Filter"
    ToolTip = "Parametric interdigital band-pass filter designer"
    Icon = "InterdigitalFilter.svg"

    def Initialize(self):
        from . import InterdigitalFilter
        self.appendToolbar("Interdigital Filter", ["InterdigitalFilter_New"])
        self.appendMenu("Interdigital Filter", ["InterdigitalFilter_New"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(InterdigitalFilterWorkbench())
