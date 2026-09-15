# Interdigital Filter Workbench for FreeCAD

## Install
Copy the `InterdigitalFilter` folder into your FreeCAD `Mod` directory.

Typical locations:
- Windows: `%APPDATA%/FreeCAD/Mod/`
- Linux: `~/.local/share/FreeCAD/Mod/`
- macOS: `~/Library/Application Support/FreeCAD/Mod/`

Restart FreeCAD. Select **Interdigital Filter** from the workbench selector.

## Use
Choose **Interdigital Filter -> New Interdigital Filter**.

The dialog is split into RF and 3D-print/mechanical parameters. The default center frequency is 869 MHz.

The generated document contains one parametric FreeCAD feature with:
- RF input parameters
- calculated dimensions
- housing shape
- lid shape
- resonator shapes

You can edit the properties and recompute before exporting STEP.

## Important
The RF calculator follows the Changpuak/Hinshaw/Monemzadeh calculation method. The enclosure is a mechanical interpretation for a 3D-printed cavity. A plastic enclosure is not itself an RF ground plane; conductive lining/coating or a metal RF cavity is required for the calculated filter to behave as intended.
