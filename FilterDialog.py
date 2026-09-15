from PySide import QtCore, QtGui
import FreeCAD as App
import FreeCADGui as Gui
import Part
from .FilterCalculator import calculate
from .InterdigitalFilter import FilterFeature, make_shape

class FilterDialog(QtGui.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interdigital Filter Designer")
        self.setMinimumWidth(480)
        lay=QtGui.QVBoxLayout(self)
        tabs=QtGui.QTabWidget(); lay.addWidget(tabs)

        rf=QtGui.QWidget(); form=QtGui.QFormLayout(rf)
        self.fc=self.spin(869,1,10000,1); self.bw=self.spin(10,.001,5000,.1)
        self.n=self.intspin(3,2,20,1); self.ripple=self.spin(0,0,20,.1); self.z0=self.spin(50,1,1000,1)
        for label,w in [("Center frequency (MHz)",self.fc),("Bandwidth (MHz)",self.bw),
                        ("Number of resonators",self.n),("Ripple (dB)",self.ripple),("Impedance (Ω)",self.z0)]:
            form.addRow(label,w)
        tabs.addTab(rf,"RF Design")

        mech=QtGui.QWidget(); mf=QtGui.QFormLayout(mech)
        self.depth=self.lenspin(30); self.rod=self.lenspin(8); self.end=self.lenspin(15)
        self.wall=self.lenspin(3); self.bottom=self.lenspin(3); self.lid=self.lenspin(3)
        self.overlap=self.lenspin(5); self.screw=self.lenspin(3.4)
        for label,w in [("Cavity depth (mm)",self.depth),("Rod diameter (mm)",self.rod),
                        ("End clearance (mm)",self.end),("Wall thickness (mm)",self.wall),
                        ("Bottom thickness (mm)",self.bottom),("Lid thickness (mm)",self.lid),
                        ("Lid overlap (mm)",self.overlap),("Screw clearance (mm)",self.screw)]:
            mf.addRow(label,w)
        tabs.addTab(mech,"3D Print / Mechanical")

        self.results=QtGui.QPlainTextEdit(); self.results.setReadOnly(True); lay.addWidget(self.results)
        buttons=QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.create); buttons.rejected.connect(self.reject); lay.addWidget(buttons)
        for w in [self.fc,self.bw,self.n,self.ripple,self.z0,self.depth,self.rod,self.end]:
            w.valueChanged.connect(self.update)
        self.update()

    def spin(self,v,mi,ma,step):
        w=QtGui.QDoubleSpinBox(); w.setRange(mi,ma); w.setDecimals(4); w.setSingleStep(step); w.setValue(v); return w
    def intspin(self,v,mi,ma,step):
        w=QtGui.QSpinBox(); w.setRange(mi,ma); w.setValue(v); return w
    def lenspin(self,v): return self.spin(v,.1,1000,.1)

    def update(self):
        try:
            d=calculate(self.fc.value(),self.bw.value(),self.n.value(),self.ripple.value(),self.z0.value(),
                        self.depth.value(),self.rod.value(),self.end.value())
            s=(f"Quarter wavelength: {d['quarter_wave_mm']:.3f} mm\n"
               f"Interior rod length: {d['inner_rod_length_mm']:.3f} mm\n"
               f"End rod length: {d['end_rod_length_mm']:.3f} mm\n"
               f"Tap position: {d['tap_mm']:.3f} mm\n"
               f"Resonator spacing: {', '.join(f'{x:.3f}' for x in d['spacings_mm'])} mm\n"
               f"RF cavity: {d['box_length_mm']:.3f} × {d['box_height_mm']:.3f} × {d['box_depth_mm']:.3f} mm")
            self.results.setPlainText(s)
        except Exception as e: self.results.setPlainText("Calculation error:\n"+str(e))

    def create(self):
        try:
            d=calculate(self.fc.value(),self.bw.value(),self.n.value(),self.ripple.value(),self.z0.value(),
                        self.depth.value(),self.rod.value(),self.end.value())
        except Exception as e:
            QtGui.QMessageBox.critical(self,"Invalid design",str(e)); return
        doc=App.newDocument("InterdigitalFilter")
        obj=doc.addObject("PartDesign::Feature","InterdigitalFilter")
        obj.Label=f"Interdigital Filter {self.fc.value():g} MHz"
        FilterFeature(obj)
        # Assign parameters after proxy initialization.
        for name,w in [("CenterFrequencyMHz",self.fc),("BandwidthMHz",self.bw),("Resonators",self.n),
                       ("RippleDB",self.ripple),("ImpedanceOhm",self.z0),("CavityDepth",self.depth),
                       ("RodDiameter",self.rod),("EndClearance",self.end),("WallThickness",self.wall),
                       ("BottomThickness",self.bottom),("LidThickness",self.lid),("LidOverlap",self.overlap),
                       ("ScrewClearance",self.screw)]:
            setattr(obj,name,w.value())
        obj.execute()
        doc.recompute()
        Gui.activeDocument().activeView().viewAxonometric()
        Gui.activeDocument().activeView().fitAll()
        self.accept()
